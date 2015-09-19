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
from pytest import raises
from urllib import quote
from urlparse import parse_qs
from urlparse import urlparse

from tests.vcr_config import uber_vcr
from uber_rides.auth import AuthorizationCodeGrant
from uber_rides.auth import ClientCredentialGrant
from uber_rides.auth import ImplicitGrant
from uber_rides.auth import refresh_access_token
from uber_rides.errors import UberIllegalState
from uber_rides.session import OAuth2Credential
from uber_rides.utils import auth


# replace these with valid tokens and credentials to rerecord fixtures
CLIENT_ID = 'clientID-28dh1'
CLIENT_SECRET = 'clientSecret-hv783s'
STATE_TOKEN = 'stateToken-se3jf'
AUTHORIZATION_CODE = 'authCode-3x734'
ACCESS_TOKEN = 'accessToken-194jd2'
REFRESH_TOKEN = 'refreshToken-14du3n'
REFRESHED_ACCESS_TOKEN = 'accessToken-34tns2'
REDIRECT_URL = 'https://developer.uber.com/my-redirect_url'

SCOPES = {'profile', 'history'}
EXPIRES_IN_SECONDS = 3000

EXPECTED_QUERYSTRING = (
    'scope={}&state={}&redirect_uri={}'
    '&response_type={}&client_id={}'
)


@fixture
def auth_code_grant():
    return AuthorizationCodeGrant(
        client_id=CLIENT_ID,
        scopes=SCOPES,
        client_secret=CLIENT_SECRET,
        redirect_url=REDIRECT_URL,
    )


@fixture
def auth_code_oauth2credential():
    return OAuth2Credential(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_url=REDIRECT_URL,
        access_token=ACCESS_TOKEN,
        expires_in_seconds=EXPIRES_IN_SECONDS,
        scopes=SCOPES,
        grant_type=auth.AUTHORIZATION_CODE_GRANT,
        refresh_token=REFRESH_TOKEN,
    )


@fixture
def implicit_grant():
    return ImplicitGrant(
        client_id=CLIENT_ID,
        scopes=SCOPES,
        redirect_url=REDIRECT_URL,
    )


@fixture
def implicit_oauth2credential():
    return OAuth2Credential(
        client_id=CLIENT_ID,
        client_secret=None,
        redirect_url=REDIRECT_URL,
        access_token=ACCESS_TOKEN,
        expires_in_seconds=EXPIRES_IN_SECONDS,
        scopes=SCOPES,
        grant_type=auth.IMPLICIT_GRANT,
        refresh_token=None,
    )


@fixture
def client_credential_grant():
    return ClientCredentialGrant(
        client_id=CLIENT_ID,
        scopes=SCOPES,
        client_secret=CLIENT_SECRET,
    )


@fixture
def client_credential_oauth2credential():
    return OAuth2Credential(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_url=None,
        access_token=ACCESS_TOKEN,
        expires_in_seconds=EXPIRES_IN_SECONDS,
        scopes=SCOPES,
        grant_type=auth.CLIENT_CREDENTIAL_GRANT,
        refresh_token=None,
    )


def test_auth_code_grant_get_authorization_url(auth_code_grant):
    """Test to get authorization url for authorization code grant."""
    url = auth_code_grant.get_authorization_url()
    parsed_url = urlparse(url)
    assert parsed_url.netloc == auth.AUTH_HOST
    assert parsed_url.path.strip('/') == auth.AUTHORIZE_PATH

    querystring = parsed_url.query
    queryparams = parse_qs(querystring)
    expected_query = EXPECTED_QUERYSTRING.format(
        '+'.join(SCOPES),
        auth_code_grant.state_token,
        quote(REDIRECT_URL, safe=''),
        auth.CODE_RESPONSE_TYPE,
        CLIENT_ID,
    )

    assert expected_query in querystring
    assert queryparams.get('scope')[0] == ' '.join(SCOPES)
    assert queryparams.get('redirect_uri')[0] == REDIRECT_URL
    assert queryparams.get('response_type')[0] == auth.CODE_RESPONSE_TYPE
    assert queryparams.get('client_id')[0] == CLIENT_ID
    assert queryparams.get('state')[0] == auth_code_grant.state_token


@uber_vcr.use_cassette()
def test_auth_code_get_session(auth_code_grant):
    """Test to get OAuth 2.0 session for authorization code grant."""
    auth_code_grant.state_token = STATE_TOKEN
    redirect_url = '{}?state={}&code={}'
    redirect_url = redirect_url.format(
        REDIRECT_URL,
        STATE_TOKEN,
        AUTHORIZATION_CODE,
    )
    session = auth_code_grant.get_session(redirect_url)

    assert session.server_token is None
    assert session.token_type == auth.OAUTH_TOKEN_TYPE
    credential = session.oauth2credential
    assert credential.access_token == ACCESS_TOKEN
    assert credential.refresh_token == REFRESH_TOKEN
    assert credential.scopes == SCOPES
    assert credential.grant_type == auth.AUTHORIZATION_CODE_GRANT
    assert credential.client_id == CLIENT_ID
    assert credential.client_secret == CLIENT_SECRET
    assert credential.redirect_url == REDIRECT_URL


