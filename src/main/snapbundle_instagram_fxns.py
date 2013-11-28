__author__ = 'prad'

import json
import requests
import calendar
import time
import ConfigParser
import snapbundle_helpers
import logging

logging.debug('Starting: ' + __name__)

# == Import all the account information that is stored in a local file (not sync'd wih public github)
config_file = 'accounts.txt'
config = ConfigParser.RawConfigParser()
config.read(config_file)

# == Start Snapbundle Variables ==
snapbundle_username = config.get('SnapbundleCredentials', 'snapbundle_username')
snapbundle_password = config.get('SnapbundleCredentials', 'snapbundle_password')
# == End Snapbundle Variables ==

# == Start Snapbundle URLs ==
base_url_objects = 'https://snapbundle.tagdynamics.net/v1/app/objects'
base_url_object_interaction = 'https://snapbundle.tagdynamics.net/v1/app/interaction'
base_url_metadata_objects = 'https://snapbundle.tagdynamics.net/v1/app/metadata/Object'
base_url_metadata_mapper_encode = 'https://snapbundle.tagdynamics.net/v1/public/metadata/mapper/encode/'
base_url_metadata_mapper_decode = 'https://snapbundle.tagdynamics.net/v1/public/metadata/mapper/decode/'
base_url_devicess = 'https://snapbundle.tagdynamics.net/v1/admin/devices'
# == End Snapbundle URLs ==


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def add_new_instagram_user_object(instagram_handle, sb_username, description):
    object_urn = "urn" + sb_username + ":instagram:" + instagram_handle
    json_info = {"moniker": instagram_handle,
                 "name": sb_username,
                 "description": description,
                 "active": "true",
                 "hasGeoLocation": "false",
                 "objectUrn": object_urn,
                 "objectType": "Person"
                 }
    url = base_url_objects
    headers = {'content-type': 'application/json'}
    payload = json.dumps(json_info)
    print "Sending to URL: " + str(url)
    print "Submitting Payload: " + str(payload)
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    print "Response (for objectURN " + object_urn + "): " + str(response.status_code) + " <--> " + str(response.json())
    #print response
    #print str(response.json())


## ----------------------------------- FXN ------------------------------------------------------------------------
def update_instagram_user_object(reference_urn, user):
    snapbundle_helpers.add_update_metadata("Object", reference_urn, "String", "id", user['id'])
    snapbundle_helpers.add_update_metadata("Object", reference_urn, "String", "username", user['username'])
    snapbundle_helpers.add_update_metadata("Object", reference_urn, "String", "full_name", user['full_name'])
    snapbundle_helpers.add_update_metadata("Object", reference_urn, "String", "profile_picture", user['profile_picture'])
    snapbundle_helpers.add_update_metadata("Object", reference_urn, "String", "bio", user['bio'])
    snapbundle_helpers.add_update_metadata("Object", reference_urn, "String", "website", user['website'])
    snapbundle_helpers.add_update_metadata("Object", reference_urn, "String", "counts", user['counts'])


## ----------------------------------- FXN ------------------------------------------------------------------------
def add_new_twitter_tweet(parent_object_urn, tweet):
    ## -- The ObjectInteraction portion of the tweet
    pattern = '%Y-%m-%d %H:%M:%S'
    created_at = tweet.created_at.strftime("%Y-%m-%d %H:%M:%S")
    created_at_epoch_utc = int(calendar.timegm(time.strptime(created_at, pattern)))
    if tweet.geo is None:
        hasGeoLocation = False
    else:
        hasGeoLocation = True

    moniker = parent_object_urn + ":tweets:" + tweet.id_str
    object_interaction = {'objectUrn': parent_object_urn,
                          'moniker': moniker,
                          'identification': get_twitter_snapbundle_device_object_id(parent_object_urn, tweet.source, tweet.retweeted),
                          'data': tweet.text,
                          'recordedTimestamp': created_at_epoch_utc,
                          'hasGeoLocation': hasGeoLocation,
                          'lat': '',
                          'lon': '',
                          'alt': ''
                          }

    url = base_url_object_interaction
    headers = {'content-type': 'application/json'}
    payload = json.dumps(object_interaction)
    print "Sending to URL: (" + str(url) + ") payload " + str(payload)
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    print "Response (for moniker " + moniker + "): " + str(response.status_code) + " <--> " + str(response.json())
    #print response
    #print str(response.json())
    return
    ## -- The additional metadata portion of the tweet
    #snapbundle_utils.add_update_metadata("Object", reference_urn, "Boolean", "contributors_enabled", user['contributors_enabled'])

    print tweet.contributors
    print tweet.truncated
    print tweet.retweeted
    print tweet.retweet_count
    print tweet.coordinates
    print tweet.id
    print tweet.id_str
    print tweet.in_reply_to_user_id
    print tweet.in_reply_to_user_id_str
    print tweet.in_reply_to_screen_name
    print tweet.in_reply_to_status_id
    print tweet.in_reply_to_status_id_str
    print tweet.text
    print tweet.source
    print tweet.source_url
    print tweet.favorited
    print tweet.favorite_count
    print tweet.place
    print tweet.lang
    #print tweet.possibly_sensitive
    #'_api': <tweepy.api.API object at 0x0000000002EC78D0>,
    #'author': <tweepy.models.User object at 0x0000000003014198>,
    #'entities': {u'symbols': [], u'user_mentions': [], u'hashtags': [],u'urls': [{u'url': u'http://t.co/OkVHIlJPyU', u'indices': [0, 22], u'expanded_url': u'http://amzn.com/k/n79ap3z4TBmT45pOqUaFFQ', u'display_url': u'amzn.com/k/n79ap3z4TBmT\u2026'}]},
    #'user': <tweepy.models.User object at 0x0000000003014198>,


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_twitter_snapbundle_device_object_id(parent_object_urn, source, retweeted):
    if retweeted:
        deviceType = 'Unknown'
    else:
        deviceType = get_snapbundle_device_type(source)

    identification = parent_object_urn + ":" + deviceType + ":" + source
    json_info = {"moniker": parent_object_urn,
                 "name": source,
                 "description": source,
                 "activeFlag": "true",
                 "deviceType": deviceType,
                 "identification": identification
                 }
    url = base_url_devicess
    headers = {'content-type': 'application/json'}
    payload = json.dumps(json_info)
    print "Sending to URL: " + str(url)
    print "Submitting Payload: " + str(payload)
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    print "Response: " + str(response.status_code) + " <--> "
    if response.status_code == 200:
        print "Device " + identification + " already existed!"
    elif response.status_code == 201:
        print "Device " + identification + " created successfully!"
    else:
        print "Unknown response: " + str(response)
    #print str(response.json())
    return identification


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_snapbundle_device_type(source):
    source = source.upper()
    # Start specific and get more general as we go down the line.
    # Looking for key words in the source string
    if "KINDLE" in source:
        return 'Kindle'
    elif "NOOK" in source:
        return 'Nook'
    elif "IPHONE" in source:
        return 'iPhone'
    elif "IPAD" in source:
        return 'iPad'
    elif "BLACKBERRY" in source:
        return 'Blackberry'
    elif "GOODREADS" in source:
        return 'Specialized'
    elif "ANDROID" in source:
        return 'Android'
    elif "PHONE" in source:
        return 'Phone'
    elif "WEB" in source:
        return 'PC'
    elif "MAC" in source:
        return 'PC'
    elif "TABLET" in source:
        return 'Tablet'
    elif "PHONE" in source:
        return 'Phone'
    else:
        return 'Unknown'