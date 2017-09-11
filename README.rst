*********************
Uber Rides Python SDK
*********************

Python SDK (beta) to support the `Uber Rides API <https://developer.uber.com/>`_.

Installation
------------

To use the Uber Rides Python SDK:

.. code-block:: bash

    $ pip install uber_rides


Head over to `pip-installer <https://pip.pypa.io/en/latest/installing/>`_ for instructions on installing pip.

To run from source, you can `download the source code <https://github.com/uber/rides-python-sdk/archive/master.zip>`_ for uber-rides, and then run:

.. code-block:: bash

    $ python setup.py install


We recommend using `virtualenv <http://www.virtualenv.org/>`_ when setting up your project environment. You may need to run the above commands with `sudo` if you’re not using it.

Read-Only Use
-------------

If you just need read-only access to Uber API resources, like getting a location’s available products, create a Session with the server token you received after `registering your app <https://developer.uber.com/dashboard>`_.

.. code-block:: python

    from uber_rides.session import Session
    session = Session(server_token=YOUR_SERVER_TOKEN)

Use this Session to create an UberRidesClient and fetch API resources:

.. code-block:: python

    from uber_rides.client import UberRidesClient
    client = UberRidesClient(session)
    response = client.get_products(37.77, -122.41)
    products = response.json.get('products')

Authorization
-------------

If you need to access protected resources or modify resources (like getting a user’s ride history or requesting a ride), you will need the user to grant access to your application through the OAuth 2.0 Authorization Code flow. See `Uber API docs <https://developer.uber.com/docs/ride-requests/guides/authentication/introduction>`_.

The Authorization Code flow is a two-step authorization process. The first step is having the user authorize your app and the second involves requesting an OAuth 2.0 access token from Uber. This process is mandatory if you want to take actions on behalf of a user or access their information.

.. code-block:: python

    from uber_rides.auth import AuthorizationCodeGrant
    auth_flow = AuthorizationCodeGrant(
        YOUR_CLIENT_ID,
        YOUR_PERMISSION_SCOPES,
        YOUR_CLIENT_SECRET,
        YOUR_REDIRECT_URL,
    )
    auth_url = auth_flow.get_authorization_url()

You can find `YOUR_CLIENT_ID` and `YOUR_CLIENT_SECRET` in the `developer dashboard <https://developer.uber.com/dashboard/>`_ under the settings tab of your application.  `YOUR_PERMISSION_SCOPES` is the `list of scopes <https://developer.uber.com/docs/ride-requests/guides/scopes>`_ you have requested in the authorizations tab. Note that `YOUR_REDIRECT_URL` must match the value you provided when you registered your application.

Navigate the user to the `auth_url` where they can grant access to your application. After, they will be redirected to a `redirect_url` with the format YOUR_REDIRECT_URL?code=UNIQUE_AUTH_CODE. Use this `redirect_url` to create a session and start UberRidesClient.

.. code-block:: python

    session = auth_flow.get_session(redirect_url)
    client = UberRidesClient(session)
    credentials = session.oauth2credential

Keep `credentials` information in a secure data store and reuse them to make API calls on behalf of your user. The SDK will handle the token refresh for you automatically when it makes API requests with an UberRidesClient.


Example Apps
------------

Navigate to the `example` folder to access the python example apps. Before you can run an example, you must edit the `example/config.*.yaml` file and add your app credentials from the Uber developer dashboard.

To get an UberRidesClient through the Authorization Code flow, run:

.. code-block:: bash

    $ python example/authorize_rider.py

The example above stores user credentials in `example/oauth2_rider_session_store.yaml`. To create an UberRidesClient with these credentials and go through a surge ride request run:

.. code-block:: bash

    $ python example/request_ride.py

---

To get an UberRidesClient authorized for driver endpoints, run:


.. code-block:: bash

    $ python example/authorize_driver.py

The example above stores user credentials in `example/oauth2_driver_session_store.yaml`.


Flask Demo Apps
"""""""""""""""

To get an understanding of how the sdk can be use in an example app see the flask examples for rider and driver dashboards:

.. code-block:: bash

    $ pip install flask


.. code-block:: bash

    $ python example/rider_dashboard.py


.. code-block:: bash

    $ python example/driver_dashboard.py


Get Available Products
""""""""""""""""""""""

