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

from pytest import fixture

from uber_rides.utils.request import build_url
from uber_rides.utils.request import generate_data


LAT = 37.7
LNG = -122.4
HOST = 'api.uber.com'
HTTPS_HOST = '{}{}'.format('https://', HOST)
DEFAULT_TARGET = 'products'
SPECIAL_CHAR_TARGET = '~products'
DEFAULT_BASE_URL = 'https://api.uber.com/products'


@fixture
def default_http_arguments_as_json():
    return {
        'latitude': LAT,
        'longitude': LNG,
    }


@fixture
def default_http_arguments_as_string():
    return '{{"latitude": {}, "longitude": {}}}'.format(LAT, LNG)


def test_generate_data_with_POST(
    default_http_arguments_as_json,
    default_http_arguments_as_string,
):
    """Assign arguments to body of request in POST."""
    data, params = generate_data('POST', default_http_arguments_as_json)
    assert not params
    assert data == default_http_arguments_as_string


def test_generate_data_with_PATCH(
    default_http_arguments_as_json,
    default_http_arguments_as_string,
):
    """Assign arguments to body of request in PATCH."""
    data, params = generate_data('PATCH', default_http_arguments_as_json)
    assert not params
    assert data == default_http_arguments_as_string


def test_generate_data_with_PUT(
    default_http_arguments_as_json,
    default_http_arguments_as_string,
):
    """Assign arguments to body of request in PUT."""
    data, params = generate_data('PUT', default_http_arguments_as_json)
    assert not params
    assert data == default_http_arguments_as_string


def test_generate_data_with_GET(default_http_arguments_as_json):
    """Assign arguments to querystring params in GET."""
    data, params = generate_data('GET', default_http_arguments_as_json)
    assert params == default_http_arguments_as_json
    assert not data


def test_generate_data_with_DELETE(default_http_arguments_as_json,):
    """Assign arguments to querystring params in DELETE."""
    data, params = generate_data('DELETE', default_http_arguments_as_json)
    assert params == default_http_arguments_as_json
    assert not data


def test_build_url_no_params():
    """Build URL with no parameters."""
    url = build_url(HOST, DEFAULT_TARGET)
    assert url == DEFAULT_BASE_URL


def test_build_url_with_scheme():
    """Build URL with https scheme."""
    url = build_url(HTTPS_HOST, DEFAULT_TARGET)
    assert url == DEFAULT_BASE_URL


def test_build_special_char_url():
    """Build URL special characters."""
    url = build_url(HOST, SPECIAL_CHAR_TARGET)
    assert url == 'https://api.uber.com/%7Eproducts'


def test_build_url_params(default_http_arguments_as_json):
    """Build URL with querystring parameters."""
    url = build_url(HOST, DEFAULT_TARGET, default_http_arguments_as_json)
    url_with_params = '{}?latitude={}&longitude={}'
    assert url == url_with_params.format(DEFAULT_BASE_URL, LAT, LNG)
