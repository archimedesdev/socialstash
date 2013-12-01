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
snapbundle_base_urn_instagram_user = "urn:instagram:users:"
# == End Snapbundle Variables ==

# == Start Snapbundle URLs ==
base_url_objects = 'https://snapbundle.tagdynamics.net/v1/app/objects'
base_url_object_interaction = 'https://snapbundle.tagdynamics.net/v1/app/interaction'
base_url_metadata_objects = 'https://snapbundle.tagdynamics.net/v1/app/metadata/Object'
base_url_metadata_objects_query = 'https://snapbundle.tagdynamics.net/v1/app/metadata/query/Object'
base_url_metadata_mapper_encode = 'https://snapbundle.tagdynamics.net/v1/public/metadata/mapper/encode/'
base_url_metadata_mapper_decode = 'https://snapbundle.tagdynamics.net/v1/public/metadata/mapper/decode/'
base_url_devicess = 'https://snapbundle.tagdynamics.net/v1/admin/devices'
base_url_files_metadata_query = 'https://snapbundle.tagdynamics.net/v1/app/files/query/Metadata/'
base_url_files = 'https://snapbundle.tagdynamics.net/v1/app/files'
# == End Snapbundle URLs ==


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def check_for_object(urn_to_check_for):
    url = base_url_objects + '/' + urn_to_check_for
    logging.info("Looking for object at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.json()['objectUrn'] != urn_to_check_for:
            logging.info("ObjectURN not found!")
            return False
        else:
            logging.info("Object Exists!!")
            logging.info(response.json())
            return True
            #return response.json()#['urn']
    except KeyError:
        logging.info("Instagram user Object does not yet exist in SnapBundle")
        return False


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def get_object(urn_to_check_for):
    url = base_url_objects + '/' + urn_to_check_for
    logging.info("Looking for object at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.json()['objectUrn'] != urn_to_check_for:
            logging.info("ObjectURN not found!")
            return False
        else:
            logging.info("Object Exists!!")
            logging.info(response.json())
            return response.json()#['urn']
    except KeyError:
        logging.info("Instagram user Object does not yet exist in SnapBundle")
        return False


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def get_object_metadata(urn_to_check_for):
    url = base_url_metadata_objects_query + '/' + urn_to_check_for
    logging.info("Looking for object metadata at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.status_code == 200:
            return response.json()
        else:
            return False
    except KeyError:
        logging.info("Instagram user Object Metadata does not yet exist in SnapBundle")
        return False


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def check_update_user_profile_pic(username, current_pic_url):
    url = base_url_metadata_objects_query + '/' + snapbundle_base_urn_instagram_user + username
    logging.info("Looking for object profile pic metadata at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.status_code == 200:
            logging.info("Profile Pic Metadata Exists for User " + username)
            # The URL metadata exists, as it should, now let's:
            # 1) Decode the existing value and compare it to the value passed in
            # 2) If the value is the same, make sure the actual file lives in SnapBundle
            # 3) If the value is different, we need to create a new File object in SnapBundle, and get the file in there
            existing_stored_urn = response.json()['urn']
            existing_stored_url = snapbundle_helpers.get_raw_value_decoded(response.json()['value'], 'String')
            need_to_upload_url = False
            if existing_stored_url == current_pic_url:
                logging.info("Existing stored profile pic URL matches current URL for user " + username + ".  Checking to see if file exists in SnapBundle")
                # Check to see if a file exists in SB for this
                url = base_url_files_metadata_query + existing_stored_urn
                file_response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
                if file_response.status_code == 200:
                    # Some files are associated with this metadata object, need to check if they match the URL
                    print "CURRENT FILES INFO associated with the metadata, NEED TO SEE IF ONE MATCHES"
                    print file_response.json()
                    for current_file_response in file_response.json():
                        if current_file_response['filename'] == current_pic_url:
                            # The file already exists, we can just return true
                            return True
                    # If we exhaust our uploaded options, no match, need to upload it
                    need_to_upload_url = True
                else:
                    # No files are associated with this metadata object, need to upload it
                    need_to_upload_url = True
            else:
                # Need to create a new File object with this picture
                need_to_upload_url = True

            if need_to_upload_url:
                return snapbundle_helpers.add_file_from_url_jpg("Metadata", existing_stored_urn, current_pic_url, current_pic_url)
        else:
            return False
    except KeyError:
        logging.info("Instagram user Object Profile Pic Metadata does not yet exist in SnapBundle")
        return False


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def add_update_new_instagram_user_object(instagram_handle, instagram_user_sb_object_urn):
    json_info = {"name": instagram_handle,
                 "active": "true",
                 "objectUrn": instagram_user_sb_object_urn,
                 "objectType": "Person"
                 }
    url = base_url_objects
    headers = {'content-type': 'application/json'}
    payload = json.dumps(json_info)
    logging.info("Submitting Payload: " + str(payload))
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    logging.info("Response (for objectURN " + instagram_user_sb_object_urn + "): " + str(response.status_code) + " <--> " + str(response.json()))
    if response.status_code == 201:
        # Created new user
        logging.info("Created new user")
    elif response.status_code == 200:
        # Updating user
        logging.info("User existed, updated")
    urn = response.json()['message']
    return urn


## ----------------------------------- FXN ------------------------------------------------------------------------
def update_instagram_user_object(reference_urn, user, new_user):
    snapbundle_helpers.add_update_metadata("Object", reference_urn, "String", "id", user['id'])
    snapbundle_helpers.add_update_metadata("Object", reference_urn, "String", "username", user['username'])
    snapbundle_helpers.add_update_metadata("Object", reference_urn, "String", "full_name", user['full_name'])
    snapbundle_helpers.add_update_metadata("Object", reference_urn, "String", "profile_picture", user['profile_picture'])
    snapbundle_helpers.add_update_metadata("Object", reference_urn, "String", "bio", user['bio'])
    snapbundle_helpers.add_update_metadata("Object", reference_urn, "String", "website", user['website'])
    snapbundle_helpers.add_update_metadata("Object", reference_urn, "String", "counts", user['counts'])
    if new_user:
        snapbundle_helpers.add_update_metadata("Object", reference_urn, "Long", "last_instagram_added", 0)

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
def get_instagram_snapbundle_device_object_id(parent_object_urn, source):
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
