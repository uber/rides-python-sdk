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

from uber_rides.errors import ClientError
from uber_rides.errors import ErrorDetails
from uber_rides.errors import ServerError
from uber_rides.utils import http


@fixture
def simple_401_error():
    code = 'unauthorized'

    mock_error = Mock(
        status_code=http.STATUS_UNAUTHORIZED,
        headers=http.DEFAULT_CONTENT_HEADERS,
    )

    error_response = {
        'message': http.ERROR_CODE_DESCRIPTION_DICT[code],
        'code': code,
    }

    mock_error.json = Mock(return_value=error_response)
    return mock_error


@fixture
def simple_422_validation_error():
    code = 'validation_failed'

    mock_error = Mock(
        status_code=http.STATUS_UNPROCESSABLE_ENTITY,
        headers=http.DEFAULT_CONTENT_HEADERS,
    )

    error_response = {
        'fields': {
            'latitude': 'Must be between -90.0 and 90.0',
            'longitude': 'Must be between -180.0 and 180.0',
        },
        'message': http.ERROR_CODE_DESCRIPTION_DICT[code],
        'code': code,
    }

    mock_error.json = Mock(return_value=error_response)
    return mock_error


@fixture
def simple_422_distance_exceeded_error():
    code = 'distance_exceeded'

    mock_error = Mock(
        status_code=http.STATUS_UNPROCESSABLE_ENTITY,
        headers=http.DEFAULT_CONTENT_HEADERS,
    )

    error_response = {
        'fields': {
            'start_longitude': http.ERROR_CODE_DESCRIPTION_DICT[code],
            'end_longitude': http.ERROR_CODE_DESCRIPTION_DICT[code],
            'start_latitude': http.ERROR_CODE_DESCRIPTION_DICT[code],
            'end_latitude': http.ERROR_CODE_DESCRIPTION_DICT[code],
        },
        'message': http.ERROR_CODE_DESCRIPTION_DICT[code],
        'code': code,
    }

    mock_error.json = Mock(return_value=error_response)
    return mock_error


@fixture
def simple_500_error():
    code = 'internal_server_error'

    mock_error = Mock(
        status_code=http.STATUS_INTERNAL_SERVER_ERROR,
        headers=http.DEFAULT_CONTENT_HEADERS,
    )

    error_response = {
        'message': http.ERROR_CODE_DESCRIPTION_DICT[code],
        'code': code,
    }

    mock_error.json = Mock(return_value=error_response)
    return mock_error


@fixture
def simple_503_error():
    code = 'service_unavailable'

    mock_error = Mock(
        status_code=http.STATUS_SERVICE_UNAVAILABLE,
        headers=http.DEFAULT_CONTENT_HEADERS,
    )

    error_response = {
        'message': http.ERROR_CODE_DESCRIPTION_DICT[code],
        'code': code,
    }

    mock_error.json = Mock(return_value=error_response)
    return mock_error


