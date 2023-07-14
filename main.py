from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from services import services
from datetime import datetime

app = FastAPI(title="CSIT SE-MINI-CHALLENGE")


def validate_dates(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


@app.get("/", include_in_schema=False)
def redirect_to_docs():
    # Redirect the root URL ("/") to the API documentation
    return RedirectResponse("/docs")


@app.get("/flight")
def get_flights(departureDate: str, returnDate: str, destination: str):
    """
    Get a list of return flights at the cheapest price, given the destination city, departure date, and arrival date.
    """

    if not departureDate or not returnDate or not destination:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing query parameters")

    if not validate_dates(departureDate) or not validate_dates(returnDate):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect date format. Please use YYYY-MM-DD")

    ticket = services.get_cheapest_flights(destination, departureDate)
    return_ticket = services.get_cheapest_return_flights(destination, returnDate)

    print(ticket)

    if ticket is None:
        return []
    if return_ticket is None:
        return []

    print(ticket)

    flight_list = []
    flight = {}
    flight["City"] = ticket["destcity"]
    flight["Departure Date"] = ticket["date"]
    flight["Departure Airline"] = ticket["airlinename"]
    flight["Departure Price"] = ticket["price"]
    flight["Return Date"] = return_ticket["date"]
    flight["Return Airline"] = return_ticket["airlinename"]
    flight["Return Price"] = return_ticket["price"]

    flight_list.append(flight)
    return flight_list


@app.get("/hotel")
def get_hotels(checkInDate: str, checkOutDate: str, destination: str):
    """
    Get a list of hotels providing the cheapest price, given the destination city, check-in date, and check-out date.
    """
    if not checkInDate or not checkOutDate or not destination:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing query parameters")

    if not validate_dates(checkInDate) or not validate_dates(checkOutDate):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect date format. Please use YYYY-MM-DD")

    hotels = services.get_cheapest_hotel(checkInDate, checkOutDate, destination)

    if hotels is None:
        return []

    return (hotels)
