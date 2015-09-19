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

from uber_rides.session import OAuth2Credential
from uber_rides.session import Session
from uber_rides.utils import auth
from uber_rides.utils import http


CLIENT_ID = 'clientID-28dh1'
CLIENT_SECRET = 'clientSecret-hv783s'
SERVER_TOKEN = 'serverToken-Y4lb2'
ACCESS_TOKEN = 'accessToken-34f21'
EXPIRES_IN_SECONDS = 3000
REFRESH_TOKEN = 'refreshToken-vsh91'
SCOPES_STRING = 'profile history'
SCOPES_SET = {'profile', 'history'}
REDIRECT_URL = 'https://developer.uber.com/my-redirect_url'


@fixture
def server_token_session():
    """Create a Session with Server Token."""
    return Session(
        server_token=SERVER_TOKEN,
    )


@fixture
def authorization_code_grant_session():
    """Create a Session from Auth Code Grant Credential."""
    oauth2credential = OAuth2Credential(
        client_id=None,
        redirect_url=None,
        access_token=ACCESS_TOKEN,
        expires_in_seconds=EXPIRES_IN_SECONDS,
        scopes=SCOPES_SET,
        grant_type=auth.AUTHORIZATION_CODE_GRANT,
        client_secret=None,
        refresh_token=REFRESH_TOKEN,
    )

    return Session(oauth2credential=oauth2credential)


@fixture
def implicit_grant_session():
    """Create a Session from Implicit Grant Credential."""
    oauth2credential = OAuth2Credential(
        client_id=None,
        redirect_url=None,
        access_token=ACCESS_TOKEN,
        expires_in_seconds=EXPIRES_IN_SECONDS,
        scopes=SCOPES_SET,
        grant_type=auth.IMPLICIT_GRANT,
        client_secret=None,
        refresh_token=None,
    )

    return Session(oauth2credential=oauth2credential)


@fixture
def client_credential_grant_session():
    """Create a Session from Client Credential Grant."""
    oauth2credential = OAuth2Credential(
        client_id=None,
        redirect_url=None,
        access_token=ACCESS_TOKEN,
        expires_in_seconds=EXPIRES_IN_SECONDS,
        scopes=SCOPES_SET,
        grant_type=auth.CLIENT_CREDENTIAL_GRANT,
        client_secret=None,
        refresh_token=None,
    )

    return Session(oauth2credential=oauth2credential)


@fixture
def authorization_code_response():
    """Response after Authorization Code Access Request."""

    mock_response = Mock(
        status_code=http.STATUS_OK,
    )

    response_json = {
        'access_token': ACCESS_TOKEN,
        'expires_in': EXPIRES_IN_SECONDS,
        'scope': SCOPES_STRING,
        'refresh_token': REFRESH_TOKEN,
    }

    mock_response.json = Mock(return_value=response_json)
    return mock_response


@fixture
def client_credentials_response():
    """Response after Client Credentials Access Request."""
    mock_response = Mock(
        status_code=http.STATUS_OK,
    )

    response_json = {
        'access_token': ACCESS_TOKEN,
        'expires_in': EXPIRES_IN_SECONDS,
        'scope': SCOPES_STRING,
    }

    mock_response.json = Mock(return_value=response_json)
    return mock_response


def test_server_token_session_initialized(server_token_session):
    """Confirm Session with Server Token initialized correctly."""
    assert server_token_session.server_token == SERVER_TOKEN
    assert server_token_session.token_type == auth.SERVER_TOKEN_TYPE
    assert server_token_session.oauth2credential is None


def test_oauth2_session_initialized(authorization_code_grant_session):
    """Confirm Session with OAuth2Credential initialized correctly."""
    assert authorization_code_grant_session.server_token is None
    assert authorization_code_grant_session.token_type == auth.OAUTH_TOKEN_TYPE
    oauth2 = authorization_code_grant_session.oauth2credential
    assert oauth2.access_token == ACCESS_TOKEN
    assert oauth2.scopes == SCOPES_SET
    assert oauth2.grant_type == auth.AUTHORIZATION_CODE_GRANT
    assert oauth2.refresh_token is REFRESH_TOKEN


