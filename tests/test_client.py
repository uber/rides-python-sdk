# Copyright (c) 2015 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from mock import Mock
from pytest import fixture
from pytest import raises
from requests import codes

from tests.vcr_config import uber_vcr
from uber_rides.client import SurgeError
from uber_rides.client import UberRidesClient
from uber_rides.errors import ErrorDetails
from uber_rides.session import OAuth2Credential
from uber_rides.session import Session
from uber_rides.utils import auth
from uber_rides.utils import http


# replace these with valid tokens and credentials to rerecord fixtures
CLIENT_ID = 'clientID-28dh1'
CLIENT_SECRET = 'clientSecret-hv783s'
SERVER_TOKEN = 'serverToken-Y4lb2'
ACCESS_TOKEN = 'accessToken-34f21'
REFRESH_TOKEN = 'refreshToken-vsh91'
REDIRECT_URL = 'https://developer.uber.com/my-redirect_url'
SCOPES = {'profile', 'history'}

# replace these with valid identifiers to rerecord request-related fixtures
RIDE_ID = 'rideID-14f1c'
SURGE_ID = 'hsg2k38b'

EXPIRES_IN_SECONDS = 3000
START_LAT = 37.775
START_LNG = -122.417
END_LAT = 37.808
END_LNG = -122.416
PRODUCT_ID = 'd4abaae7-f4d6-4152-91cc-77523e8165a4'
PRODUCTS_AVAILABLE = 5
SURGE_HREF = 'api.uber.com/v1/surge-confirmations/{}'

EXPECTED_PRODUCT_KEYS = set([
    'capacity',
    'description',
    'price_details',
    'image',
    'display_name',
    'product_id',
])

EXPECTED_TIME_KEYS = set([
    'localized_display_name',
    'estimate',
    'display_name',
    'product_id',
])

EXPECTED_PRICE_KEYS = set([
    'high_estimate',
    'low_estimate',
    'minimum',
    'currency_code',
    'localized_display_name',
    'estimate',
    'display_name',
    'product_id',
])

EXPECTED_PROMOTION_KEYS = set([
    'display_text',
    'localized_value',
    'type',
])

EXPECTED_ACTIVITY_KEYS = set([
    'status',
    'distance',
    'start_time',
    'start_city',
    'end_time',
    'request_id',
    'product_id',
])

EXPECTED_PROFILE_KEYS = set([
    'picture',
    'first_name',
    'last_name',
    'uuid',
    'email',
    'promo_code',
])

EXPECTED_ESTIMATE_RIDE_PRICE_KEYS = set([
    'high_estimate',
    'low_estimate',
    'minimum',
    'currency_code',
    'surge_confirmation_id',
    'surge_confirmation_href',
    'surge_multiplier',
])

EXPECTED_ESTIMATE_RIDE_TRIP_KEYS = set([
    'distance_unit',
    'duration_estimate',
    'distance_estimate',
])

EXPECTED_RIDE_DETAILS_KEYS = set([
    'status',
    'request_id',
    'driver',
    'eta',
    'location',
    'vehicle',
    'surge_multiplier',
])

EXPECTED_RIDE_MAP_KEYS = set([
    'href',
    'request_id',
])

EXPECTED_INDIVIDUAL_CHARGE_KEYS = set([
    'amount',
    'type',
    'name',
])

EXPECTED_RECEIPT_KEYS = set([
    'normal_fare',
    'surge_charge',
    'total_owed',
    'total_charged',
    'subtotal',
])


@fixture
def oauth2credential():
    """Create OAuth2Credential class to hold access token information."""
    return OAuth2Credential(
        client_id=CLIENT_ID,
        redirect_url=REDIRECT_URL,
        access_token=ACCESS_TOKEN,
        expires_in_seconds=EXPIRES_IN_SECONDS,
        scopes=SCOPES,
        grant_type=auth.AUTHORIZATION_CODE_GRANT,
        client_secret=CLIENT_SECRET,
        refresh_token=REFRESH_TOKEN,
    )


@fixture
def authorized_sandbox_client(oauth2credential):
    """Create an UberRidesClient in Sandbox Mode with OAuth 2.0 Credentials."""
    session = Session(oauth2credential=oauth2credential)
    return UberRidesClient(session, sandbox_mode=True)


@fixture
def authorized_production_client(oauth2credential):
    """Create an UberRidesClient in Production with OAuth 2.0 Credentials."""
    session = Session(oauth2credential=oauth2credential)
    return UberRidesClient(session)


