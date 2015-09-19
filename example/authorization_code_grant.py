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

"""Initializes an UberRidesClient with OAuth 2.0 Credentials.

This example demonstrates how to get an access token through the
OAuth 2.0 Authorization Code Grant and use credentials to create
an UberRidesClient.

To run this example:

    (1) Set your app credentials in config.yaml
    (2) Run `python authorization_code_grant.py`
    (3) A success message will print, 'Hello {YOUR_NAME}'
    (4) User OAuth 2.0 credentials are recorded in
        'oauth2_session_store.yaml'
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from yaml import safe_dump

from example import utils
from example.utils import fail_print
from example.utils import response_print
from example.utils import success_print
from example.utils import import_app_credentials

from uber_rides.auth import AuthorizationCodeGrant
from uber_rides.client import UberRidesClient
from uber_rides.errors import ClientError
from uber_rides.errors import ServerError
from uber_rides.errors import UberIllegalState


def authorization_code_grant_flow(credentials, storage_filename):
    """Get an access token through Authorization Code Grant.

    Parameters
        credentials (dict)
            All your app credentials and information
            imported from the configuration file.
        storage_filename (str)
            Filename to store OAuth 2.0 Credentials.

    Returns
        (UberRidesClient)
            An UberRidesClient with OAuth 2.0 Credentials.
    """
    auth_flow = AuthorizationCodeGrant(
        credentials.get('client_id'),
        credentials.get('scopes'),
        credentials.get('client_secret'),
        credentials.get('redirect_url'),
    )

    auth_url = auth_flow.get_authorization_url()
    login_message = 'Login and grant access by going to:\n{}\n'
    login_message = login_message.format(auth_url)
    response_print(login_message)

    redirect_url = 'Copy the URL you are redirected to and paste here: \n'
    result = raw_input(redirect_url).strip()

    try:
        session = auth_flow.get_session(result)

    except (ClientError, UberIllegalState), error:
        fail_print(error)
        return

    credential = session.oauth2credential

    credential_data = {
        'client_id': credential.client_id,
        'redirect_url': credential.redirect_url,
        'access_token': credential.access_token,
        'expires_in_seconds': credential.expires_in_seconds,
        'scopes': list(credential.scopes),
        'grant_type': credential.grant_type,
        'client_secret': credential.client_secret,
        'refresh_token': credential.refresh_token,
    }

    with open(storage_filename, 'w') as yaml_file:
        yaml_file.write(safe_dump(credential_data, default_flow_style=False))

    return UberRidesClient(session, sandbox_mode=True)


def hello_user(api_client):
    """Use an authorized client to fetch and print profile information.

    Parameters
        api_client (UberRidesClient)
            An UberRidesClient with OAuth 2.0 credentials.
    """

    try:
        response = api_client.get_user_profile()

    except (ClientError, ServerError), error:
        fail_print(error)
        return

    else:
        profile = response.json
        first_name = profile.get('first_name')
        email = profile.get('email')
        message = 'Hello, {}. Successfully granted access token to {}.'
        message = message.format(first_name, email)
        success_print(message)


if __name__ == '__main__':
    """Run the example.

    Get an access token through the OAuth 2.0 Authorization Code Grant
    and use credentials to create an UberRidesClient.
    """
    credentials = import_app_credentials()

    api_client = authorization_code_grant_flow(
        credentials,
        utils.STORAGE_FILENAME,
    )

    hello_user(api_client)
