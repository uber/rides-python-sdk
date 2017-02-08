
v0.4.1 - 2/8/2017
-------------------
- Made state token optional in authorization code grant

v0.4.0 - 1/23/2017
-------------------
- Upgrade OAuth endpoints to use v2.

v0.3.1 - 11/12/2016
-------------------
- Removal of rate limiting headers. The headers are deprecated with v1.2: X-Rate-Limit-Limit, X-Rate-Limit-Remaining, X-Rate-Limit-Reset.

v0.3.0 - 11/12/2016
-------------------
- Release of v1.2 endpoints for the Riders API.
- API base URL would need to reflect the version bump: https://api.uber.com/v1.2/.

v0.2.7 - 9/28/2016
-------------------
- Added support for Python wheels

v0.2.6 - 9/28/2016
------------------
 - Added better support for python 2.

v0.2.5 - 7/18/2016
------------------
 - Add seat_count support to get_price_estimates

v0.2.4 - 6/10/2016
------------------
 - Added SDK Version header

v0.2.3 - 6/8/2016
-----------------
 - Added Pool support

v0.2.2 - 6/2/2016
-----------------
 - Fixed backwards compatibility setup support for Python 2
 - Allowed custom state tokens for authorizations
 - Improved ErrorDetails formatting

v0.2.1 - 3/29/2016
------------------
 - Added support for Python 3

v0.2.0 - 2/20/2016
------------------
 - Added places support
 - Added payment methods support
 - Added trip experiences support
 - Added optional destination (Fix for Issue #4)
 - Added update destinaion support
 - Added default product ID support for estimates and ride requests
 - Rides Client mode (Sandbox or Production) is explicitly set

v0.1.0 - 9/26/2015
------------------
 - Initial version.