@fixture
def server_token_client():
    """Create an UberRidesClient with Server Token."""
    session = Session(server_token=SERVER_TOKEN)
    return UberRidesClient(session)


@fixture
def http_surge_error():
    code = 'surge'

    mock_error = Mock(
        status_code=http.STATUS_CONFLICT,
        headers=http.DEFAULT_CONTENT_HEADERS,
    )

    error_response = {
        'meta': {
            'surge_confirmation': {
                'href': SURGE_HREF.format(SURGE_ID),
                'surge_confirmation_id': SURGE_ID,
            },
        },
        'errors': [
            {
                'status': http.STATUS_CONFLICT,
                'code': code,
                'title': http.ERROR_CODE_DESCRIPTION_DICT[code],
            },
        ],
    }

    mock_error.json = Mock(return_value=error_response)
    return mock_error


@uber_vcr.use_cassette()
def test_get_products(authorized_sandbox_client, server_token_client):
    """Test to fetch products with access token and server token."""
    clients = [authorized_sandbox_client, server_token_client]

    for client in clients:
        response = client.get_products(START_LAT, START_LNG)
        assert response.status_code == codes.ok

        # assert response looks like products information
        response = response.json
        products = response.get('products')
        assert len(products) >= PRODUCTS_AVAILABLE
        assert isinstance(products, list)

        for product in products:
            assert EXPECTED_PRODUCT_KEYS.issubset(product)


@uber_vcr.use_cassette()
def test_get_single_product(authorized_sandbox_client, server_token_client):
    """Test fetch product by ID with access token and server token."""
    clients = [authorized_sandbox_client, server_token_client]

    for client in clients:
        response = client.get_product(PRODUCT_ID)
        assert response.status_code == codes.ok

        # assert response looks like single product information
        response = response.json
        assert 'products' not in response
        assert EXPECTED_PRODUCT_KEYS.issubset(response)


@uber_vcr.use_cassette()
def test_get_price_estimates(authorized_sandbox_client, server_token_client):
    """Test to fetch price estimates with access token and server token."""
    clients = [authorized_sandbox_client, server_token_client]

    for client in clients:
        response = client.get_price_estimates(
            START_LAT,
            START_LNG,
            END_LAT,
            END_LNG,
        )
        assert response.status_code == codes.ok

        # assert response looks like price estimates
        response = response.json
        prices = response.get('prices')
        assert len(prices) >= PRODUCTS_AVAILABLE
        assert isinstance(prices, list)

        for price in prices:
            assert EXPECTED_PRICE_KEYS.issubset(price)


@uber_vcr.use_cassette()
def test_get_pickup_time_estimates(
    authorized_sandbox_client,
    server_token_client,
):
    """Test to fetch time estimates with access token and server token."""
    clients = [authorized_sandbox_client, server_token_client]

    for client in clients:
        response = client.get_pickup_time_estimates(
            START_LAT,
            START_LNG,
        )
        assert response.status_code == codes.ok

        # assert response looks like pickup time estimates
        response = response.json
        times = response.get('times')
        assert len(times) >= PRODUCTS_AVAILABLE
        assert isinstance(times, list)

        for time in times:
            assert EXPECTED_TIME_KEYS.issubset(time)


@uber_vcr.use_cassette()
def test_get_promotions(authorized_sandbox_client, server_token_client):
    """Test to fetch promotions with access token and server token."""
    clients = [authorized_sandbox_client, server_token_client]

    for client in clients:
        response = client.get_promotions(
            START_LAT,
            START_LNG,
            END_LAT,
            END_LNG,
        )
        assert response.status_code == codes.ok

        # assert response looks like promotions
        response = response.json
        assert EXPECTED_PROMOTION_KEYS.issubset(response)


@uber_vcr.use_cassette()
def test_get_user_activity(authorized_sandbox_client):
    """Test to fetch user activity with access token."""
    response = authorized_sandbox_client.get_user_activity()
    assert response.status_code == codes.ok

    # assert response looks like user activity
    response = response.json
    history = response.get('history')
    assert len(history) == 5
    assert isinstance(history, list)

    for activity in history:
        assert EXPECTED_ACTIVITY_KEYS.issubset(activity)


@uber_vcr.use_cassette()
def test_get_user_profile(authorized_sandbox_client):
    """Test to fetch user profile with access token."""
    response = authorized_sandbox_client.get_user_profile()
    assert response.status_code == codes.ok

    # assert response looks like use profile
    response = response.json
    assert EXPECTED_PROFILE_KEYS.issubset(response)


