
from flask import Flask, redirect, request, render_template

from example import utils  # NOQA
from example.utils import import_app_credentials

from uber_rides.auth import AuthorizationCodeGrant
from uber_rides.client import UberRidesClient

import datetime

app = Flask(__name__, template_folder="./")

credentials = import_app_credentials('config.driver.yaml')

auth_flow = AuthorizationCodeGrant(
    credentials.get('client_id'),
    credentials.get('scopes'),
    credentials.get('client_secret'),
    credentials.get('redirect_url'),
)


@app.template_filter('date')
def date(value, format='%b %d, %Y at %H:%M'):
    return datetime.datetime.fromtimestamp(value).strftime(format)


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

    # Fetch profile for driver
    profile = client.get_driver_profile().json

    # Fetch last 50 trips and payments for driver
    trips = client.get_driver_trips(0, 50).json
    payments = client.get_driver_payments(0, 50).json

    return render_template('driver_dashboard.html',
                           profile=profile,
                           trips=trips['trips'],
                           payments=payments['payments']
                           )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
