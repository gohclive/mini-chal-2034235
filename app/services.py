from pymongo import MongoClient
from datetime import datetime
import re

import pymongo


class Services:

    @staticmethod
    def connect_to_mongodb():
        try:
            # Connect to MongoDB
            client = MongoClient(
                'mongodb+srv://userReadOnly:7ZT817O8ejDfhnBM@minichallenge.q4nve1r.mongodb.net/')
            # Access a specific database
            db = client['minichallenge']
            # Return the database object
            return db
        except Exception as e:
            print(f"Error connecting to MongoDB: {str(e)}")
            return None

    def find_city(self, destination):
        db = self.connect_to_mongodb()

        if db is None:
            return None

        flights_collection = db['flights']

        city = flights_collection.find_one({'destcity': {'$regex': f'^{re.escape(destination)}$', '$options': 'i'}})
        return city if city else None

    def get_cheapest_flights(self, destination, departure_date):
        # Connect to MongoDB
        db = self.connect_to_mongodb()

        if db is None:
            return None

        try:
            # Access the flights collection
            flights_collection = db['flights']

            date_departure_object = datetime.strptime(departure_date, '%Y-%m-%d')

            query = {
                'srccountry': 'Singapore',
                'date': date_departure_object,
                'destcity': {'$regex': f'^{re.escape(destination)}$', '$options': 'i'}
            }

            # Sort by price in ascending order to get the cheapest flights first
            sort_criteria = [("price", pymongo.ASCENDING)]

            projection = {
                '_id': 0,
                'destcity': 1,
                'date': 1,
                'airlinename': 1,
                'price': 1
            }

            results = flights_collection.find(query, projection).sort(sort_criteria)

            if results.count() == 0:
                return None

            for result in results:
                result['date'] = result['date'].strftime('%Y-%m-%d')
            return result

        except Exception as e:
            print(f"Error retrieving flights from MongoDB: {str(e)}")
            return None

    def get_cheapest_return_flights(self, destination, arrival_date):
        # Connect to MongoDB
        db = self.connect_to_mongodb()

        if db is None:
            return None

        try:
            # Access the flights collection
            flights_collection = db['flights']

            date_arrival_object = datetime.strptime(arrival_date, '%Y-%m-%d')

            query = {
                'srccity': {'$regex': f'^{re.escape(destination)}$', '$options': 'i'},
                'date': date_arrival_object,
                'destcountry': "Singapore"
            }

            # Sort by price in ascending order to get the cheapest flights first
            sort_criteria = [("price", pymongo.ASCENDING)]

            projection = {
                '_id': 0,
                'date': 1,
                'airlinename': 1,
                'price': 1
            }

            results = flights_collection.find(query, projection).sort(sort_criteria)

            if results.count() == 0:
                return None

            for result in results:
                result['date'] = result['date'].strftime('%Y-%m-%d')
            return result

        except Exception as e:
            print(f"Error retrieving flights from MongoDB: {str(e)}")
            return None

    def get_cheapest_hotel(self, checkInDate, checkOutDate, destination):
        # Connect to MongoDB
        db = self.connect_to_mongodb()

        if db is None:
            return None

        try:
            # Access the flights collection
            hotels_collection = db['hotels']

            check_in_date = datetime.strptime(checkInDate, "%Y-%m-%d")
            check_out_date = datetime.strptime(checkOutDate, "%Y-%m-%d")

            # Construct the MongoDB query
            query = [
                {
                    "$match": {
                        "city": {'$regex': f'^{re.escape(destination)}$', '$options': 'i'},
                        "date": {
                            "$gte": check_in_date,
                            "$lte": check_out_date
                        }
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "city": "$city",
                            "hotel": "$hotelName"
                        },
                        "totalPrice": {"$sum": "$price"}
                    }
                },
                {
                    "$sort": {"totalPrice": 1}
                }
            ]

            # Execute the query
            result = hotels_collection.aggregate(query)

            formatted_results = []
            for hotel in result:
                formatted_result = {
                    "City": hotel["_id"]["city"],
                    "Check In Date": check_in_date.strftime("%Y-%m-%d"),
                    "Check Out Date": check_out_date.strftime("%Y-%m-%d"),
                    "Hotel": hotel["_id"]["hotel"],
                    "Price": hotel["totalPrice"]
                }
                formatted_results.append(formatted_result)

            return formatted_results

        except Exception as e:
            print(f"Error retrieving hotels from MongoDB: {str(e)}")
            return None


services = Services()

if __name__ == '__main__':
    services = Services()

    a = services.get_cheapest_flights("frankfurt", "2023-12-10")
    print(a)

    b = services.get_cheapest_return_flights("frankfurt", "2023-12-16")
    print(b)
