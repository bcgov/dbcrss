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


 Usage
 -----

 python heartbeat.py -url "<URL TO TEST>" -o <OUTPUT FILE>

 Usage Examples:
 --------

 python heartbeat.py -url "https://geocoder.api.gov.bc.ca/addresses.json?addressString=%20525%20Superior%20Street%2C%20Victoria%2C%20BC&locationDescriptor=any&maxResults=1&interpolation=adaptive&echo=true&setBack=0&outputSRS=4326&minScore=1&provinceCode=BC&apikey=<KEY_HERE>" -o ../data/geocoder-secure-heartbeat.txt

 python heartbeat.py -url "https://apps.gov.bc.ca/pub/geocoder/addresses.json?addressString=%20525%20Superior%20Street%2C%20Victoria%2C%20BC&locationDescriptor=any&maxResults=1&interpolation=adaptive&echo=true&setBack=0&outputSRS=4326&minScore=1&provinceCode=BC&apikey=nokeyprovided" -o ../data/geocoder-public-heartbeat.txt

 python heartbeat.py -url "https://router.api.gov.bc.ca/route.json?routeDescription=spansProvinceFastest&points=-126.844567%2C49.978503%2C-122.799997%2C58.925305&outputSRS=4326&criteria=fastest&distanceUnit=km&apikey=<KEY_HERE>" -o ../data/router-heartbeat.txt

 python heartbeat.py -url "http://apps.gov.bc.ca/pub/bcgnws/names/search?name=victoria&outputFormat=json" -o ../data/bcgnws-heartbeat.txt

 python heartbeat.py -url "https://apps.gov.bc.ca/pub/geomark/geomarks/gm-7A4A2A93A090493186442C1A48B179C4/point.json?srid=4326" -o ../data/geomark-heartbeat.txt

 python heartbeat.py -url "https://catalogue.data.gov.bc.ca/api/3/action/package_search?fq=license_id:22" -o ../data/bcdc-heartbeat.txt

 Contact Us
 -----------
 https://forms.gov.bc.ca/databc-contact-us/
'''

import os
import sys
import time
import urllib2
import json
import argparse


#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------

def getHeader():
  return "chart|date|executionTime|upstreamLatency|proxyLatency|responseCode|responseTime\n"

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------

argParser = argparse.ArgumentParser(description='Checks the heartbeat of a given URL')
argParser.add_argument('-url', dest='url', action='store', default=None, required=True, help='The URL to check the heartbeat of')
argParser.add_argument('-o', dest='outFilename', action='store', default=None, required=True, help='The file to append heartbeat results to')

try:
  args = argParser.parse_args()
except argparse.ArgumentError as e:
  argParser.print_help()
  sys.exit(1)

response_code = ""
upstreamLatency = ""
proxyLatency = ""
exec_time = ""
response_time = ""

# Get the date and time
timestamp = time.strftime('%Y/%m/%d|%H:%M:%S|')

try:
  #Run an HTTP GET on the url
  start_time = time.time();
  response = urllib2.urlopen(args.url)
  end_time = time.time();
  response_time = (end_time - start_time) * 1000
  # Get the HTTP response code
  response_code = response.getcode()
  #Get latency values from header
  if response.info().getheader('X-Kong-Upstream-Latency'):
    upstreamLatency = response.info().getheader('X-Kong-Upstream-Latency')
  if response.info().getheader('X-Kong-Proxy-Latency'):
    proxyLatency = response.info().getheader('X-Kong-Proxy-Latency')
  # Get the response body
  response_body = response.read()
except urllib2.URLError as e:
  if hasattr(e, "code"):
    response_code = e.code

try:
  # Assume the response object is JSON, and try to parse it.
  data = json.loads(response_body)
  # If the response body was JSON, and it it contains an executionTime property
  # then fetch that value
  if 'executionTime' in data:
    exec_time = data['executionTime']
except Exception as e:
  pass #fail silently

#
#Only retain 7 days of data (10 minute intervals)
one_week_lines = 1008
num_lines_to_remove = 0
if os.path.exists(args.outFilename):
  num_lines_total = int((sum(1 for line in open(args.outFilename))) - 1)
  num_lines_to_remove = (num_lines_total - one_week_lines) + 1
else:
  outFile = open(args.outFilename, 'w+')
  outFile.write(getHeader())
  outFile.close()

#
if num_lines_to_remove >= 1:
  print "total lines: "+str(num_lines_total)+". removing "+str(num_lines_to_remove)+" lines"
  lines = open(args.outFilename).readlines()
  outFile = open(args.outFilename, 'w+')
  outFile.write(getHeader())
  outFile.writelines(lines[num_lines_to_remove:])
  outFile.write(str(timestamp))
  outFile.write(str(exec_time) + '|')
  outFile.write(str(upstreamLatency) + '|')
  outFile.write(str(proxyLatency) + '|')
  outFile.write(str(response_code) + '|')
  outFile.write(str(response_time))
  outFile.write('\n')
  outFile.close()
else:
  outFile = open(args.outFilename, 'a')
  outFile.write(str(timestamp))
  outFile.write(str(exec_time) + '|')
  outFile.write(str(upstreamLatency) + '|')
  outFile.write(str(proxyLatency) + '|')
  outFile.write(str(response_code) + '|')
  outFile.write(str(response_time))
  outFile.write('\n')
  outFile.close() 

