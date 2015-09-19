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

from requests import codes
from time import time

from uber_rides.errors import ClientError
from uber_rides.errors import UberIllegalState
from uber_rides.utils import auth


EXPIRES_THRESHOLD_SECONDS = 500


class Session(object):
    """A class to store credentials.

    A Session can be initialized with a Server Token or with a set of
    OAuth 2.0 Credentials, but not with both. A Session uses credentials
    to properly construct requests to Uber and access protected resources.
    """

    def __init__(
        self,
        server_token=None,
        oauth2credential=None,
    ):
        """Initialize a Session.

        Parameters
            sever_token (str)
                Your application's server token. Available at
                developer.uber.com.
            oauth2credential (OAuth2Credential)
                Access token and additional OAuth 2.0 credentials used
                to access protected resources.

        Raises
            UberIllegalState (APIError)
                Raised if there is an attempt to create session with
                both server token and access token.
        """
        if server_token and oauth2credential:
            message = (
                'Session cannot have both Server '
                'and OAuth 2.0 Credentials.'
            )
            raise UberIllegalState(message)

        if server_token is None and oauth2credential is None:
            message = (
                'Session must have either Server '
                'Token or OAuth 2.0 Credentials.'
            )
            raise UberIllegalState(message)

        if server_token:
            self.server_token = server_token
            self.token_type = auth.SERVER_TOKEN_TYPE
            self.oauth2credential = None

        elif oauth2credential:
            self.oauth2credential = oauth2credential
            self.token_type = auth.OAUTH_TOKEN_TYPE
            self.server_token = None


class OAuth2Credential(object):
    """A class to store OAuth 2.0 credentials.

    OAuth 2.0 credentials are used to properly construct requests
    to Uber and access protected resources. The class also stores
    app information (such as client_id) to refresh or request new
    access tokens if they expire or are revoked.
    """

    def __init__(
        self,
        client_id,
        access_token,
        expires_in_seconds,
        scopes,
        grant_type,
        redirect_url=None,
        client_secret=None,
        refresh_token=None,
    ):
        """Initialize an OAuth2Credential.

        Parameters
            client_id (str)
                Your app's Client ID.
            access_token (str)
                Access token received from OAuth 2.0 Authorization.
            expires_in_seconds (int)
                Seconds after initial grant when access token will expire.
            scopes (set)
                Set of permission scopes to request.
                (e.g. {'profile', 'history'}) Keep this list minimal so
                users feel safe granting your app access to their information.
            grant_type (str)
                Type of OAuth 2.0 Grant used to obtain access token.
                (e.g. 'authorization_code')
            redirect_url (str)
                The URL that the Uber server will redirect to.
            client_secret (str)
                Your app's Client Secret.
            refresh_token (str)
                Optional refresh token used to get a new access token.
                Only used for Authorization Code Grant.
        """
        self.client_id = client_id
        self.access_token = access_token
        self.expires_in_seconds = self._now() + int(expires_in_seconds)
        self.scopes = scopes
        self.grant_type = grant_type
        self.redirect_url = redirect_url
        self.client_secret = client_secret
        self.refresh_token = refresh_token

    @classmethod
    def make_from_response(
        cls,
        response,
        grant_type,
        client_id,
        client_secret=None,
        redirect_url=None,
    ):
        """Alternate constructor for OAuth2Credential().

        Create an OAuth2Credential from an HTTP Response.

        Parameters
            response (Response)
                HTTP Response containing OAuth 2.0 credentials.
            grant_type (str)
                Type of OAuth 2.0 Grant used to obtain access token.
                (e.g. 'authorization_code')
            client_id (str)
                Your app's Client ID.
            client_secret (str)
                Your app's Client Secret.
            redirect_url (str)
                The URL that the Uber server will redirect to.

        Returns
            (OAuth2Credential)

        Raises
            ClientError (APIError)
                Raised if the response is invalid.
        """
        if response.status_code != codes.ok:
            message = 'Error with Access Token Request: {}'
            message = message.format(response.reason)
            raise ClientError(response, message)

        response = response.json()

        # convert space delimited string to set
        scopes = response.get('scope')
        scopes_set = {scope for scope in scopes.split()}

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            redirect_url=redirect_url,
            access_token=response.get('access_token'),
            expires_in_seconds=response.get('expires_in'),
            scopes=scopes_set,
            grant_type=grant_type,
            refresh_token=response.get('refresh_token', None),
        )

    def is_stale(self):
        """Check whether the session's current access token is about to expire.

        Returns
            (bool)
                True if access_token expires within threshold
        """
        expires_in_seconds = self.expires_in_seconds - self._now()
        return expires_in_seconds < EXPIRES_THRESHOLD_SECONDS

    def _now(self):
        return int(time())
