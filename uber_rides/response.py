# Copyright (c) 2015 MF Genius, LLC.
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
import pprint

GET = "GET"
PUT = "PUT"
PATCH = "PATCH"
DELETE = "DELETE"
POST = "POST"


class SubclassTracker(type):
    def __init__(cls, name, bases, dct):
        if not hasattr(cls, '_registry'):
            cls._registry = {}
        if not hasattr(cls, '_endpoints'):
            cls._endpoints = {}

        if dct.get("_uber_name"):
            if cls._registry.get(dct["_uber_name"]) is not None:
                raise Exception("Uber Class Name already claimed".format(dct["_uber_name"]))
            cls._registry.update({dct["_uber_name"]: cls})

        if dct.get("_endpoint"):
            endpoint = "v{0}/{1}".format(dct["_version"], dct["_endpoint"])
            endpoints = ["{1}:{0}".format(endpoint, i) for i in dct["_methods"]]
            for i in endpoints:
                if cls._endpoints.get(i) is not None:
                    raise Exception("Uber Endpoint already claimed: {0}".format(i))
                cls._endpoints.update({endpoint: i})


        super(SubclassTracker, cls).__init__(name, bases, dct)

class BaseUber(object):
    __metaclass__ = SubclassTracker
    _objects = []
    _keys = []


    def __init__(self, dictionary):
        assert isinstance(dictionary, dict)
        self._object_names = [i._uber_name for i in self._objects]
        for k, v in dictionary.iteritems():
            if k in self._keys:
                setattr(self, k, v)
                continue
            if k in self._object_names:
                if isinstance(v, list):
                    for i in v:
                        if hasattr(self, k):
                            getattr(self, k).append(self._get_object(k, i))
                        else:
                            setattr(self, k, [self._get_object(k, i)])
                elif v is None:
                    setattr(self, k, v)
                else:
                    setattr(self, k, self._get_object(k, v))

    def _get_object(self, key, json):
        obj = None
        for i in self._objects:
            if key == i._uber_name:
                return i(json)

    def __repr__(self):
        return pprint.pformat(self.__dict__())

    def __dict__(self):
        out = {}
        for i in self._keys:
            out.update({i: getattr(self, i, None)})
        for i in self._objects:
            out.update({i._uber_name: getattr(self, i._uber_name, None)})
        return out

    def serialize(self):
        return self.__dict__()

class BaseUberClass(BaseUber):
    _uber_name = None

class ServiceFeesObj(BaseUberClass):
    _uber_name = "service_fees"
    _keys = ["fee", "name"]

class PriceDetailsObj(BaseUberClass):
    _uber_name = "price_details"
    _keys = ["distance_unit", "cost_per_minute", "minimum", "cost_per_distance", "base", "cancellation_fee", "currency_code"]
    _objects = [ServiceFeesObj]

class ProductIDObj(BaseUberClass):
    _uber_name = "products"
    _keys = ["capacity", "description", "image", "display_name", "product_id"]
    _objects = [PriceDetailsObj]

class PricesObj(BaseUberClass):
    _uber_name = "prices"
    _keys = ["product_id", "currency_code", "display_name", "estimate", "low_estimate", "high_estimate", "surge_multiplier", "duration", "distance"]

class TimesObj(BaseUberClass):
    _uber_name = "times"
    _keys = ["product_id", "display_name", "estimate"]

class StartCityObj(BaseUberClass):
    _uber_name = "start_city"
    _keys = ["latitude", "display_name", "longitude"]

class HistoryObj_V1_2(BaseUberClass):
    _uber_name = "history_v1.2"
    _keys = ["status", "distance", "request_time", "start_time", "end_time", "request_id", "product_id"]
    _objects = [StartCityObj]

class HistoryObj_V1_1(BaseUberClass):
    _uber_name = "history_v1.1"
    _keys = ["uuid", "request_time", "product_id", "status", "distance", "start_time", "end_time"]

class DriverObj(BaseUberClass):
    _uber_name = "driver"
    _keys = ["phone_number", "rating", "picture_url", "name"]

class LocationObj(BaseUberClass):
    _uber_name = "location"
    _keys = ["latitude", "longitude", "bearing"]

class VehicleObj(BaseUberClass):
    _uber_name = "vehicle"
    _keys = ["make", "model", "license_place", "picture_url"]

class RequestRideObj(BaseUberClass):
    _uber_name = "request"
    _keys = ["request_id", "status", "eta", "surge_multiplier"]
    _objects = [VehicleObj, DriverObj, LocationObj]

class PriceObj(BaseUberClass):
    _uber_name = "price"
    _keys = ["surge_confirmation_href", "high_estimate", "surge_confirmation_id", "minimum", "low_estimate", "surge_multiplier", "display", "currency_code"]

class TripObj(BaseUberClass):
    _uber_name = "trip"
    _keys = ["distance_unit", "duration_estimate", "distance_estimate"]

class ChargesObj(BaseUberClass):
    _uber_name = "charges"
    _keys = ["name", "amount", "type"]

class SurgeChargeObj(BaseUberClass):
    _uber_name = "surge_charge"
    _keys = ["name", "amount", "type"]

class ChargeAdjustmentsObj(BaseUberClass):
    _uber_name = "charge_adjustments"
    _keys = ["name", "amount", "type"]

class EventObj(BaseUberClass):
    _uber_name = "event"
    _keys = ["name", "location", "latitude", "longitude", "product_id", "time"]

