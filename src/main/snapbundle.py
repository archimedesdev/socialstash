__author__ = 'prad'

import urllib2
import json
import base64
import requests
import snapbundle_utils

username = 'paul@archimedessolutions.com'
password = 'ohTw33t!'
base_url_objects = 'https://snapbundle.tagdynamics.net/v1/app/objects'
user_object = 'praddc'

request = urllib2.Request(base_url_objects + '/' + user_object)
base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
request.add_header("Authorization", "Basic %s" % base64string)
try:
    response = urllib2.urlopen(request)
except urllib2.URLError, e:
    if e.code == 404:
        print "That user does not exist"
else:
    data = json.load(response)

##--------------------------------------------------------------------------

r = requests.get(base_url_objects + '/' + user_object, auth=(username, password))
#print r.json()

r = requests.get('https://snapbundle.tagdynamics.net/v1/app/objects', auth=(username, password))
print r.json()

r = requests.get('https://snapbundle.tagdynamics.net/v1/app/metadata/query/Object/praddc', auth=(username, password))
#print r
print r.json()
