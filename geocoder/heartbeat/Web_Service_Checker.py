'''
 Description
 -----------

 This python script is used to submit a single request to a web service
 or collection of web services. This script will capture and parse the
 web service response and write an entry to a text file. Intended to be
 included in a scheduled job with a regular interval to monitor a
 web service.

 Specifically, the script will log the date and time, executionTime
 and response code for the BC Physical Address Geocoder and the
 BC Route Planner.

 Learn more about these APIs using API consoles linked from the BC
 Data Catalogue:

 BC Physical Address Geocoder:
 https://catalogue.data.gov.bc.ca/dataset/8f4a016f-14db-4def-8ef9-7c797de1cdd9

 BC Route Planner:
 https://catalogue.data.gov.bc.ca/dataset/3dad0c30-ef32-4f4c-82fa-33787d5f85f8

 Two of the APIs below require the use of API keys. The API keys listed
 below are throttled and not intended for general use. To acquire an API
 key for your application please contact DataBC.

 Contact Us
 -----------
 https://forms.gov.bc.ca/databc-contact-us/
'''

# Import modules
import sys
import time
import urllib2
import json

# Clear variables
logfile_1 = ''
logfile_2 = ''
logfile_3 = ''
geocoder_secure_url = ''
geocoder_public_url = ''
router_url = ''
json_response = ''
web_request = ''
service_url = []
log_files = []


# Define variables

# Request URL to the gated geocoder
# Please contact DataBC to acquire an API key for your application
geocoder_secure_url = 'https://geocoder.api.gov.bc.ca/addresses.json?' \
                      'addressString=%20525%20Superior%20Street%2C%20' \
                      'Victoria%2C%20BC&locationDescriptor=any&maxResults=1' \
                      '&interpolation=adaptive&echo=true&setBack=0&' \
                      'outputSRS=4326&minScore=1&provinceCode=BC' \
                      '&apikey=' NEED AN API KEY - THROTTLED AND GENERIC

# Request URL to the public geocoder
geocoder_public_url = 'https://apps.gov.bc.ca/pub/geocoder/addresses.json?' \
                      'addressString=%20525%20Superior%20Street%2C%20' \
                      'Victoria%2C%20BC&locationDescriptor=any&maxResults=1' \
                      '&interpolation=adaptive&echo=true&setBack=0&' \
                      'outputSRS=4326&minScore=1&provinceCode=BC&' \
                      'apikey=nokeyprovided'

# Request URL to the BC Route Planner
# Please contact DataBC to acquire an API key for your application
router_url = 'https://router.api.gov.bc.ca/route.json?routeDescription=' \
             'spansProvinceFastest&points=-126.844567%2C49.978503%2C-' \
             '122.799997%2C58.925305&outputSRS=4326&criteria=fastest' \
             '&distanceUnit=km&apikey=' NEED AN API KEY - THROTTLED AND GENERIC

# Location of the text files
logfile_1 = GitHub repo URL '\geocoder-secure-heartbeat.txt'
logfile_2 = GitHub repo URL '\geocoder-public-heartbeat.txt'
logfile_3 = GitHub repo URL '\router-heartbeat.txt'

# Counter used to iterate through the 'log_file' list.
log_count = 0

# Lists to iterate through the variables above
service_url = [geocoder_secure_url, geocoder_public_url, router_url]
log_files = [logfile_1, logfile_2, logfile_3]

# Loop through and write results to the respective log files
for _URL_ in service_url:
    # Get the date and time
    timestamp = time.strftime('%Y/%m/%d|%H:%M:%S|')
    # Get the HTTP response code
    response_code = urllib2.urlopen(_URL_).getcode()
    # Get the JSON response and parse out the execution time (executionTime)
    web_request = urllib2.urlopen(_URL_)
    json_response = web_request.read()
    # Load the JSON response for parsing
    data = json.loads(json_response)
    # Grab the executionTime parameter
    exec_time = data['executionTime']
    # Write the results to log file
    target_gated_log = open(log_files[log_count], 'a')
    target_gated_log.write(str(timestamp))
    target_gated_log.write(str(exec_time) + '|')
    target_gated_log.write(str(response_code))
    target_gated_log.write('\n')
    target_gated_log.close()
    log_count += 1
    
