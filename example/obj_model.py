from uber_rides.errors import ClientError, ServerError
from utils import paragraph_print, fail_print, success_print
from request_surge_ride import create_uber_client, PRODUCT_ID, START_LAT, START_LNG, END_LAT, END_LNG
from uber_rides.session import Session
from uber_rides.client import UberRidesClient

SERVER_TOKEN = INSERT_SERVER_TOKEN_HERE

def estimate_ride(api_client):
    """Use an UberRidesClient to fetch a ride estimate and print the results.

    Parameters
        api_client (UberRidesClient)
            An authorized UberRidesClient to access API resources.
    """
    try:
        estimate = api_client.estimate_ride(
            PRODUCT_ID,
            START_LAT,
            START_LNG,
            END_LAT,
            END_LNG,
        )

    except (ClientError, ServerError), error:
        fail_print(error)

    else:
        return estimate


if __name__ == '__main__':
    """Run the example.

    Create an UberRidesClient from OAuth 2.0 Credentials,
    and then uses Object Model
    """
    session = Session(server_token=SERVER_TOKEN)
    print session
    api_client = UberRidesClient(session, sandbox_mode=True)

    est = api_client.get_pickup_time_estimates(START_LAT, START_LNG)
    paragraph_print(est) #Notice I can just print this out now

    #For now, I have to call the 'uber_obj' in the response... its easy enough to make this the object itself and add
    #in the other attributes, but wanted to see what you guys wanted to do first as an object is almost always preferable to work
    #with

    paragraph_print(est.uber_obj.times)

    for i in est.uber_obj.times: #again, could just be est.prices
        paragraph_print(i)
