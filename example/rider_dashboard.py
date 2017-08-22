
from flask import Flask, redirect, request, render_template

from example import utils  # NOQA
from example.utils import import_app_credentials

from uber_rides.auth import AuthorizationCodeGrant
from uber_rides.client import UberRidesClient

from collections import OrderedDict, Counter

app = Flask(__name__, template_folder="./")

credentials = import_app_credentials('config.rider.yaml')

auth_flow = AuthorizationCodeGrant(
    credentials.get('client_id'),
    credentials.get('scopes'),
    credentials.get('client_secret'),
    credentials.get('redirect_url'),
)


@app.route('/')
def index():
    """Index controller to redirect user to sign in with uber."""
    return redirect(auth_flow.get_authorization_url())


@app.route('/uber/connect')
def connect():
    """Connect controller to handle token exchange and query Uber API."""

    # Exchange authorization code for acceess token and create session
    session = auth_flow.get_session(request.url)
    client = UberRidesClient(session)

    # Fetch profile for rider
    profile = client.get_rider_profile().json

    # Fetch all trips from history endpoint
    trips = []
    i = 0
    while True:
        try:
            response = client.get_rider_trips(
                limit=50,
                offset=i)
            i += 50
            if len(response.json['history']) > 0:
                trips += response.json['history']
            else:
                break
        except:
            break
            pass

    # Compute trip stats for # of rides and distance
    total_rides = 0
    total_distance_traveled = 0

    # Compute ranked list of # trips per city
    cities = list()
    for ride in trips:
        cities.append(ride['start_city']['display_name'])

        # only parse actually completed trips
        if ride['distance'] > 0:
            total_rides += 1
            total_distance_traveled += int(ride['distance'])

    total_cities = 0
    locations_counter = Counter(cities)
    locations = OrderedDict()
    cities_by_frequency = sorted(cities, key=lambda x: -locations_counter[x])
    for city in list(cities_by_frequency):
        if city not in locations:
            total_cities += 1
            locations[city] = cities.count(city)

    return render_template('rider_dashboard.html',
                           profile=profile,
                           trips=trips,
                           locations=locations,
                           total_rides=total_rides,
                           total_cities=total_cities,
                           total_distance_traveled=total_distance_traveled
                           )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
