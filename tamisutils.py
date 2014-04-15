import base64
import json
import csv
import StringIO

from datetime import datetime
from functools import wraps
import urllib
from django.contrib.auth import authenticate
from django.http import HttpResponse
import httplib2
import os.path
import os

from django.conf import settings
from django.template.base import Template
from django.template.context import Context
#from geonode import datamanager


def testFormhubConnection(url, username, password):
    auth = base64.encodestring(username+ ':' + password)
    headers = {'Authorization' : 'Basic ' + auth}
    http = httplib2.Http(disable_ssl_certificate_validation=True)
    http.add_credentials(username, password)
    resp, content = http.request(url, headers=headers)
    if resp.status == 200:
        return True, "success"
    elif resp.status == 404:
        return False, "Cannot find URL"
    elif resp.status == 403:
        return False, "User name or password incorrect"
    else:
        return False, "Unknown error"



def getFormhubCSV(TAMISConnection):
#post to TAMIS URL

    url = dataconnection.formhub_url.strip('/') + "/data.csv"
    auth = base64.encodestring(dataconnection.formhub_username + ':' +  dataconnection.formhub_password)
    headers = {'Authorization' : 'Basic ' + auth}
    http = httplib2.Http(disable_ssl_certificate_validation=True)
    http.add_credentials(dataconnection.formhub_username, dataconnection.formhub_password)
    resp, content = http.request(url, headers=headers)

    f = StringIO.StringIO(content)
    reader = csv.reader(f, delimiter=',')
    headers = reader.next()
    data = []
    for row in reader:
        data.append(row)
    return headers, data


# from geopy import geocoders


# def geocodeSet(opentext, addition):
#     if addition:
#         geocodestring = opentext + addition
#     else:
#         geocodestring = opentext
#     g = geocoders.GoogleV3()
#     try:
#         place, (lat, lon) = g.geocode(geocodestring)
#     except:
#         return False
#     if lat and lon:
#         return {'lat':lat, 'lon':lon}  
#     else:
#         return False
#     #do the geocode


