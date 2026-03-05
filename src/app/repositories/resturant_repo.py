import csv
from app.schemas.resturantSchema import Resturant, deliveryResturant


def load_resturants():
    try:
        with open("app/data/resturants.csv", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        return []

def save_resturants(resturants):
    with open("app/data/resturants.csv", "w", newline="") as f:
        fieldnames = Resturant.model_fields.keys()

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for r in resturants:
            if isinstance(r, Resturant):
                writer.writerow(r.model_dump())
            else:
                writer.writerow(r)


def save_foodDelivery(search_id):
    with open("app/data/food_delivery.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["restaurant_id"] == str(search_id):
                            return deliveryResturant(**row)
        return None