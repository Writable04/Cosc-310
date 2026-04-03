# helpful website https://developers.google.com/maps/documentation/routes/reference/rest/v2/TopLevel/computeRoutes
import googlemaps, requests, json # add this to project imports list
from app.data import routeData
from datetime import datetime, timedelta, timezone

class MapStorage(): 
    def __init__(self):
        self.apiKey = routeData.GoogleMapsAPIKey
        self.client = googlemaps.Client(self.apiKey)
        self.nowUTC = datetime.now(timezone.utc) + timedelta(minutes=1) 
        self.url = 'https://routes.googleapis.com/directions/v2:computeRoutes'

        self.headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': self.apiKey, 
        'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.legs.duration,routes.staticDuration'
        }
 
        # origin = "3333 University Way, Kelowna, BC"
        # destination = "5533 Airport Way, Kelowna, BC"
        self.payload = {
        # "origin": {
        #     "address": origin
        # }, 
        # "destination":{
        #     "address": destination
        # },
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
        #"departureTime": self.nowUTC.strftime('%Y-%m-%dT%H:%M:%SZ'), # timezone doesnt matter cuz we are calculating trip time and distance
        "computeAlternativeRoutes": False
        }   


    def calculateDeliveryTimeMins(self, origin: str, destination: str) -> int:
        payload = self.payload.copy()
        payload["origin"] = {"address": origin}
        payload["destination"] = {"address": destination}
        payload["departureTime"] = (datetime.now(timezone.utc) + timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%SZ')

        directions_result = requests.post(self.url, headers=self.headers, data=json.dumps(payload))
        data = directions_result.json()

        if directions_result.status_code == 200 and 'routes' in data:
            durStr = data['routes'][0]['duration']
            totalMinutes = int(durStr.replace('s', '')) // 60 #use replace to remove unit char from numerical value
            return totalMinutes
        else:
            #print(directions_result.json()['error']['message'])
            return(-1)

    def calculateDeliveryDistanceKM(self, origin: str, destination: str) -> float:
        payload = self.payload.copy()
        payload["origin"] = {"address": origin}
        payload["destination"] = {"address": destination}
        payload["departureTime"] = (datetime.now(timezone.utc) + timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%SZ')

        directions_result = requests.post(self.url, headers=self.headers, data=json.dumps(payload))
        data = directions_result.json()

        if directions_result.status_code == 200 and 'routes' in data:
            distance_m = data['routes'][0]['distanceMeters']
            return distance_m / 1000.0
        else:
            #print(directions_result.json()['error']['message'])
            return(-1.0)


if __name__ == "__main__":
    test = MapStorage().calculateDeliveryTimeMins(origin="1137 Alumni Ave, Kelowna, BC",
                                                  destination="2271 Harvey Ave, Kelowna, BC")
    print(test)
