*********************
Uber Rides Python SDK
*********************

Python SDK (beta) to support the `Uber Rides API <https://developer.uber.com/>`_.

Installation
------------

To use the Uber Rides Python SDK:

.. code-block:: bash

    $ pip install uber_rides


Head over to `pip-installer <http://www.pip-installer.org/en/latest/index.html>`_ for instructions on installing pip.

To run from source, you can `download the source code <https://github.com/uber/rides-python-sdk/archive/master.zip>`_ for uber-rides, and then run:

.. code-block:: bash

    $ python setup.py install


We recommend using `virtualenv <http://www.virtualenv.org/>`_ when setting up your project environment. You may need to run the above commands with `sudo` if you’re not using it.

Read-Only Use
-------------

If you just need read-only access to Uber API resources, like getting a location’s available products, create a Session with the server token you received after `registering your app <https://developer.uber.com/dashboard>`_.

.. code-block::

    from uber_rides.session import Session
    session = Session(server_token=YOUR_SERVER_TOKEN)

Use this Session to create an UberRidesClient and fetch API resources:

.. code-block::

    from uber_rides.client import UberRidesClient
    client = UberRidesClient(session)
    response = client.get_products(37.77, -122.41)
    products = response.json.get('products')

Authorization
-------------

If you need to access protected resources or modify resources (like getting a user’s ride history or requesting a ride), you will need the user to grant access to your application through the OAuth 2.0 Authorization Code flow. See `Uber API docs <https://developer.uber.com/docs/authentication>`_. 

The Authorization Code flow is a two-step authorization process. The first step is having the user authorize your app and the second involves requesting an OAuth 2.0 access token from Uber. This process is mandatory if you want to take actions on behalf of a user or access their information.

.. code-block::

    from uber_rides.auth import AuthorizationCodeGrant
    auth_flow = AuthorizationCodeGrant(
        YOUR_CLIENT_ID,
        YOUR_PERMISSION_SCOPES,
        YOUR_CLIENT_SECRET,
        YOUR_REDIRECT_URL,
    )
    auth_url = auth_flow.get_authorization_url()

Note that `YOUR_REDIRECT_URL` must match the value you provided when you registered your application. 

Navigate the user to the `auth_url` where they can grant access to your application. After, they will be redirected to a `redirect_url` with the format YOUR_REDIRECT_URL?code=UNIQUE_AUTH_CODE. Use this `redirect_url` to create a session and start UberRidesClient.

.. code-block::

    session = auth_flow.get_session(redirect_url)
    client = UberRidesClient(session)
    credentials = session.oauth2credential

Keep `credentials` information in a secure data store and reuse them to make API calls on behalf of your user. The SDK will handle the token refresh for you automatically when it makes API requests with an UberRidesClient.


Example Usage
-------------

Navigate to the `example` folder to access the python scripts examples.  Before you can run an example, you must edit the `example/config.yaml` file and add your app credentials.

To get an UberRidesClient through the Authorization Code flow, run:

.. code-block:: bash

    $ python example/authorization_code_grant.py

The example above stores user credentials in `example/oauth2_session_store.yaml`. To create an UberRidesClient with these credentials and go through a surge ride request run:

.. code-block:: bash

    $ python example/request_surge_ride.py

Get Available Products
""""""""""""""""""""""

.. code-block::

    response = client.get_products(37.77, -122.41)
    products = response.json.get('products')
    product_id = products[0].get('product_id')

Request a Ride
""""""""""""""

.. code-block::

    response = client.request_ride(
        product_id=product_id,
        start_latitude=37.77,
        start_longitude=-122.41,
        end_latitude=37.79,
        end_longitude=-122.41,
    )
    ride_details = response.json
    ride_id = ride_details.get('request_id')


This makes a real-world request and send an Uber driver to the specified start location.

To develop and test against request endpoints in a sandbox environment, make sure to instantiate your UberRidesClient with

.. code-block::

    client = UberRidesClient(session, sandbox_mode=True)


The default for `sandbox_mode` is set to `False`. See our `documentation <https://developer.uber.com/docs/sandbox>`_ to read more about using the Sandbox Environment.

Update Sandbox Ride
"""""""""""""""""""

If you are requesting sandbox rides, you will need to step through the different states of a ride.

.. code-block::

    response = client.update_sandbox_ride(ride_id, 'accepted')


If the update is successful, `response.status_code` will be 204.

The `update_sandbox_ride` method is not valid in normal mode, where the ride status will change automatically.

Getting help
------------

Uber developers actively monitor the `Uber Tag <http://stackoverflow.com/questions/tagged/uber-api>`_ on StackOverflow. If you need help installing or using the library, you can ask a question there. Make sure to tag your question with `uber-api` and `python`!

For full documentation about our API, visit our `Developer Site <https://developer.uber.com/>`_.

Contributing
------------

We love contributions. If you've found a bug in the library or would like new features added, go ahead and open issues or pull requests against this repo. Write a test to show your bug was fixed or the feature works as expected.
