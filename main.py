from just_eat_client import JustEatClient

if __name__ == "__main__":
    client = JustEatClient()
    postcode = input("Insert your postcode to retrieve data about "
                     "all restaurants: ")

    restaurants = client.get_restaurants_by_postcode(postcode)
    client.write_to_json_file(restaurants, postcode)
