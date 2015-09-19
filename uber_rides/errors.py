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


class APIError(Exception):
    """Parent class of all Uber API errors."""
    pass


class HTTPError(APIError):
    """Parent class of all HTTP errors."""

    def _adapt_response(self, response):
        """Convert error responses to standardized ErrorDetails."""
        if response.headers['content-type'] == 'application/json':
            body = response.json()
            status = response.status_code

            if body.get('errors'):
                return self._complex_response_to_error_adapter(body)

            elif body.get('code') and body.get('message'):
                return self._simple_response_to_error_adapter(status, body)

            elif body.get('error'):
                code = response.reason
                return self._message_to_error_adapter(status, code, body)

        raise UnknownHttpError(response)

    def _complex_response_to_error_adapter(self, body):
        """Convert a list of error responses."""
        meta = body.get('meta')
        errors = body.get('errors')
        e = []

        for error in errors:
            status = error['status']
            code = error['code']
            title = error['title']

            e.append(ErrorDetails(status, code, title))

        return e, meta

    def _simple_response_to_error_adapter(self, status, original_body):
        """Convert a single error response."""
        body = original_body.copy()
        code = body.pop('code')
        title = body.pop('message')
        meta = body    # save whatever is left in the response

        e = [ErrorDetails(status, code, title)]

        return e, meta

    def _message_to_error_adapter(self, status, code, original_body):
        """Convert single string message to error response."""
        body = original_body.copy()
        title = body.pop('error')
        meta = body    # save whatever is left in the response

        e = [ErrorDetails(status, code, title)]

        return e, meta


class ClientError(HTTPError):
    """Raise for 4XX Errors.

    Contains an array of ErrorDetails objects.
    """

    def __init__(self, response, message=None):
        """
        Parameters
            response
                The 4XX HTTP response.
            message
                An error message string. If one is not provided, the
                default message is used.
        """
        if not message:
            message = (
                'The request contains bad syntax or cannot be filled '
                'due to a fault from the client sending the request.'
            )

        super(ClientError, self).__init__(message)
        errors, meta = super(ClientError, self)._adapt_response(response)
        self.errors = errors
        self.meta = meta


class ServerError(HTTPError):
    """Raise for 5XX Errors.

    Contains a single ErrorDetails object.
    """

    def __init__(self, response, message=None):
        """
        Parameters
            response
                The 5XX HTTP response.
            message
                An error message string. If one is not provided, the
                default message is used.
        """
        if not message:
            message = (
                'The server encounter an error or is '
                'unable to process the request.'
            )

        super(ServerError, self).__init__(message)
        self.error, self.meta = self._adapt_response(response)

    def _adapt_response(self, response):
        """Convert various error responses to standardized ErrorDetails."""
        errors, meta = super(ServerError, self)._adapt_response(response)
        return errors[0], meta  # single error instead of array


class ErrorDetails(object):
    """Class to standardize all errors."""

    def __init__(self, status, code, title):
        self.status = status
        self.code = code
        self.title = title


class UnknownHttpError(APIError):
    """Throw when an unknown HTTP error occurs.

    Thrown when a previously unseen error is
    received and there is no standard schema to convert
    it into a well-formed HttpError.
    """

    def __init__(self, response):
        super(UnknownHttpError, self).__init__()
        self.response = response


class UberIllegalState(APIError):
    """Raise for Illegal State Errors.

    Thrown when the environment or class is not in an
    appropriate state for the requested operation.
    """
    pass