@uber_vcr.use_cassette()
def test_refresh_auth_code_access_token(auth_code_oauth2credential):
    """Test to refresh OAuth 2.0 session for authorization code grant."""
    session = refresh_access_token(auth_code_oauth2credential)

    assert session.server_token is None
    assert session.token_type == auth.OAUTH_TOKEN_TYPE
    credential = session.oauth2credential
    assert credential.access_token == REFRESHED_ACCESS_TOKEN
    assert credential.refresh_token
    assert credential.scopes == SCOPES
    assert credential.grant_type == auth.AUTHORIZATION_CODE_GRANT
    assert credential.client_id == CLIENT_ID
    assert credential.client_secret == CLIENT_SECRET
    assert credential.redirect_url == REDIRECT_URL


def test_implicit_grant_get_authorization_url(implicit_grant):
    """Test to get authorization url for implicit grant."""
    url = implicit_grant.get_authorization_url()
    parsed_url = urlparse(url)
    assert parsed_url.netloc == auth.AUTH_HOST
    assert parsed_url.path.strip('/') == auth.AUTHORIZE_PATH

    querystring = parsed_url.query
    queryparams = parse_qs(querystring)
    expected_query = EXPECTED_QUERYSTRING.format(
        '+'.join(SCOPES),
        None,
        quote(REDIRECT_URL, safe=''),
        auth.TOKEN_RESPONSE_TYPE,
        CLIENT_ID,
    )

    assert expected_query in querystring
    assert queryparams.get('scope')[0] == ' '.join(SCOPES)
    assert queryparams.get('redirect_uri')[0] == REDIRECT_URL
    assert queryparams.get('response_type')[0] == auth.TOKEN_RESPONSE_TYPE
    assert queryparams.get('client_id')[0] == CLIENT_ID


def test_implicit_grant_get_session(implicit_grant):
    """Test to get OAuth 2.0 session from URL for implicit grant."""
    redirect_url = (
        '{}#access_token={}&token_type=Bearer&state=None'
        '&expires_in=2592000&scope=profile+history'
    )
    redirect_url = redirect_url.format(REDIRECT_URL, ACCESS_TOKEN)
    session = implicit_grant.get_session(redirect_url)

    assert session.server_token is None
    assert session.token_type == auth.OAUTH_TOKEN_TYPE
    credential = session.oauth2credential
    assert credential.access_token == ACCESS_TOKEN
    assert credential.scopes == SCOPES
    assert credential.grant_type == auth.IMPLICIT_GRANT
    assert credential.client_id == CLIENT_ID
    assert credential.redirect_url == REDIRECT_URL
    assert credential.client_secret is None
    assert credential.refresh_token is None


def test_refresh_implicit_access_token(implicit_oauth2credential):
    """Test that refreshing credentials for implicit grant raises error."""
    with raises(UberIllegalState) as error:
        refresh_access_token(implicit_oauth2credential)

    assert 'Grant Type does not support Refresh Tokens' in error.value[0]


@uber_vcr.use_cassette()
def test_client_credential_get_session(client_credential_grant):
    """Test to get OAuth 2.0 session for client credential grant."""
    session = client_credential_grant.get_session()

    assert session.server_token is None
    assert session.token_type == auth.OAUTH_TOKEN_TYPE
    credential = session.oauth2credential
    assert credential.access_token == ACCESS_TOKEN
    assert credential.scopes == SCOPES
    assert credential.grant_type == auth.CLIENT_CREDENTIAL_GRANT
    assert credential.client_id == CLIENT_ID
    assert credential.client_secret == CLIENT_SECRET
    assert credential.refresh_token is None
    assert credential.redirect_url is None


@uber_vcr.use_cassette()
def test_refresh_client_credential_access_token(
    client_credential_oauth2credential,
):
    """Test to refresh OAuth 2.0 session for client credential grant."""
    session = refresh_access_token(client_credential_oauth2credential)

    assert session.server_token is None
    assert session.token_type == auth.OAUTH_TOKEN_TYPE
    credential = session.oauth2credential
    assert credential.access_token == REFRESHED_ACCESS_TOKEN
    assert credential.scopes == SCOPES
    assert credential.grant_type == auth.CLIENT_CREDENTIAL_GRANT
    assert credential.client_id == CLIENT_ID
    assert credential.client_secret == CLIENT_SECRET
    assert credential.redirect_url is None
    assert credential.refresh_token is None
