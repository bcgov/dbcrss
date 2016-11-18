# DataBC Heartbeat (Web Service Checker)

DataBC offers a number of RESTful APIs which are owned and managed by the Province of BC. 

This repo contains python scripts, resultant files and web pages to verify that DataBC web services are online. A single request is sent to
each web service using a scheduled job to ensure consistency and comparison over multiple days.
Specific information for each web service is recorded including a timestamp, execution time and response code.


### License

https://github.com/bcgov/dbcrss/blob/master/heartbeat/LICENSE
