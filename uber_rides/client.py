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

"""Python client for the Uber API.

This client is designed to make calls to the Uber API.
An UberRidesClient is instantiated with a Session which holds either
your server token or OAuth 2.0 credentials. Your usage of this
module might look like:

    client = UberRidesClient(session)
    products = client.get_products(latitude, longitude)
    profile = client.get_user_profile()
    ride_details = client.get_ride_details(ride_id)
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from requests import codes

from uber_rides.auth import refresh_access_token
from uber_rides.auth import revoke_access_token
from uber_rides.errors import ClientError
from uber_rides.errors import UberIllegalState
from uber_rides.request import Request
from uber_rides.utils import auth


VALID_PRODUCT_STATUS = frozenset([
    'processing',
    'accepted',
    'arriving',
    'in_progress',
    'driver_canceled',
    'completed',
])

PRODUCTION_HOST = 'api.uber.com'
SANDBOX_HOST = 'sandbox-api.uber.com'


class UberRidesClient(object):
    """Class to make calls to the Uber API."""

    def __init__(self, session, sandbox_mode=False):
        """Initialize an UberRidesClient.

        Parameters
            session (Session)
                The Session object containing access credentials.
            sandbox_mode (bool)
                Default (False) is not using sandbox mode.
        """
        self.session = session
        self.api_host = SANDBOX_HOST if sandbox_mode else PRODUCTION_HOST

    def _api_call(self, method, target, args=None):
        """Create a Request object and execute the call to the API Server.

        Parameters
            method (str)
                HTTP request (e.g. 'POST').
            target (str)
                The target URL with leading slash (e.g. '/v1/products').
            args (dict)
                Optional dictionary of arguments to attach to the request.

        Returns
            (Response)
                The server's response to an HTTP request.
        """
        self.refresh_oauth_credential()
        handlers = [surge_handler]
        request = Request(
            auth_session=self.session,
            api_host=self.api_host,
            method=method,
            path=target,
            handlers=handlers,
            args=args,
        )
        return request.execute()

    def get_products(self, latitude, longitude):
        """Get information about the Uber products offered at a given location.

        Parameters
            latitude (float)
                The latitude component of a location.
            longitude (float)
                The longitude component of a location.

        Returns
            (Response)
                A Response object containing available products information.
        """
        args = {
            'latitude': latitude,
            'longitude': longitude,
        }

        return self._api_call('GET', 'v1/products', args=args)

    def get_product(self, product_id):
        """Get information about a specific Uber product.

        Parameters
            product_id (str)
                Unique identifier representing a specific product for a
                given location.

        Returns
            (Response)
                A Response containing information about a specific product.
        """
        endpoint = 'v1/products/{}'.format(product_id)
        return self._api_call('GET', endpoint)

    def get_price_estimates(
        self,
        start_latitude,
        start_longitude,
        end_latitude,
        end_longitude,
    ):
        """Get price estimates for products at a given location.

        Parameters
            start_latitude (float)
                The latitude component of a start location.
            start_longitude (float)
                The longitude component of a start location.
            end_latitude (float)
                The latitude component of a end location.
            end_longitude (float)
                The longitude component of a end location.

        Returns
            (Response)
                A Response object containing each product's price estimates.
        """
        args = {
            'start_latitude': start_latitude,
            'start_longitude': start_longitude,
            'end_latitude': end_latitude,
            'end_longitude': end_longitude,
        }

        return self._api_call('GET', 'v1/estimates/price', args=args)

    def get_pickup_time_estimates(self, start_latitude, start_longitude):
        """Get pickup time estimates for products at a given location.

        Parameters
            start_latitude (float)
                The latitude component of a start location.
            start_longitude (float)
                The longitude component of a start location.

        Returns
            (Response)
                A Response containing each product's pickup time estimates.
        """
        args = {
            'start_latitude': start_latitude,
            'start_longitude': start_longitude,
        }

        return self._api_call('GET', 'v1/estimates/time', args=args)

    def get_promotions(
        self,
        start_latitude,
        start_longitude,
        end_latitude,
        end_longitude,
    ):
        """Get information about the promotions available to a user.

        Parameters
            start_latitude (float)
                The latitude component of a start location.
            start_longitude (float)
                The longitude component of a start location.
            end_latitude (float)
                The latitude component of a end location.
            end_longitude (float)
                The longitude component of a end location.

        Returns
            (Response)
                A Response object containing available promotions.
        """
        args = {
            'start_latitude': start_latitude,
            'start_longitude': start_longitude,
            'end_latitude': end_latitude,
            'end_longitude': end_longitude,
        }

        return self._api_call('GET', 'v1/promotions', args=args)

    def get_user_activity(self, offset=None, limit=None):
        """Get activity about the user's lifetime activity with Uber.

        Parameters
            offset (int)
                The integer offset for activity results. Default is 0.
            limit (int)
                Integer amount of results to return. Maximum is 50.
                Default is 5.

        Returns
            (Response)
                A Response object containing ride history.
        """
        args = {
            'offset': offset,
            'limit': limit,
        }

        return self._api_call('GET', 'v1.2/history', args=args)

    def get_user_profile(self):
        """Get information about the authorized Uber user.

        Returns
            (Response)
                A Response object containing account information.
        """
        return self._api_call('GET', 'v1/me')

    def estimate_ride(
        self,
        product_id,
        start_latitude,
        start_longitude,
        end_latitude=None,
        end_longitude=None,
    ):
        """Estimate ride details given a product, start, and end location.

        Only pickup time estimates and surge pricing information provided
        if no end location provided.

        Parameters
            product_id (str)
                Unique identifier representing a specific product for a
                given location.
            start_latitude (float)
                The latitude component of a start location.
            start_longitude (float)
                The longitude component of a start location.
            end_latitude (float)
                Optional latitude component of a end location.
            end_longitude (float)
                Optional longitude component of a end location.

        Returns
            (Response)
                A Response object containing time, price, and distance
                estimates for a ride.
        """
        args = {
            'product_id': product_id,
            'start_latitude': start_latitude,
            'start_longitude': start_longitude,
            'end_latitude': end_latitude,
            'end_longitude': end_longitude,
        }

        return self._api_call('POST', 'v1/requests/estimate', args=args)

    def request_ride(
        self,
        product_id,
        start_latitude,
        start_longitude,
        end_latitude,
        end_longitude,
        surge_confirmation_id=None,
    ):
        """Request a ride on behalf of an Uber user.

        Parameters
            product_id (str)
                Unique identifier representing a specific product for a
                given location.
            start_latitude (float)
                The latitude component of a start location.
            start_longitude (float)
                The longitude component of a start location.
            end_latitude (float)
                The latitude component of a end location.
            end_longitude (float)
                The longitude component of a end location.
            surge_confirmation_id (str)
                Optional unique identifier of the surge session for a user.

        Returns
            (Response)
                A Response object containing the ride request ID and other
                details about the requested ride.

        Raises
            SurgeError (ClientError)
                Thrown when the requested product is currently surging.
                User must confirm surge price through surge_confirmation_href.
        """
        args = {
            'product_id': product_id,
            'start_latitude': start_latitude,
            'start_longitude': start_longitude,
            'end_latitude': end_latitude,
            'end_longitude': end_longitude,
            'surge_confirmation_id': surge_confirmation_id,
        }

        return self._api_call('POST', 'v1/requests', args=args)

    def get_ride_details(self, ride_id):
        """Get status details about an ongoing or past ride.

        Params
            ride_id (str)
                The unique ID of the Ride Request.

        Returns
            (Response)
                A Response object containing the ride's
                status, location, driver, and other details.
        """
        endpoint = 'v1/requests/{}'.format(ride_id)
        return self._api_call('GET', endpoint)

    def cancel_ride(self, ride_id):
        """Cancel an ongoing ride on behalf of a user.

        Params
            ride_id (str)
                The unique ID of the Ride Request.

        Returns
            (Response)
                A Response object with successful status_code
                if ride was canceled.
        """
        endpoint = 'v1/requests/{}'.format(ride_id)
        return self._api_call('DELETE', endpoint)

    def get_ride_map(self, ride_id):
        """Get a map with a visual representation of a Request.

        Params
            ride_id (str)
                The unique ID of the Ride Request.

        Returns
            (Response)
                A Response object with a link to a map.
        """
        endpoint = 'v1/requests/{}/map'.format(ride_id)
        return self._api_call('GET', endpoint)

    def get_ride_receipt(self, ride_id):
        """Get receipt information from a completed ride.

        Params
            ride_id (str)
                The unique ID of the Ride Request.

        Returns
            (Response)
                A Response object containing the charges for
                the given ride.
        """
        endpoint = 'v1/requests/{}/receipt'.format(ride_id)
        return self._api_call('GET', endpoint)

    def update_sandbox_ride(self, ride_id, new_status):
        """Update the status of an ongoing sandbox request.

        Params
            ride_id (str)
                The unique ID of the Ride Request.
            new_status (str)
                Status from VALID_PRODUCT_STATUS.

        Returns
            (Response)
                A Response object with successful status_code
                if ride status was updated.
        """
        if new_status not in VALID_PRODUCT_STATUS:
            message = '{} is not a valid product status.'
            raise UberIllegalState(message.format(new_status))

        args = {'status': new_status}
        endpoint = 'v1/sandbox/requests/{}'.format(ride_id)
        return self._api_call('PUT', endpoint, args=args)

    def update_sandbox_product(
        self,
        product_id,
        surge_multiplier=None,
        drivers_available=None,
    ):
        """Update sandbox product availability.

        Params
            product_id (str)
                Unique identifier representing a specific product for a
                given location.
            surge_multiplier (float)
                Optional surge multiplier to manipulate pricing of product.
            drivers_available (bool)
                Optional boolean to manipulate availability of product.

        Returns
            (Response)
                The Response with successful status_code
                if product status was updated.
        """
        args = {
            'surge_multiplier': surge_multiplier,
            'drivers_available': drivers_available,
        }

        endpoint = 'v1/sandbox/products/{}'.format(product_id)
        return self._api_call('PUT', endpoint, args=args)

    def refresh_oauth_credential(self):
        """Refresh session's OAuth 2.0 credentials if they are stale."""
        if self.session.token_type == auth.SERVER_TOKEN_TYPE:
            return

        credential = self.session.oauth2credential
        if credential.is_stale():
            refresh_session = refresh_access_token(credential)
            self.session = refresh_session

    def revoke_oauth_credential(self):
        """Revoke the session's OAuth 2.0 credentials."""
        if self.session.token_type == auth.SERVER_TOKEN_TYPE:
            return

        credential = self.session.oauth2credential
        revoke_access_token(credential)