@uber_vcr.use_cassette()
def test_estimate_ride(authorized_sandbox_client):
    """Test to fetch ride estimate with access token."""
    response = authorized_sandbox_client.estimate_ride(
        PRODUCT_ID,
        START_LAT,
        START_LNG,
        END_LAT,
        END_LNG,
    )
    assert response.status_code == codes.ok

    # assert response looks like price and time estimates
    response = response.json
    price = response.get('price')
    assert EXPECTED_ESTIMATE_RIDE_PRICE_KEYS.issubset(price)
    trip = response.get('trip')
    assert EXPECTED_ESTIMATE_RIDE_TRIP_KEYS.issubset(trip)


@uber_vcr.use_cassette()
def test_request_ride(authorized_sandbox_client):
    """Test to request ride with access token."""
    response = authorized_sandbox_client.request_ride(
        PRODUCT_ID,
        START_LAT,
        START_LNG,
        END_LAT,
        END_LNG,
    )
    assert response.status_code == codes.accepted

    # assert response looks like ride details
    response = response.json
    assert EXPECTED_RIDE_DETAILS_KEYS.issubset(response)


@uber_vcr.use_cassette()
def test_get_ride_details(authorized_sandbox_client):
    """Test to fetch ride details with access token."""
    response = authorized_sandbox_client.get_ride_details(RIDE_ID)
    assert response.status_code == codes.ok

    # assert response looks like ride details
    response = response.json
    assert EXPECTED_RIDE_DETAILS_KEYS.issubset(response)
    assert response.get('status') == 'processing'


@uber_vcr.use_cassette()
def test_get_ride_map(authorized_sandbox_client):
    """Test to fetch ride map with access token."""
    response = authorized_sandbox_client.get_ride_map(RIDE_ID)
    assert response.status_code == codes.ok

    # assert response looks like map
    response = response.json
    assert EXPECTED_RIDE_MAP_KEYS.issubset(response)


@uber_vcr.use_cassette()
def test_update_sandbox_ride(authorized_sandbox_client):
    """Test to update sandbox ride status with access token."""
    response = authorized_sandbox_client.update_sandbox_ride(
        ride_id=RIDE_ID,
        new_status='accepted',
    )
    assert response.status_code == codes.no_content


@uber_vcr.use_cassette()
def test_cancel_ride(authorized_sandbox_client):
    """Test to cancel ride status with access token."""
    response = authorized_sandbox_client.cancel_ride(RIDE_ID)
    assert response.status_code == codes.no_content


@uber_vcr.use_cassette()
def test_get_ride_receipt(authorized_sandbox_client):
    """Test to fetch ride receipt with access token."""
    response = authorized_sandbox_client.get_ride_receipt(RIDE_ID)
    assert response.status_code == codes.ok

    # assert response looks like ride receipt
    response = response.json
    assert EXPECTED_RECEIPT_KEYS.issubset(response)
    charges = response.get('charges')

    for charge in charges:
        assert EXPECTED_INDIVIDUAL_CHARGE_KEYS.issubset(charge)


@uber_vcr.use_cassette()
def test_update_sandbox_product(authorized_sandbox_client):
    """Test to update sandbox ride status with access token."""
    response = authorized_sandbox_client.update_sandbox_product(
        product_id=PRODUCT_ID,
        surge_multiplier=2,
    )
    assert response.status_code == codes.no_content


@uber_vcr.use_cassette()
def test_request_ride_with_surge(authorized_sandbox_client):
    """Test raising a SurgeError when requesting a ride with surge."""
    with raises(SurgeError):
        authorized_sandbox_client.request_ride(
            PRODUCT_ID,
            START_LAT,
            START_LNG,
            END_LAT,
            END_LNG,
        )


def test_surge_error_formation(http_surge_error):
    """Test HTTP surge error response converted to SurgeError correctly."""
    surge_error = SurgeError(http_surge_error, 'msg')

    assert surge_error.message == 'msg'
    assert isinstance(surge_error.errors, list)
    assert isinstance(surge_error.meta, dict)

    error_details = surge_error.errors[0]
    expected_code = 'surge'
    expected_description = http.ERROR_CODE_DESCRIPTION_DICT[expected_code]

    assert isinstance(error_details, ErrorDetails)
    assert error_details.status == http.STATUS_CONFLICT
    assert error_details.code == expected_code
    assert error_details.title == expected_description

    assert surge_error.surge_confirmation_id == SURGE_ID
    assert surge_error.surge_confirmation_href == SURGE_HREF.format(SURGE_ID)
