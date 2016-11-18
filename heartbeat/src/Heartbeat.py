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

 Two of the APIs below require the use of API keys. To acquire an API
 key for your application please contact DataBC.

 Contact Us
 -----------
 https://forms.gov.bc.ca/databc-contact-us/
'''