def surge_handler(response, **kwargs):
    """Error Handler to surface 409 Surge Conflict errors.

    Attached as a callback hook on the Request object.

    Parameters
        response (requests.Response)
            The HTTP response from an API request.
        **kwargs
            Arbitrary keyword arguments.
    """
    if response.status_code == codes.conflict:
        json = response.json()
        error = json['errors'][0]

        if error['code'] == 'surge':
            raise SurgeError(response)

    return response


class SurgeError(ClientError):
    """Raise for 409 Surge Conflicts."""

    def __init__(self, response, message=None):
        """
        Parameters
            response (requests.Response)
                The HTTP response from an API request.
            message (str)
                An error message string. If one is not provided, the
                default message is used.
        """
        if not message:
            message = (
                'Surge pricing is currently in effect for this product. '
                'User must confirm surge by visiting the confirmation url.'
            )

        super(SurgeError, self).__init__(
            response=response,
            message=message,
        )

        surge_href, surge_id = self.adapt_meta(self.meta)
        self.surge_confirmation_href = surge_href
        self.surge_confirmation_id = surge_id

    def adapt_meta(self, meta):
        """Convert meta from error response to href and surge_id attributes."""

        surge = meta.get('surge_confirmation')
        href = surge.get('href')
        surge_id = surge.get('surge_confirmation_id')

        return href, surge_id
