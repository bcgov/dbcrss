"""
 Last Modified: August 9, 2017

------------------------------------------------------------------------------
 Description
------------------------------------------------------------------------------

 This python script is used to submit a single request to a web service
 or collection of web services. This script will capture and parse the
 web service response (and header) and write an entry to a text file.
 Intended to be included in a scheduled job with a regular interval to
 monitor a web service.

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

------------------------------------------------------------------------------
 Usage
------------------------------------------------------------------------------
 python heartbeat.py -url "<URL TO TEST>" -o <OUTPUT FILE>

------------------------------------------------------------------------------
 Usage Examples
------------------------------------------------------------------------------
 python heartbeat.py -url "https://geocoder.api.gov.bc.ca/addresses.json?addressString=%20525%20Superior%20Street%2C%20Victoria%2C%20BC&locationDescriptor=any&maxResults=1&interpolation=adaptive&echo=true&setBack=0&outputSRS=4326&minScore=1&provinceCode=BC&apikey=<KEY_HERE>" -o ../data/geocoder-secure-heartbeat.txt

 python heartbeat.py -url "https://apps.gov.bc.ca/pub/geocoder/addresses.json?addressString=%20525%20Superior%20Street%2C%20Victoria%2C%20BC&locationDescriptor=any&maxResults=1&interpolation=adaptive&echo=true&setBack=0&outputSRS=4326&minScore=1&provinceCode=BC&apikey=nokeyprovided" -o ../data/geocoder-public-heartbeat.txt

 python heartbeat.py -url "https://router.api.gov.bc.ca/route.json?routeDescription=spansProvinceFastest&points=-126.844567%2C49.978503%2C-122.799997%2C58.925305&outputSRS=4326&criteria=fastest&distanceUnit=km&apikey=<KEY_HERE>" -o ../data/router-heartbeat.txt

 python heartbeat.py -url "http://apps.gov.bc.ca/pub/bcgnws/names/search?name=victoria&outputFormat=json" -o ../data/bcgnws-heartbeat.txt

 python heartbeat.py -url "https://apps.gov.bc.ca/pub/geomark/geomarks/gm-7A4A2A93A090493186442C1A48B179C4/point.json?srid=4326" -o ../data/geomark-heartbeat.txt

 python heartbeat.py -url "https://catalogue.data.gov.bc.ca/api/3/action/package_search?fq=license_id:22" -o ../data/bcdc-heartbeat.txt

------------------------------------------------------------------------------
 Contact Us
------------------------------------------------------------------------------
 https://forms.gov.bc.ca/databc-contact-us/
"""

import argparse
import collections
import csv
import datetime
import json
import os
import sys
import time

if sys.version_info > (3,):
    from urllib.error import HTTPError, URLError
    from urllib.request import urlopen
else:
    from urllib2 import HTTPError, URLError, urlopen

HEADER_FIELDNAMES = (
    'chart',  # TODO: should be 'date'?
    'date',  # TODO: should be 'time'?
    'executionTime',
    'upstreamLatency',
    'proxyLatency',
    'responseCode',
    'responseTime'
)
# Only retain 7 days of data (10 minute intervals)
# 6 (10 minute chunks per hour) * 24 (hours per day) * 7 (days)
MAX_ROWS = 6 * 24 * 7  # 1008


def _get_current_date_and_time():
    d = datetime.datetime.now()
    return {
        'chart': d.strftime('%Y/%m/%d'),  # TODO: should be 'date'?
        'date': d.strftime('%H:%M:%S')  # TODO: should be 'time'?
    }


def _get_url_response_info(url):
    try:
        # Run an HTTP GET on the url
        start_time = time.time()
        response = urlopen(url)
    except HTTPError as e:
        return {'responseCode': e.code}
    except (URLError, ValueError):
        return {}
    else:
        end_time = time.time()

    try:
        data = json.loads(response.read())
    except ValueError:
        # If the data being deserialized is not a valid JSON document,
        # a ValueError will be raised (Python 2.7 -> 3.4)
        exec_time = ''
    else:
        exec_time = data.get('executionTime', '')

    return {
        'executionTime': exec_time,
        'proxyLatency': response.info().getheader(
            'X-Kong-Proxy-Latency',
            default=''
        ),
        'responseCode': response.getcode(),
        'responseTime': (end_time - start_time) * 1000,
        'upstreamLatency': response.info().getheader(
            'X-Kong-Upstream-Latency',
            default=''
        )
    }


def _parse_cmd_line_args():
    parser = argparse.ArgumentParser(
        description='Checks the heartbeat of a given URL'
    )
    parser.add_argument(
        '-url',
        dest='url',
        action='store',
        required=True,
        help='The URL to check the heartbeat of'
    )
    parser.add_argument(
        '-o',
        dest='output_filename',
        action='store',
        required=True,
        help='The file to append heartbeat results to'
    )
    return parser.parse_args()


def _read_csv(filename):
    result = collections.deque(maxlen=MAX_ROWS)
    if os.path.exists(filename):
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='|')
            result.extend(reader)
    return result


def _write_csv(filename, rows):
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(
            csvfile,
            delimiter='|',
            fieldnames=HEADER_FIELDNAMES
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    # Parse command-line arguments from sys.argv
    args = _parse_cmd_line_args()

    # Initialize dictionary to hold new URL response information
    url_response_info = {key: '' for key in HEADER_FIELDNAMES}

    # Update the date and time key/value pairs
    url_response_info.update(_get_current_date_and_time())

    # Update the URL response information key/value pairs
    url_response_info.update(_get_url_response_info(args.url))

    # Read rows into a deque (if file exists, else empty deque)
    current_rows = _read_csv(args.output_filename)

    # Append new URL response information to the deque
    current_rows.append(url_response_info)

    # Write all rows to csv output file
    _write_csv(args.output_filename, current_rows)


if __name__ == '__main__':
    main()
