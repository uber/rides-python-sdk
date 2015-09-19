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

from uber_rides.errors import ClientError
from uber_rides.errors import ServerError


def error_handler(response, **kwargs):
    """Error Handler to surface 4XX and 5XX errors.

    Attached as a callback hook on the Request object.

    Parameters
        response (requests.Response)
            The HTTP response from an API request.
        **kwargs
            Arbitrary keyword arguments.

    Raises
        ClientError (ApiError)
            Raised if response contains a 4XX status code.
        ServerError (ApiError)
            Raised if response contains a 5XX status code.

    Returns
        response (requests.Response)
            The original HTTP response from the API request.
    """
    if 400 <= response.status_code <= 499:
        raise ClientError(response)

    elif 500 <= response.status_code <= 599:
        raise ServerError(response)

    return response
