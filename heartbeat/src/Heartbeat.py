#Last Modified: December 16, 2016

'''
--------------------------------------------------------------------------------
 Description
--------------------------------------------------------------------------------

 This python script is used to submit a single request to a web service
 or collection of web services. This script will capture and parse the
 web service response (and header) and write an entry to a text file. Intended to be
 included in a scheduled job with a regular interval to monitor a
 web service.

 The script will log the date, time, executionTime, latency
 and response code for the BC Physical Address Geocoder and the
 BC Route Planner.

 Learn more about these APIs using API consoles linked from the BC
 Data Catalogue:

 BC Physical Address Geocoder:
 https://catalogue.data.gov.bc.ca/dataset/8f4a016f-14db-4def-8ef9-7c797de1cdd9

 BC Route Planner:
 https://catalogue.data.gov.bc.ca/dataset/3dad0c30-ef32-4f4c-82fa-33787d5f85f8

 Two of these APIs require the use of API keys. To acquire an API
 key for your application please contact DataBC.


 Contact Us
 -----------
 https://forms.gov.bc.ca/databc-contact-us/
 --------------------------------------------------------------------------------
'''

# Import modules
import sys
import time
import urllib2
import json

#--------------------------------------------------------------------------------
# Variable Descriptions
#--------------------------------------------------------------------------------
# Accept the API Key for the gated Geocoder and BC Route Planner as an argument
dbc_api_key = str(sys.argv[1])
# Request URL for the public Geocoder
geocoder_public_url = ''
# Request URL for the gated Geocoder
geocoder_secure_url = ''
# JSON response from web service request
json_response = ''
# Counter used to iterate through the 'log_file' list.
log_count = 0
# Log file containing response and header details for the gated Geocoder
logfile_1 = ''
# Log file containing response and header details for the public Geocoder
logfile_2 = ''
# Log file containing response and header details for the BC Route Planner
logfile_3 = ''
# List of text file locations to store output
log_files = []
# The total number of lines found in the textfile
num_lines_total = 0
# The number of lines beyond 7 days of data that need to be removed from the text file
num_lines_to_remove = 0
# The proxy latency as provided in response header
proxyLatency = 0
# The HTTP response status code
response_code = 0
# Request URL for the BC Route Planner
router_url = ''
# List of URLs (requests)
service_url = []
# The upstream latency provided in response header
upstreamLatency = 0
# web request submitted to web services
web_request = ''

#--------------------------------------------------------------------------------

# Request URL to the gated geocoder
# Please contact DataBC to acquire an API key for your application
geocoder_secure_url = 'https://geocoder.api.gov.bc.ca/addresses.json?' \
                      'addressString=%20525%20Superior%20Street%2C%20' \
                      'Victoria%2C%20BC&locationDescriptor=any&maxResults=1' \
                      '&interpolation=adaptive&echo=true&setBack=0&' \
                      'outputSRS=4326&minScore=1&provinceCode=BC' \
                      '&apikey=' + dbc_api_key

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
             '&distanceUnit=km&apikey=' + dbc_api_key

# Location of the text files
logfile_1 = 'geocoder-secure-heartbeat.txt'
logfile_2 = 'geocoder-public-heartbeat.txt'
logfile_3 = 'router-heartbeat.txt'

# Lists to iterate through the variables above
service_url = [geocoder_secure_url, geocoder_public_url, router_url]
log_files = [logfile_1, logfile_2, logfile_3]

# Loop through and write results to the respective log files
for _URL_ in service_url:
    try:
        # Get the date and time
        timestamp = time.strftime('%Y/%m/%d|%H:%M:%S|')
        # Get the HTTP response code
        response_code = urllib2.urlopen(_URL_).getcode()
        #Get latency values from header
        upstreamLatency = urllib2.urlopen(_URL_).info().getheader('X-Kong-Upstream-Latency')
        proxyLatency = urllib2.urlopen(_URL_).info().getheader('X-Kong-Proxy-Latency')
        # Get the JSON response and parse out the execution time (executionTime)
        web_request = urllib2.urlopen(_URL_)
        json_response = web_request.read()
        # Load the JSON response for parsing
        data = json.loads(json_response)
        # Grab the executionTime parameter
        exec_time = data['executionTime']
    except:
        response_code = 0
        upstreamLatency = 0
        proxyLatency = 0
        exec_time = 0
    #
    #Only retain 7 days of data (10 minute intervals)
    one_week_lines = 1008
    num_lines_total = int((sum(1 for line in open(log_files[log_count]))) - 1)
    num_lines_to_remove = (num_lines_total - one_week_lines) + 1
    #
    if num_lines_to_remove >= 1:
        lines = open(log_files[log_count]).readlines()
        target_log = open(log_files[log_count], 'w')
        target_log.write("chart|date|executionTime|upstreamLatency|proxyLatency|responseCode\n")
        target_log.writelines(lines[num_lines_to_remove:])
        target_log.write(str(timestamp))
        target_log.write(str(exec_time) + '|')
        target_log.write(str(upstreamLatency) + '|')
        target_log.write(str(proxyLatency) + '|')
        target_log.write(str(response_code))
        target_log.write('\n')
        target_log.close()
    else:
        target_log = open(log_files[log_count], 'a')
        target_log.write(str(timestamp))
        target_log.write(str(exec_time) + '|')
        target_log.write(str(upstreamLatency) + '|')
        target_log.write(str(proxyLatency) + '|')
        target_log.write(str(response_code))
        target_log.write('\n')
        target_log.close() 
    #
    log_count += 1