class UberClassObj(BaseUberClass):
    _uber_name = "TOP_LEVEL_UBER_OBJECT"
    _objects = [ProductIDObj, PricesObj]

##############################Endpoints###########################

class BaseUberClassEndpoint(BaseUber):
    _endpoint = None
    _version = 1
    _methods = [GET]

    def __init__(self, dictionary):
        super(BaseUberClassEndpoint, self).__init__(dictionary)
        if not hasattr(self, "_version"):
            self._version = 1
        if not hasattr(self, "_methods"):
            self._methods = [GET]

    def path(self):
        return "v{0}/{1}".format(self.version, self.endpoint)

class Products(BaseUberClassEndpoint):
    _endpoint = "products"
    _objects = [ProductIDObj]
    _version = 1
    _methods = [GET]


class ProductsID(BaseUberClassEndpoint):
    _endpoint = "products/{0}"
    _keys = ["capacity", "description", "image", "display_name", "product_id"]
    _objects = [PriceDetailsObj]
    _version = 1
    _methods = [GET]

class EstimatesPrice(BaseUberClassEndpoint):
    _endpoint = "estimates/price"
    _objects = [PricesObj]
    _version = 1
    _methods = [GET]

class EstimatesTime(BaseUberClassEndpoint):
    _version = 1
    _methods = [GET]
    _endpoint = "estimates/time"
    _objects = [TimesObj]

class Prices(BaseUberClassEndpoint):
    _version = 1
    _methods = [GET]
    _endpoint = "prices"
    _objects = [PricesObj]

class Times(BaseUberClassEndpoint):
    _version = 1
    _methods = [GET]
    _endpoint = "times"
    _objects = [TimesObj]

class History_V1_2(BaseUberClassEndpoint):
    _methods = [GET]
    _endpoint = "history"
    _version = 1.2
    _keys = ["offset", "limit", "count"]
    _objects = [HistoryObj_V1_2]

class History_V1_1(BaseUberClassEndpoint):
    _methods = [GET]
    _endpoint = "history"
    _version = 1.1
    _keys = ["offset", "limit", "count"]
    _objects = [HistoryObj_V1_1]

class Me(BaseUberClassEndpoint):
    _version = 1
    _methods = [GET]
    _endpoint = "me"
    _keys = ["first_name", "last_name", "email", "picture", "promo_code", "uuid"]

class RequestsCreateRide(BaseUberClassEndpoint):
    _version = 1
    _endpoint = "requests"
    _methods = [POST]
    _keys = ["request_id", "status", "eta", "surge_multiplier"]
    _objects = [VehicleObj, DriverObj, LocationObj]

class RequestsRideDetails(BaseUberClassEndpoint):
    _version = 1
    _methods = [GET]
    _endpoint = "requests/{0}"
    _keys = ["request_id", "status", "eta", "surge_multiplier"]
    _objects = [VehicleObj, DriverObj, LocationObj]

class RequestsRideEstimate(BaseUberClassEndpoint):
    _version = 1
    _endpoint = "requests/estimate"
    _methods = [POST]
    _keys = ["pickup_estimate"]
    _objects = [PriceObj]

class RequestsDelete(BaseUberClassEndpoint):
    _version = 1
    _endpoint = "requests/{0}"
    _methods = [DELETE]

class RequestsMap(BaseUberClassEndpoint):
    _version = 1
    _methods = [GET]
    _endpoint = "requests/{0}/map"
    _keys = ["request_id", "href"]

class RequestsReceipt(BaseUberClassEndpoint):
    _version = 1
    _methods = [GET]
    _endpoint = "requests/{0}/receipt"
    _keys = ["request_id", "normal_fare", "subtotal", "total_changed", "total_owed", "currency_code", "duration", "distance", "distance_label"]
    _objects = [ChargesObj, SurgeChargeObj, ChargeAdjustmentsObj]

class Reminders(BaseUberClassEndpoint):
    _version = 1
    _endpoint = "reminders"
    _methods = [POST, GET, PATCH]
    _keys = ["product_id", "reminder_id", "reminder_time", "reminder_status"]
    _objects = [EventObj]

class Promotions(BaseUberClassEndpoint):
    _version = 1
    _methods = [GET]
    _endpoint = "promotions"
    _keys = ["display_text", "localized_value", "type"]

class SandboxRideStatus(BaseUberClassEndpoint):
    _version = 1
    _endpoint = "sandbox/requests/{0}"
    _methods = [PUT]

class SandboxProducts(BaseUberClassEndpoint):
    _version = 1
    _endpoint = "sandbox/products/{0}"
    _methods = [PUT]

class Response(object):
    """The response from an HTTP request."""

    def __init__(self, response, response_obj):
        """Initialize a Response.

        Parameters
            response (requests.Response)
                The HTTP response from an API request.
        """
        self.status_code = response.status_code
        self.request = response.request
        self.rate_limit = response.headers['X-Rate-Limit-Limit']
        self.rate_remaining = response.headers['X-Rate-Limit-Remaining']
        self.rate_reset = response.headers['X-Rate-Limit-Reset']
        self.headers = response.headers

        # (TODO: request_id is not surfaced yet)
        # self.request_id = response.headers['request_id']

        try:
            self.json = response.json()
        except:
            self.json = None
        print self.json
        self.uber_obj = response_obj(self.json)

    def __repr__(self):
        return self.uber_obj.__repr__()