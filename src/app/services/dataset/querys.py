from app.schemas.resturantSchema import Resturant
from rapidfuzz import fuzz, process

def filter_resturants(storage, **filters):
    rows = storage.read_all()
    results = rows

    for key, value in filters.items():
        if value in (None,"",0,0,[]):
            continue
            
        if key == "name":
            
            search = str(value).lower()
            names = [row.get("name", "").lower() for row in results]

            matches = process.extract(
            search,
            names,
            scorer=fuzz.WRatio,
            score_cutoff=80
            )
            
            matched_names = {m[0] for m in matches}

            results = [row for row in results if ( search in row.get("name", "").lower() or row.get("name", "").lower() in matched_names)]

        elif key == "cuisine":
            cuisine = str(value).lower()
            results = [row for row in results if cuisine in row.get("cuisine","").lower()]
    
        elif key == "distance":
            results = [row for row in results if row.get("distance","") is not None and row.get("distance") <= value]

        elif key == "rating":
            results = [row for row in results if row.get("rating","") is not None and float(row.get("rating")) >= value]

    return [Resturant(**row) for row in results]



