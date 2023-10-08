import json
import os
import re
from datetime import datetime

import requests
from requests import Response

from exceptions import (JustEatWrongPostalCodeTypeError,
                        JustEatAPIError,
                        JustEatNoRestaurantsByPostalCodeError)


class JustEatClient:
    BASE_URL = "https://uk.api.just-eat.io/restaurants/bypostcode/"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                      "AppleWebKit/605.1.15"
                      "(KHTML, like Gecko) Version/16.2 Safari/605.1.15"
    }

    def get_restaurants_by_postcode(self, postcode: str) -> list[dict]:
        if not self._validate_postcode(postcode):
            raise JustEatWrongPostalCodeTypeError("You are using wrong postal code")

        full_url = f"{self.BASE_URL}{postcode}"
        resp = requests.get(full_url, headers=self.HEADERS)

        if self._validate_response_status_codes(resp):
            try:
                restaurants_full_data = resp.json()["Restaurants"]
            except requests.exceptions.JSONDecodeError:
                raise JustEatAPIError("Internal server error")

            if not restaurants_full_data:
                raise JustEatNoRestaurantsByPostalCodeError("There are no restaurants "
                                                            "in your region")
            restaurants = []

            for restaurant in restaurants_full_data:
                restaurant_name = restaurant["Name"]
                restaurant_rating = restaurant["Rating"]
                restaurant_cuisines = restaurant["Cuisines"]
                print(f"Name: {restaurant_name}\n"
                      f"Rating: {restaurant_rating}\n"
                      f"Cuisines: {restaurant_cuisines}")
                print("-" * 100)
                restaurants.append({
                    "Name": restaurant_name,
                    "Rating": restaurant_rating,
                    "Cuisines": restaurant_cuisines
                })

            return restaurants

    @staticmethod
    def _validate_response_status_codes(response: Response) -> bool:
        if response.status_code == "400":
            raise JustEatAPIError("Bad request")

        if response.status_code == "401":
            raise JustEatAPIError("Unauthorized")

        if response.status_code == "429":
            raise JustEatAPIError("Too many requests")

        if response.status_code == "500":
            raise JustEatAPIError("Internal server error")

        if response.status_code == "403":
            raise JustEatAPIError("Access Forbidden")

        return True

    @staticmethod
    def _validate_postcode(postcode: str):
        expr = (r"^(GIR 0AA|[A-PR-UWYZ]([0-9]{1,2}|"
                r"([A-HK-Y][0-9]([0-9ABEHMNPRV-Y])?)|"
                r"[0-9][A-HJKPS-UW])\ [0-9][ABD-HJLNP-UW-Z]{2})$")
        return bool(re.match(expr, postcode))

    @staticmethod
    def write_to_json_file(data: list[dict], postcode: str) -> None:
        postcode = postcode.replace(" ", "")
        filename = f"{postcode}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S:%f')}.json"
        dirname = "restaurants_data"
        with open(os.path.join(dirname, filename), "w") as output_file:
            json.dump(data, output_file, indent=2)
