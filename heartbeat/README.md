# DataBC Web Services Heartbeat Monitoring Utilities

This repo contains scripts, resultant files and web pages that can be used to help verify the operating status of specific web service APIs provided by DataBC. 

A single request is sent to each web service using a scheduled job to ensure consistency and allow for comparison over multiple days. Specific information for each web service is recorded including a time stamp, execution time, network latency, proxy latency and HTTP response status code.

* The resultant text files show entries on 10 minute intervals; a value of zero means no response from the API


### Visualizations

B.C. Geographical Names Web Service<br/>
http://bcgov.github.io/dbcrss/heartbeat/bcgnws/  <br/><br/>

DataBC Web Services<br/>


### Supported web browsers

A modern web browser is recommended for viewing GitHub pages which include data visualizations.


### Licenses

Content found at the root of the 'src' folder:  <br/>
https://github.com/bcgov/dbcrss/blob/master/heartbeat/LICENSE  <br/>

Content found within the 'src/d3' folder:  <br/>
https://github.com/bcgov/dbcrss/blob/master/heartbeat/src/d3/LICENSE  <br/>