@fixture
def complex_409_surge_error():
    code = 'surge'

    mock_error = Mock(
        status_code=http.STATUS_CONFLICT,
        headers=http.DEFAULT_CONTENT_HEADERS,
    )

    error_response = {
        'meta': {
            'surge_confirmation': {
                'href': 'api.uber.com/v1/surge-confirmations/abc',
                'surge_confirmation_id': 'abc',
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


@fixture
def complex_422_same_pickup_dropoff_error():
    code = 'same_pickup_dropoff'

    mock_error = Mock(
        status_code=http.STATUS_UNPROCESSABLE_ENTITY,
        headers=http.DEFAULT_CONTENT_HEADERS,
    )

    error_response = {
        'meta': {},
        'errors': [
            {
                'status': http.STATUS_UNPROCESSABLE_ENTITY,
                'code': code,
                'title': http.ERROR_CODE_DESCRIPTION_DICT[code],
            },
        ],
    }

    mock_error.json = Mock(return_value=error_response)
    return mock_error


def test_simple_401_error(simple_401_error):
    """Test Unauthorized Error converted to ClientError correctly."""
    client_error = ClientError(simple_401_error, 'msg')

    assert client_error.message == 'msg'
    assert isinstance(client_error.errors, list)
    assert isinstance(client_error.meta, dict)
    assert not client_error.meta

    error_details = client_error.errors[0]
    expected_code = 'unauthorized'
    expected_description = http.ERROR_CODE_DESCRIPTION_DICT[expected_code]

    assert isinstance(error_details, ErrorDetails)
    assert error_details.status == http.STATUS_UNAUTHORIZED
    assert error_details.code == expected_code
    assert error_details.title == expected_description


def test_simple_422_validation_error(simple_422_validation_error):
    """Test Validation Error converted to ClientError correctly."""
    client_error = ClientError(simple_422_validation_error, 'msg')

    assert client_error.message == 'msg'
    assert isinstance(client_error.errors, list)
    assert isinstance(client_error.meta, dict)

    error_details = client_error.errors[0]
    expected_code = 'validation_failed'
    expected_description = http.ERROR_CODE_DESCRIPTION_DICT[expected_code]

    assert isinstance(error_details, ErrorDetails)
    assert error_details.status == http.STATUS_UNPROCESSABLE_ENTITY
    assert error_details.code == expected_code
    assert error_details.title == expected_description

    meta = client_error.meta

    fields = {
        'fields': {
            'latitude': 'Must be between -90.0 and 90.0',
            'longitude': 'Must be between -180.0 and 180.0',
        },
    }

    assert meta == fields


def test_simple_422_distance_exceeded_error(
    simple_422_distance_exceeded_error
):
    """Test Distance Exceeded Error converted to ClientError correctly."""
    client_error = ClientError(simple_422_distance_exceeded_error, 'msg')

    assert client_error.message == 'msg'
    assert isinstance(client_error.errors, list)
    assert isinstance(client_error.meta, dict)

    error_details = client_error.errors[0]
    expected_code = 'distance_exceeded'
    expected_description = http.ERROR_CODE_DESCRIPTION_DICT[expected_code]

    assert isinstance(error_details, ErrorDetails)
    assert error_details.status == http.STATUS_UNPROCESSABLE_ENTITY
    assert error_details.code == expected_code
    assert error_details.title == expected_description

    meta = client_error.meta

    fields = {
        'fields': {
            'start_longitude': http.ERROR_CODE_DESCRIPTION_DICT[expected_code],
            'end_longitude': http.ERROR_CODE_DESCRIPTION_DICT[expected_code],
            'start_latitude': http.ERROR_CODE_DESCRIPTION_DICT[expected_code],
            'end_latitude': http.ERROR_CODE_DESCRIPTION_DICT[expected_code],
        },
    }

    assert meta == fields


def test_simple_500_error(simple_500_error):
    """Test Internal Server Error converted to ClientError correctly."""
    server_error = ServerError(simple_500_error, 'msg')

    assert server_error.message == 'msg'
    assert isinstance(server_error.meta, dict)
    assert not server_error.meta

    error_details = server_error.error   # single error instead of array
    expected_code = 'internal_server_error'
    expected_description = http.ERROR_CODE_DESCRIPTION_DICT[expected_code]

    assert isinstance(error_details, ErrorDetails)
    assert error_details.status == http.STATUS_INTERNAL_SERVER_ERROR
    assert error_details.code == expected_code
    assert error_details.title == expected_description


def test_simple_503_error(simple_503_error):
    """Test Service Unavailable Error converted to ClientError correctly."""
    server_error = ServerError(simple_503_error, 'msg')

    assert server_error.message == 'msg'
    assert isinstance(server_error.meta, dict)
    assert not server_error.meta

    error_details = server_error.error   # single error instead of array
    expected_code = 'service_unavailable'
    expected_description = http.ERROR_CODE_DESCRIPTION_DICT[expected_code]

    assert isinstance(error_details, ErrorDetails)
    assert error_details.status == http.STATUS_SERVICE_UNAVAILABLE
    assert error_details.code == expected_code
    assert error_details.title == expected_description


def test_complex_409_surge_error(complex_409_surge_error):
    """Test Surge Error converted to ClientError correctly."""
    client_error = ClientError(complex_409_surge_error, 'msg')

    assert client_error.message == 'msg'
    assert isinstance(client_error.errors, list)
    assert isinstance(client_error.meta, dict)

    error_details = client_error.errors[0]
    expected_code = 'surge'
    expected_description = http.ERROR_CODE_DESCRIPTION_DICT[expected_code]

    assert isinstance(error_details, ErrorDetails)
    assert error_details.status == http.STATUS_CONFLICT
    assert error_details.code == expected_code
    assert error_details.title == expected_description

    surge_meta = client_error.meta['surge_confirmation']

    assert surge_meta['surge_confirmation_id'] == 'abc'
    assert surge_meta['href'] == 'api.uber.com/v1/surge-confirmations/abc'


def test_complex_422_same_pickup_dropoff_error(
    complex_422_same_pickup_dropoff_error
):
    """Test Same Pickup-Dropoff Error converted to ClientError correctly."""
    client_error = ClientError(complex_422_same_pickup_dropoff_error, 'msg')

    assert client_error.message == 'msg'
    assert isinstance(client_error.errors, list)
    assert isinstance(client_error.meta, dict)
    assert not client_error.meta

    error_details = client_error.errors[0]
    expected_code = 'same_pickup_dropoff'
    expected_description = http.ERROR_CODE_DESCRIPTION_DICT[expected_code]

    assert isinstance(error_details, ErrorDetails)
    assert error_details.status == http.STATUS_UNPROCESSABLE_ENTITY
    assert error_details.code == expected_code
    assert error_details.title == expected_description
