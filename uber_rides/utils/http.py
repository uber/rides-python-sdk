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

URL_SCHEME = 'https://'

ALLOWED_METHODS = frozenset(['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
BODY_METHODS = frozenset(['POST', 'PUT', 'PATCH'])
QUERY_METHODS = frozenset(['GET', 'DELETE'])

DEFAULT_CONTENT_HEADERS = {'content-type': 'application/json'}

STATUS_OK = 200
STATUS_UNAUTHORIZED = 401
STATUS_CONFLICT = 409
STATUS_UNPROCESSABLE_ENTITY = 422
STATUS_INTERNAL_SERVER_ERROR = 500
STATUS_SERVICE_UNAVAILABLE = 503

ERROR_CODE_DESCRIPTION_DICT = {
    'distance_exceeded': 'Distance between two points exceeds 100 miles.',
    'unauthorized': 'Invalid OAuth 2.0 credentials provided.',
    'validation_failed': 'Invalid request.',
    'internal_server_error': 'Unexpected internal server error occurred.',
    'service_unavailable': 'Service temporarily unavailable.',
    'surge': 'Surge pricing is in effect.',
    'same_pickup_dropoff': 'Pickup and Dropoff can\'t be the same.',
}

VALID_TOKEN_TYPES = frozenset(['Token', 'Bearer'])
