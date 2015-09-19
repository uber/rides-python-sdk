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

from json import dumps
from requests import Request
from urllib import quote
from urllib import urlencode
from urlparse import urljoin

from uber_rides.utils.handlers import error_handler
from uber_rides.utils import http


def generate_data(method, args):
    """Assign arguments to body or URL of an HTTP request.

    Parameters
        method (str)
            HTTP Method. (e.g. 'POST')
        args (dict)
            Dictionary of data to attach to each Request.
            e.g. {'latitude': 37.561, 'longitude': -122.742}

    Returns
        (str or dict)
            Either params containing the dictionary of arguments
            or data containing arugments in JSON-formatted string.
    """
    data = {}
    params = {}

    if method in http.BODY_METHODS:
        data = dumps(args)
    else:
        params = args

    return data, params


def generate_prepared_request(method, url, headers, data, params, handlers):
    """Add handlers and prepare a Request.

    Parameters
        method (str)
            HTTP Method. (e.g. 'POST')
        headers (dict)
            Headers to send.
        data (JSON-formatted str)
            Body to attach to the request.
        params (dict)
            Dictionary of URL parameters to append to the URL.
        handlers (list)
            List of callback hooks, for error handling.

    Returns
        (requests.PreparedRequest)
            The fully mutable PreparedRequest object,
            containing the exact bytes to send to the server.
    """
    request = Request(
        method=method,
        url=url,
        headers=headers,
        data=data,
        params=params,
    )

    handlers.append(error_handler)

    for handler in handlers:
        request.register_hook('response', handler)

    return request.prepare()


def build_url(host, path, params=None):
    """Build a URL.

    This method encodes the parameters and adds them
    to the end of the base URL, then adds scheme and hostname.

    Parameters
        host (str)
            Base URL of the Uber Server that handles API calls.
        path (str)
            Target path to add to the host (e.g. 'v1/products').
        params (dict)
            Optional dictionary of parameters to add to the URL.

    Returns
        (str)
            The fully formed URL.
    """
    path = quote(path)
    params = params or {}

    if params:
        path = '/{}?{}'.format(path, urlencode(params))
    else:
        path = '/{}'.format(path)

    if not host.startswith(http.URL_SCHEME):
        host = '{}{}'.format(http.URL_SCHEME, host)

    return urljoin(host, path)