.. code-block:: python

    response = client.get_products(37.77, -122.41)
    products = response.json.get('products')
    product_id = products[0].get('product_id')

Get Price Estimates
"""""""""""""""""""

.. code-block:: python

    response = client.get_price_estimates(
        start_latitude=37.770,
        start_longitude=-122.411,
        end_latitude=37.791,
        end_longitude=-122.405,
        seat_count=2
    )

    estimate = response.json.get('prices')

Get Rider Profile
"""""""""""""""""

.. code-block:: python

    response = client.get_rider_profile()
    profile = response.json

    first_name = profile.get('first_name')
    last_name = profile.get('last_name')
    email = profile.get('email')

Get User History
""""""""""""""""

.. code-block:: python

    response = client.get_user_activity()
    history = response.json

Request a Ride
""""""""""""""

.. code-block:: python

    # Get products for location
    response = client.get_products(37.77, -122.41)
    products = response.json.get('products')

    product_id = products[0].get('product_id')

    # Get upfront fare for product with start/end location
    estimate = client.estimate_ride(
        product_id=product_id,
        start_latitude=37.77,
        start_longitude=-122.41,
        end_latitude=37.79,
        end_longitude=-122.41,
        seat_count=2
    )
    fare = estimate.json.get('fare')

    # Request ride with upfront fare for product with start/end location
    response = client.request_ride(
        product_id=product_id,
        start_latitude=37.77,
        start_longitude=-122.41,
        end_latitude=37.79,
        end_longitude=-122.41,
        seat_count=2,
        fare_id=fare['fare_id']
    )

    request = response.json
    request_id = request.get('request_id')

    # Request ride details from request_id
    response = client.get_ride_details(request_id)
    ride = response.json

    # Cancel a ride
    response = client.cancel_ride(request_id)
    ride = response.json


This makes a real-world request and send an Uber driver to the specified start location.

To develop and test against request endpoints in a sandbox environment, make sure to instantiate your UberRidesClient with

.. code-block:: python

    client = UberRidesClient(session, sandbox_mode=True)


The default for `sandbox_mode` is set to `False`. See our `documentation <https://developer.uber.com/docs/ride-requests/guides/sandbox>`_ to read more about using the Sandbox Environment.

Update Sandbox Ride
"""""""""""""""""""

If you are requesting sandbox rides, you will need to step through the different states of a ride.

.. code-block:: python

    response = client.update_sandbox_ride(ride_id, 'accepted')
    response = client.update_sandbox_ride(ride_id, 'in_progress')


If the update is successful, `response.status_code` will be 204.

The `update_sandbox_ride` method is not valid in normal mode, where the ride status will change automatically.

Get Driver Profile
""""""""""""""""""

.. code-block:: python

    response = client.get_driver_profile()
    profile = response.json

    first_name = profile.get('first_name')
    last_name = profile.get('last_name')
    email = profile.get('email')


Get Driver Trips
""""""""""""""""

.. code-block:: python

    response = client.get_driver_trips()
    trips = response.json


Get Driver Payments
"""""""""""""""""""

.. code-block:: python

    response = client.get_driver_payments()
    payments = response.json


Get Uber for Business Receipts
""""""""""""""""""""""""""""""

.. code-block:: python

    from uber_rides.auth import ClientCredentialGrant
    from uber_rides.client import UberRidesClient

    auth_flow = ClientCredentialGrant(
    <CLIENT_ID>,
    <SCOPES>,
    <CLIENT_SECRET>
    )
    session = auth_flow.get_session()

    client = UberRidesClient(session)
    receipt = client.get_business_trip_receipt('2a2f3da4-asdad-ds-12313asd')
    pdf_url = client.get_business_trip_receipt_pdf_url('2a2f3da4-asdad-ds-12313asd')


Getting help
------------

Uber developers actively monitor the `Uber Tag <http://stackoverflow.com/questions/tagged/uber-api>`_ on StackOverflow. If you need help installing or using the library, you can ask a question there. Make sure to tag your question with `uber-api` and `python`!

For full documentation about our API, visit our `Developer Site <https://developer.uber.com/>`_.

See the `Getting Started Tutorial <https://developer.uber.com/docs/riders/ride-requests/tutorials/api/python>`_.


Contributing
------------

We love contributions. If you've found a bug in the library or would like new features added, go ahead and open issues or pull requests against this repo. Write a test to show your bug was fixed or the feature works as expected.
