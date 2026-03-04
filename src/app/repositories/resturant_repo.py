import json

def load_resturants():
    try:
        with open("app/data/resturants.json", "r") as f:
            return json.load(f)
    except:
        return []


def save_resturants(resturants):
    with open("app/data/resturants.json", "w") as f:
        json.dump(resturants, f, indent=4)