# Copyright (c) 2016 Uber Technologies, Inc.
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
CLIENT_ID = 'xxx'
CLIENT_SECRET = 'xxx'
SERVER_TOKEN = 'xxx'

ACCESS_TOKEN = 'xxx'
REFRESH_TOKEN = 'xxx'
REDIRECT_URL = 'https://uberapitester.com/api/v1/uber/oauth'

SCOPES = {
          'profile',
          'places',
          'request',
          'request_receipt',
          'all_trips',
          'history'
          }

# replace these with valid identifiers to rerecord request-related fixtures
RIDE_ID = '0aec0061-1e20-4239-a0b7-78328e9afec8'
SURGE_ID = 'hsg2k38b'

# addresses to test places
HOME_ADDRESS = '555 Market Street, SF'
FULL_HOME_ADDRESS = '555 Market St, San Francisco, CA 94105, USA'
WORK_ADDRESS = '1455 Market Street, SF'
FULL_WORK_ADDRESS = '1455 Market St, San Francisco, CA 94103, USA'

# ride details
EXPIRES_IN_SECONDS = 3000
START_LAT = 37.7899886
START_LNG = -122.4021253
END_LAT = 37.775232
END_LNG = -122.4197513
UPDATE_LAT = 37.775234
UPDATE_LNG = -122.4197515
NON_UFP_PRODUCT_ID = '3ab64887-4842-4c8e-9780-ccecd3a0391d'
UFP_PRODUCT_ID = '821415d8-3bd5-4e27-9604-194e4359a449'
UFP_FARE_ID = '7dad38f13eab3124621d16604c35fb26e3' \
              '0395e76937c507565fb1b4aa4a8264'
UFP_SHARED_PRODUCT_ID = '26546650-e557-4a7b-86e7-6a3942445247'
UFP_SHARED_SEAT_COUNT = 2
UFP_SHARED_FARE_ID = 'd30e732b8bba22c9cdc10513ee86380087cb'\
                     '4a6f89e37ad21ba2a39f3a1ba960'
PRODUCTS_AVAILABLE = 8

NO_DESTINATION_PRODUCT_ID = '2541f77c-920a-45c4-8bf3-603ecd625195'

NON_UFP_SURGE_PRODUCT_ID = 'd5ef01d9-7d54-413e-b265-425948d06e92'
NON_UFP_SURGE_START_LAT = -22.9674153
NON_UFP_SURGE_START_LNG = -43.1801978
NON_UFP_SURGE_END_LAT = -22.9883286
NON_UFP_SURGE_END_LNG = -43.1925661
SURGE_HREF = 'api.uber.com/v1.2/surge-confirmations/{}'

