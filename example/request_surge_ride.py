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

"""Use an UberRidesClient to request and complete a ride.

This example demonstrates how to use an UberRidesClient to request a ride
under surge. After successfully requesting a ride, it updates the
ride status to 'completed' and deactivates surge.

To run this example:

    (1) Run `python authorization_code_grant.py` to get OAuth 2.0 Credentials
    (2) Run `python request_surge_ride.py`
    (3) The UberRidesClient will make API calls and print the
        results to your terminal.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from urllib.parse import parse_qs
from urllib.parse import urlparse

from example.utils import create_uber_client
from example.utils import fail_print
from example.utils import import_oauth2_credentials
from example.utils import paragraph_print
from example.utils import response_print
from example.utils import success_print

from uber_rides.client import SurgeError
from uber_rides.errors import ClientError
from uber_rides.errors import ServerError

# uberX
PRODUCT_ID = 'a1111c8c-c720-46c3-8534-2fcdd730040d'

# California Academy of Sciences
START_LAT = 37.770
START_LNG = -122.466

# Pier 39
END_LAT = 37.791
END_LNG = -122.405


def estimate_ride(api_client):
    """Use an UberRidesClient to fetch a ride estimate and print the results.

    Parameters
        api_client (UberRidesClient)
            An authorized UberRidesClient with 'request' scope.
    """
    try:
        estimate = api_client.estimate_ride(
            product_id=PRODUCT_ID,
            start_latitude=START_LAT,
            start_longitude=START_LNG,
            end_latitude=END_LAT,
            end_longitude=END_LNG,
        )

    except (ClientError, ServerError) as error:
        fail_print(error)

    else:
        success_print(estimate.json)


def update_surge(api_client, surge_multiplier):
    """Use an UberRidesClient to update surge and print the results.

    Parameters
        api_client (UberRidesClient)
            An authorized UberRidesClient with 'request' scope.
        surge_mutliplier (float)
            The surge multiple for a sandbox product. A multiplier greater than
            or equal to 2.0 will require the two stage confirmation screen.
    """
    try:
        update_surge = api_client.update_sandbox_product(
            PRODUCT_ID,
            surge_multiplier=surge_multiplier,
        )

    except (ClientError, ServerError) as error:
        fail_print(error)

    else:
        success_print(update_surge.status_code)


def update_ride(api_client, ride_status, ride_id):
    """Use an UberRidesClient to update ride status and print the results.

    Parameters
        api_client (UberRidesClient)
            An authorized UberRidesClient with 'request' scope.
        ride_status (str)
            New ride status to update to.
        ride_id (str)
            Unique identifier for ride to update.
    """
    try:
        update_product = api_client.update_sandbox_ride(ride_id, ride_status)

    except (ClientError, ServerError) as error:
        fail_print(error)

    else:
        message = '{} New status: {}'
        message = message.format(update_product.status_code, ride_status)
        success_print(message)


def request_ride(api_client, surge_confirmation_id=None):
    """Use an UberRidesClient to request a ride and print the results.

    If the product has a surge_multiple greater than or equal to 2.0,
    a SurgeError is raised. Confirm surge by visiting the
    surge_confirmation_url and automatically try the request again.

    Parameters
        api_client (UberRidesClient)
            An authorized UberRidesClient with 'request' scope.
        surge_confirmation_id (string)
            Unique identifer received after confirming surge.

    Returns
        The unique ID of the requested ride.
    """
    try:
        request = api_client.request_ride(
            product_id=PRODUCT_ID,
            start_latitude=START_LAT,
            start_longitude=START_LNG,
            end_latitude=END_LAT,
            end_longitude=END_LNG,
            surge_confirmation_id=surge_confirmation_id,
        )

    except SurgeError as e:
        surge_message = 'Confirm surge by visiting: \n{}\n'
        surge_message = surge_message.format(e.surge_confirmation_href)
        response_print(surge_message)

        confirm_url = 'Copy the URL you are redirected to and paste here: \n'
        result = input(confirm_url).strip()

        querystring = urlparse(result).query
        query_params = parse_qs(querystring)
        surge_id = query_params.get('surge_confirmation_id')[0]

        # automatically try request again
        return request_ride(api_client, surge_id)

    except (ClientError, ServerError) as error:
        fail_print(error)
        return

    else:
        success_print(request.json)
        return request.json.get('request_id')


def get_ride_details(api_client, ride_id):
    """Use an UberRidesClient to get ride details and print the results.

    Parameters
        api_client (UberRidesClient)
            An authorized UberRidesClient with 'request' scope.
        ride_id (str)
            Unique ride identifier.
    """
    try:
        ride_details = api_client.get_ride_details(ride_id)

    except (ClientError, ServerError) as error:
        fail_print(error)

    else:
        success_print(ride_details.json)


if __name__ == '__main__':
    """Run the example.

    Create an UberRidesClient from OAuth 2.0 Credentials, update a sandbox
    product's surge, request and complete a ride.
    """
    credentials = import_oauth2_credentials()
    api_client = create_uber_client(credentials)

    paragraph_print("Ride estimates before surge.")
    estimate_ride(api_client)

    paragraph_print("Activate surge.")
    update_surge(api_client, 2.0)

    paragraph_print("Ride estimates after surge.")
    estimate_ride(api_client)

    paragraph_print("Request a ride with surging product.")
    ride_id = request_ride(api_client)

    paragraph_print("Update ride status to accepted.")
    update_ride(api_client, 'accepted', ride_id)

    paragraph_print("Updated ride details.")
    get_ride_details(api_client, ride_id)

    paragraph_print("Update ride status to completed.")
    update_ride(api_client, 'in_progress', ride_id)
    update_ride(api_client, 'completed', ride_id)

    paragraph_print("Updated ride details.")
    get_ride_details(api_client, ride_id)

    paragraph_print("Deactivate surge.")
    update_surge(api_client, 1.0)
