# DataBC Heartbeat

DataBC offers a number of RESTful APIs which are owned and managed by the Province of BC. 

This repo contains scripts, resultant files and web pages to verify that web services hosted by DataBC are online. A single request is sent to
each web service using a scheduled job to ensure consistency and allow for comparison over multiple days.
Specific information for each web service is recorded including a time stamp, execution time and HTTP response status code.


### Supported web browsers

A modern web browser is recommended for viewing GitHub pages which include data visualizations (d3).

http://bcgov.github.io/dbcrss/heartbeat/geocoder_pub/  <br/>
http://bcgov.github.io/dbcrss/heartbeat/geocoder_sec/  <br/>
http://bcgov.github.io/dbcrss/heartbeat/router/  <br/>


### Licenses

Content found at the root of the 'src' folder
https://github.com/bcgov/dbcrss/blob/master/heartbeat/LICENSE

Content found within the 'src/d3' folder
https://github.com/bcgov/dbcrss/blob/master/heartbeat/src/d3/LICENSE