def test_new_authorization_code_grant_session_is_not_stale(
    authorization_code_grant_session,
):
    """Confirm that a new Session from Auth Code Grant is not stale."""
    assert authorization_code_grant_session.server_token is None
    assert authorization_code_grant_session.oauth2credential
    assert authorization_code_grant_session.token_type == auth.OAUTH_TOKEN_TYPE
    assert not authorization_code_grant_session.oauth2credential.is_stale()


def test_new_implicit_grant_session_is_not_stale(implicit_grant_session):
    """Confirm that a new Session from Implicit Grant is not stale."""
    assert implicit_grant_session.server_token is None
    assert implicit_grant_session.oauth2credential
    assert implicit_grant_session.token_type == auth.OAUTH_TOKEN_TYPE
    assert not implicit_grant_session.oauth2credential.is_stale()


def test_new_client_credential_session_is_not_stale(
    client_credential_grant_session,
):
    """Confirm that a new Session from Client Credential Grant is not stale."""
    assert client_credential_grant_session.server_token is None
    assert client_credential_grant_session.oauth2credential
    assert client_credential_grant_session.token_type == auth.OAUTH_TOKEN_TYPE
    assert not client_credential_grant_session.oauth2credential.is_stale()


def test_old_authorization_code_grant_session_is_stale(
    authorization_code_grant_session
):
    """Confirm that an old Session from Auth Code Grant is stale."""
    authorization_code_grant_session.oauth2credential.expires_in_seconds = 1
    assert authorization_code_grant_session.oauth2credential.is_stale()


def test_old_implicit_grant_session_is_stale(implicit_grant_session):
    """Confirm that an old Session from Implicit Grant is stale."""
    implicit_grant_session.oauth2credential.expires_in_seconds = 1
    assert implicit_grant_session.oauth2credential.is_stale()


def test_old_client_credential_session_is_stale(
    client_credential_grant_session,
):
    """Confirm that an old Session from Client Credential Grant is stale."""
    client_credential_grant_session.oauth2credential.expires_in_seconds = 1
    assert client_credential_grant_session.oauth2credential.is_stale()


def test_make_session_from_authorization_code_response(
    authorization_code_response,
):
    """Test classmethod to build OAuth2Credential from HTTP Response."""
    oauth2credential = OAuth2Credential.make_from_response(
        response=authorization_code_response,
        grant_type=auth.AUTHORIZATION_CODE_GRANT,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_url=REDIRECT_URL,
    )

    assert oauth2credential.access_token == ACCESS_TOKEN
    assert oauth2credential.scopes == SCOPES_SET
    assert oauth2credential.grant_type == auth.AUTHORIZATION_CODE_GRANT
    assert oauth2credential.refresh_token == REFRESH_TOKEN
    assert oauth2credential.client_id == CLIENT_ID
    assert oauth2credential.client_secret == CLIENT_SECRET
    assert oauth2credential.redirect_url == REDIRECT_URL


def test_make_session_from_client_credentials_response(
    client_credentials_response,
):
    """Test classmethod to build OAuth2Credential from HTTP Response."""
    oauth2credential = OAuth2Credential.make_from_response(
        response=client_credentials_response,
        grant_type=auth.CLIENT_CREDENTIAL_GRANT,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )

    assert oauth2credential.access_token == ACCESS_TOKEN
    assert oauth2credential.scopes == SCOPES_SET
    assert oauth2credential.grant_type == auth.CLIENT_CREDENTIAL_GRANT
    assert oauth2credential.refresh_token is None
    assert oauth2credential.client_id == CLIENT_ID
    assert oauth2credential.client_secret == CLIENT_SECRET
    assert oauth2credential.redirect_url is None
