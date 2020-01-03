
* Support API search

* Topics support, including the option to select series by topic. This should
  be straight-forward as it's similar to the region implementation. But the API
  is also schizophrenic in its topics implementation. They make sense for WDI
  but they can be a bit weird even nonsensical for other databases.

* Re-architect to segment very large requests into smaller ones to prevent 
  400 Bad Request responses

* Support for fetching multiple footnotes, hmmm...

* See if the API team can support the 'all' keyword for metadata requests
  so that we could do the same
