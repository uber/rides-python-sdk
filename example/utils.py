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

"""General utilities for command line examples."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple
from yaml import safe_load


# set your app credentials here
CREDENTIALS_FILENAME = 'example/config.yaml'

# where your OAuth 2.0 credentials are stored
STORAGE_FILENAME = 'example/oauth2_session_store.yaml'

DEFAULT_CONFIG_VALUES = frozenset([
    'INSERT_CLIENT_ID_HERE',
    'INSERT_CLIENT_SECRET_HERE',
    'INSERT_REDIRECT_URL_HERE',
])

Colors = namedtuple('Colors', 'response, success, fail, end')
COLORS = Colors(
    response='\033[94m',
    success='\033[92m',
    fail='\033[91m',
    end='\033[0m',
)


def success_print(message):
    """Print a message in green text.

    Parameters
        message (str)
            Message to print.
    """
    print(COLORS.success, message, COLORS.end)


def response_print(message):
    """Print a message in blue text.

    Parameters
        message (str)
            Message to print.
    """
    print(COLORS.response, message, COLORS.end)


def fail_print(message):
    """Print a message in red text.

    Parameters
        message (str)
            Message to print.
    """
    print(COLORS.fail, message, COLORS.end)


def paragraph_print(message):
    """Print message with padded newlines.

    Parameters
        message (str)
            Message to print.
    """
    paragraph = '\n{}\n'
    print(paragraph.format(message))


def import_app_credentials(filename=CREDENTIALS_FILENAME):
    """Import app credentials from configuration file.

    Parameters
        filename (str)
            Name of configuration file.

    Returns
        credentials (dict)
            All your app credentials and information
            imported from the configuration file.
    """
    with open(filename, 'r') as config_file:
        config = safe_load(config_file)

    client_id = config['client_id']
    client_secret = config['client_secret']
    redirect_url = config['redirect_url']

    config_values = [client_id, client_secret, redirect_url]

    for value in config_values:
        if value in DEFAULT_CONFIG_VALUES:
            exit('Missing credentials in {}'.format(filename))

    credentials = {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_url': redirect_url,
        'scopes': set(config['scopes']),
    }

    return credentials


def import_oauth2_credentials(filename=STORAGE_FILENAME):
    """Import OAuth 2.0 session credentials from storage file.

    Parameters
        filename (str)
            Name of storage file.

    Returns
        credentials (dict)
            All your app credentials and information
            imported from the configuration file.
    """
    with open(filename, 'r') as storage_file:
        storage = safe_load(storage_file)

    # depending on OAuth 2.0 grant_type, these values may not exist
    client_secret = storage.get('client_secret')
    redirect_url = storage.get('redirect_url')
    refresh_token = storage.get('refresh_token')

    credentials = {
        'access_token': storage['access_token'],
        'client_id': storage['client_id'],
        'client_secret': client_secret,
        'expires_in_seconds': storage['expires_in_seconds'],
        'grant_type': storage['grant_type'],
        'redirect_url': redirect_url,
        'refresh_token': refresh_token,
        'scopes': storage['scopes'],
    }

    return credentials
