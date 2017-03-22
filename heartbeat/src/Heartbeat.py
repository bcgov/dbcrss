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

 python heartbeat.py -url "https://geocoder.api.gov.bc.ca/addresses.json?addressString=%20525%20Superior%20Street%2C%20Victoria%2C%20BC&locationDescriptor=any&maxResults=1&interpolation=adaptive&echo=true&setBack=0&outputSRS=4326&minScore=1&provinceCode=BC&apikey=<KEY_HERE>" -o geocoder-secure-heartbeat.txt

 python heartbeat.py -url "https://apps.gov.bc.ca/pub/geocoder/addresses.json?addressString=%20525%20Superior%20Street%2C%20Victoria%2C%20BC&locationDescriptor=any&maxResults=1&interpolation=adaptive&echo=true&setBack=0&outputSRS=4326&minScore=1&provinceCode=BC&apikey=nokeyprovided" -o geocoder-public-heartbeat.txt

 python heartbeat.py -url "https://router.api.gov.bc.ca/route.json?routeDescription=spansProvinceFastest&points=-126.844567%2C49.978503%2C-122.799997%2C58.925305&outputSRS=4326&criteria=fastest&distanceUnit=km&apikey=<KEY_HERE>" -o router-heartbeat.txt


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
  return "chart|date|executionTime|upstreamLatency|proxyLatency|responseCode\n"

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

try:
  # Get the date and time
  timestamp = time.strftime('%Y/%m/%d|%H:%M:%S|')
  # Get the HTTP response code
  response_code = urllib2.urlopen(args.url).getcode()
  #Get latency values from header
  upstreamLatency = urllib2.urlopen(args.url).info().getheader('X-Kong-Upstream-Latency')
  proxyLatency = urllib2.urlopen(args.url).info().getheader('X-Kong-Proxy-Latency')
  # Get the JSON response and parse out the execution time (executionTime)
  web_request = urllib2.urlopen(args.url)
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
  outFile.write(str(response_code))
  outFile.write('\n')
  outFile.close()
else:
  outFile = open(args.outFilename, 'a')
  outFile.write(str(timestamp))
  outFile.write(str(exec_time) + '|')
  outFile.write(str(upstreamLatency) + '|')
  outFile.write(str(proxyLatency) + '|')
  outFile.write(str(response_code))
  outFile.write('\n')
  outFile.close() 

