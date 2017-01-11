# DataBC Heartbeat

DataBC offers a number of RESTful APIs which are owned and managed by the Province of BC. 

This repo contains scripts, resultant files and web pages to verify that web services hosted by DataBC are online. A single request is sent to
each web service using a scheduled job to ensure consistency and allow for comparison over multiple days.
Specific information for each web service is recorded including a time stamp, execution time, network latency, proxy latency and HTTP response status code.

* In the resultant text files showing entries every 10 minutes a value of zero means no response.


### Visualizations

http://bcgov.github.io/dbcrss/heartbeat/geocoder_pub/  <br/>
http://bcgov.github.io/dbcrss/heartbeat/geocoder_pub_latency/  <br/>
http://bcgov.github.io/dbcrss/heartbeat/geocoder_sec/  <br/>
http://bcgov.github.io/dbcrss/heartbeat/geocoder_sec_latency/  <br/>
http://bcgov.github.io/dbcrss/heartbeat/router/  <br/>
http://bcgov.github.io/dbcrss/heartbeat/router_latency/  <br/>


### Supported web browsers

A modern web browser is recommended for viewing GitHub pages which include data visualizations.


### Licenses

Content found at the root of the 'src' folder:  <br/>
https://github.com/bcgov/dbcrss/blob/master/heartbeat/LICENSE  <br/>

Content found within the 'src/d3' folder:  <br/>
https://github.com/bcgov/dbcrss/blob/master/heartbeat/src/d3/LICENSE  <br/>
