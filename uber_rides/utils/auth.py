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

SERVER_TOKEN_TYPE = 'Token'
OAUTH_TOKEN_TYPE = 'Bearer'
AUTHORIZATION_CODE_GRANT = 'authorization_code'
CLIENT_CREDENTIAL_GRANT = 'client_credentials'
IMPLICIT_GRANT = 'implicit'
REFRESH_TOKEN = 'refresh_token'
AUTH_HOST = 'login.uber.com'
ACCESS_TOKEN_PATH = 'oauth/token'
AUTHORIZE_PATH = 'oauth/authorize'
REVOKE_PATH = 'oauth/revoke'
CODE_RESPONSE_TYPE = 'code'
TOKEN_RESPONSE_TYPE = 'token'
VALID_RESPONSE_TYPES = frozenset([
    CODE_RESPONSE_TYPE,
    TOKEN_RESPONSE_TYPE,
])
