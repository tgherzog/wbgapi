
This module provides a very rudimentary interface to the World Bank's data API.

Currently only low-level functionality is defined, but the aspiration is this
will improve over time to take advantage of the latest API functionality, as
well as perhaps compensate for some of its flaws.

Current functionality includes:

* generator objects to page through large data requests efficiently

* error classes and exceptions to handle server errors and malformed
  requests
