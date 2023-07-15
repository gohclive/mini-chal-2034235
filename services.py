from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import re
import os
import pymongo


class Services:

    load_dotenv()
    DB_URL = os.environ.get('DB_URL')

    @staticmethod
    def connect_to_mongodb():
        try:
            # Connect to MongoDB
            client = MongoClient(services.DB_URL)
            # Access a specific database
            db = client['minichallenge']
            # Return the database object
            return db
        except Exception as e:
            print(f"Error connecting to MongoDB: {str(e)}")
            return None

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

            projection = {
                '_id': 0,
                'destcity': 1,
                'date': 1,
                'airlinename': 1,
                'price': 1
            }

            results = list(flights_collection.find(query, projection).sort("price", pymongo.ASCENDING).limit(1))

            if len(results) == 0:
                return None

            for result in results:
                result['date'] = result['date'].strftime('%Y-%m-%d')
            return results[0]

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

            results = list(flights_collection.find(query, projection).sort(sort_criteria).limit(1))

            if len(results) == 0:
                return None

            for result in results:
                result['date'] = result['date'].strftime('%Y-%m-%d')
            return results[0]

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
            result = list(hotels_collection.aggregate(query))
            if len(result) == 0:
                return None

            formatted_results = []
            for hotel in result:
                formatted_result = {
                    "City": destination.lower().title(),
                    "Check In Date": check_in_date.strftime("%Y-%m-%d"),
                    "Check Out Date": check_out_date.strftime("%Y-%m-%d"),
                    "Hotel": hotel["_id"]["hotel"],
                    "Price": hotel["totalPrice"]
                }
                formatted_results.append(formatted_result)
            return formatted_results[0]

        except Exception as e:
            print(f"Error retrieving hotels from MongoDB: {str(e)}")
            return None


services = Services()