EXPECTED_PRODUCT_KEYS = set([
    'capacity',
    'description',
    'image',
    'display_name',
    'product_id',
    'shared',
    'short_description',
    'product_group',
    'cash_enabled',
    'upfront_fare_enabled'
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
    'currency_code',
    'localized_display_name',
    'estimate',
    'distance',
    'duration',
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

EXPECTED_ESTIMATE_RIDE_FARE_KEYS = set([
    'value',
    'fare_id',
    'expires_at',
    'currency_code',
    'display',
])

EXPECTED_ESTIMATE_RIDE_TRIP_KEYS = set([
    'distance_unit',
    'duration_estimate',
    'distance_estimate',
])

EXPECTED_ESTIMATE_SHARED_RIDE_TRIP_KEYS = set([
    'distance_unit',
    'duration_estimate',
    'distance_estimate',
])

EXPECTED_RIDE_DETAILS_KEYS = set([
    'status',
    'request_id',
    'product_id',
    'driver',
    'pickup',
    'destination',
    'location',
    'vehicle',
    'shared',
])

EXPECTED_SHARED_RIDE_DETAILS_KEYS = set([
    'status',
    'request_id',
    'product_id',
    'driver',
    'pickup',
    'destination',
    'location',
    'vehicle',
    'shared'
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
    'distance',
    'charge_adjustments',
    'total_owed',
    'total_fare',
    'total_charged',
    'distance_label',
    'request_id',
    'duration',
    'subtotal',
])

EXPECTED_PLACE_KEYS = set(['address'])

EXPECTED_PAYMENT_KEYS = set([
    'payment_method_id',
    'type',
    'description',
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
        response = client.get_product(UFP_PRODUCT_ID)
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
            UFP_SHARED_SEAT_COUNT,
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

        for pickup_time in times:
            assert EXPECTED_TIME_KEYS.issubset(pickup_time)


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
def test_estimate_shared_ride(authorized_sandbox_client):
    """Test to estimate a shared ride."""
    try:
        response = authorized_sandbox_client.estimate_ride(
            product_id=UFP_SHARED_PRODUCT_ID,
            seat_count=UFP_SHARED_SEAT_COUNT,
            start_latitude=START_LAT,
            start_longitude=START_LNG,
            end_latitude=END_LAT,
            end_longitude=END_LNG,
        )
    except Exception as e:
        print(e.errors[0].__dict__)
    assert response.status_code == codes.ok

    # assert response looks like price and time estimates
    response = response.json
    fare = response.get('fare')
    assert EXPECTED_ESTIMATE_RIDE_FARE_KEYS.issubset(fare)
    trip = response.get('trip')
    assert EXPECTED_ESTIMATE_SHARED_RIDE_TRIP_KEYS.issubset(trip)


@uber_vcr.use_cassette()
def test_estimate_ride(authorized_sandbox_client):
    """Test to fetch ride estimate with access token."""
    response = authorized_sandbox_client.estimate_ride(
        product_id=UFP_PRODUCT_ID,
        start_latitude=START_LAT,
        start_longitude=START_LNG,
        end_latitude=END_LAT,
        end_longitude=END_LNG,
    )
    assert response.status_code == codes.ok

    # assert response looks like price and time estimates
    response = response.json
    fare = response.get('fare')
    assert EXPECTED_ESTIMATE_RIDE_FARE_KEYS.issubset(fare)
    trip = response.get('trip')
    assert EXPECTED_ESTIMATE_RIDE_TRIP_KEYS.issubset(trip)


@uber_vcr.use_cassette()
def test_estimate_ride_with_places(authorized_sandbox_client):
    """Test to fetch ride estimate with place ids."""
    response = authorized_sandbox_client.estimate_ride(
        product_id=UFP_PRODUCT_ID,
        start_place_id='home',
        end_place_id='work',
    )
    assert response.status_code == codes.ok

    # assert response looks like price and time estimates
    response = response.json
    fare = response.get('fare')
    assert EXPECTED_ESTIMATE_RIDE_FARE_KEYS.issubset(fare)
    trip = response.get('trip')
    assert EXPECTED_ESTIMATE_RIDE_TRIP_KEYS.issubset(trip)


@uber_vcr.use_cassette()
def test_request_ride(authorized_sandbox_client):
    """Test to request ride with access token."""
    response = authorized_sandbox_client.request_ride(
        product_id=UFP_PRODUCT_ID,
        fare_id=UFP_FARE_ID,
        start_latitude=START_LAT,
        start_longitude=START_LNG,
        end_latitude=END_LAT,
        end_longitude=END_LNG,
    )
    assert response.status_code == codes.accepted

    # assert response looks like ride details
    response = response.json
    assert EXPECTED_RIDE_DETAILS_KEYS.issubset(response)


@uber_vcr.use_cassette()
def test_request_shared_ride(authorized_sandbox_client):
    """Test to request shared ride with access token."""
    try:
        response = authorized_sandbox_client.request_ride(
            product_id=UFP_SHARED_PRODUCT_ID,
            fare_id=UFP_SHARED_FARE_ID,
            seat_count=UFP_SHARED_SEAT_COUNT,
            start_latitude=START_LAT,
            start_longitude=START_LNG,
            end_latitude=END_LAT,
            end_longitude=END_LNG,
        )
    except Exception as e:
        print(e)
        print(e.errors[0].__dict__)
    assert response.status_code == codes.accepted


@uber_vcr.use_cassette()
def test_request_ride_with_no_default_product(authorized_sandbox_client):
    """Test to request ride with no default product."""
    response = authorized_sandbox_client.request_ride(
        fare_id=UFP_FARE_ID,
        start_latitude=START_LAT,
        start_longitude=START_LNG,
        end_latitude=END_LAT,
        end_longitude=END_LNG,
    )
    assert response.status_code == codes.accepted

    # assert response looks like ride details
    response = response.json
    assert EXPECTED_RIDE_DETAILS_KEYS.issubset(response)


@uber_vcr.use_cassette()
def test_request_ride_with_places(authorized_sandbox_client):
    """Test to request ride with place ids."""
    response = authorized_sandbox_client.request_ride(
        product_id=UFP_PRODUCT_ID,
        fare_id=UFP_FARE_ID,
        start_place_id='home',
        end_place_id='work',
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
def test_get_current_ride_details(authorized_sandbox_client):
    """Test to fetch current ride details with access token."""
    response = authorized_sandbox_client.get_current_ride_details()
    assert response.status_code == codes.ok

    # assert response looks like ride details
    response = response.json
    assert EXPECTED_RIDE_DETAILS_KEYS.issubset(response)
    assert response.get('status') == 'processing'


@uber_vcr.use_cassette()
def test_get_current_shared_ride_details(authorized_sandbox_client):
    """Test to fetch current shared ride details with access token."""
    response = authorized_sandbox_client.get_current_ride_details()
    assert response.status_code == codes.ok

    # assert response looks like ride details
    response = response.json
    assert EXPECTED_SHARED_RIDE_DETAILS_KEYS.issubset(response)
    assert response.get('status') == 'processing'


@uber_vcr.use_cassette()
def test_update_ride_destination(authorized_sandbox_client):
    """Test to update the trip destination."""
    response = authorized_sandbox_client.update_ride(
        RIDE_ID,
        end_latitude=UPDATE_LAT,
        end_longitude=UPDATE_LNG,
    )
    assert response.status_code == codes.no_content


@uber_vcr.use_cassette()
def test_update_ride_destination_with_places(authorized_sandbox_client):
    """Test to update the trip destination with a place ID."""
    response = authorized_sandbox_client.update_ride(
        RIDE_ID,
        end_place_id='work',
    )
    assert response.status_code == codes.no_content


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
    """Test to cancel ride with access token."""
    response = authorized_sandbox_client.cancel_ride(RIDE_ID)
    assert response.status_code == codes.no_content


@uber_vcr.use_cassette()
def test_cancel_current_ride(authorized_sandbox_client):
    """Test to cancel the current ride with access token."""
    response = authorized_sandbox_client.cancel_current_ride()
    assert response.status_code == codes.no_content


@uber_vcr.use_cassette()
def test_get_ride_receipt(authorized_sandbox_client):
    """Test to fetch ride receipt with access token."""
    response = authorized_sandbox_client.get_ride_receipt(RIDE_ID)
    assert response.status_code == codes.ok

    # assert response looks like ride receipt
    response = response.json
    assert EXPECTED_RECEIPT_KEYS.issubset(response)
    charges = response.get('charge_adjustments')

    for charge in charges:
        assert EXPECTED_INDIVIDUAL_CHARGE_KEYS.issubset(charge)


@uber_vcr.use_cassette()
def test_update_sandbox_product(authorized_sandbox_client):
    """Test to update sandbox ride status with access token."""
    response = authorized_sandbox_client.update_sandbox_product(
        product_id=NON_UFP_SURGE_PRODUCT_ID,
        surge_multiplier=2,
    )
    assert response.status_code == codes.no_content


@uber_vcr.use_cassette()
def test_request_ride_with_surge(authorized_sandbox_client):
    """Test raising a SurgeError when requesting a ride with surge."""
    with raises(SurgeError):
        authorized_sandbox_client.request_ride(
            product_id=NON_UFP_SURGE_PRODUCT_ID,
            start_latitude=NON_UFP_SURGE_START_LAT,
            start_longitude=NON_UFP_SURGE_START_LNG,
            end_latitude=NON_UFP_SURGE_END_LAT,
            end_longitude=NON_UFP_SURGE_END_LNG,
        )


def test_surge_error_formation(http_surge_error):
    """Test HTTP surge error response converted to SurgeError correctly."""
    surge_error = SurgeError(http_surge_error, 'msg')

    assert str(surge_error) == 'msg'
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


@uber_vcr.use_cassette()
def test_set_home_address(authorized_sandbox_client):
    """Test to update a user's home address with an access token."""
    response = authorized_sandbox_client.set_home_address(HOME_ADDRESS)
    assert response.status_code == codes.ok

    # assert response looks like places details
    response = response.json
    assert EXPECTED_PLACE_KEYS.issubset(response)
    assert response.get('address') == FULL_HOME_ADDRESS


@uber_vcr.use_cassette()
def test_get_home_address(authorized_sandbox_client):
    """Test to fetch a user's home address with an access token."""
    response = authorized_sandbox_client.get_home_address()
    assert response.status_code == codes.ok

    # assert response looks like places details
    response = response.json
    assert EXPECTED_PLACE_KEYS.issubset(response)
    assert response.get('address') == FULL_HOME_ADDRESS


@uber_vcr.use_cassette()
def test_set_work_address(authorized_sandbox_client):
    """Test to update a user's work address with an access token."""
    response = authorized_sandbox_client.set_work_address(WORK_ADDRESS)
    assert response.status_code == codes.ok

    # assert response looks like places details
    response = response.json
    assert EXPECTED_PLACE_KEYS.issubset(response)
    assert response.get('address') == FULL_WORK_ADDRESS


@uber_vcr.use_cassette()
def test_get_work_address(authorized_sandbox_client):
    """Test to fetch a user's work address with an access token."""
    response = authorized_sandbox_client.get_work_address()
    assert response.status_code == codes.ok

    # assert response looks like places details
    response = response.json
    assert EXPECTED_PLACE_KEYS.issubset(response)
    assert response.get('address') == FULL_WORK_ADDRESS


@uber_vcr.use_cassette()
def test_get_payment_methods(authorized_sandbox_client):
    """Test to get a list of payment methods with an access token."""
    response = authorized_sandbox_client.get_payment_methods()
    assert response.status_code == codes.ok

    response = response.json
    payments = response.get('payment_methods')

    for payment in payments:
        assert EXPECTED_PAYMENT_KEYS.issubset(payment)
