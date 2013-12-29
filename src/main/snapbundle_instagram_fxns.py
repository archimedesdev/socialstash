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
snapbundle_base_urn_instagram = "urn:instagram:"
snapbundle_base_urn_instagram_user = snapbundle_base_urn_instagram + "users:"
snapbundle_base_urn_instagram_post = snapbundle_base_urn_instagram + "posts:"
snapbundle_base_instagram_filter_name = "instagram:filters:"
# == End Snapbundle Variables ==

# == Start Snapbundle URLs ==
base_url_object_interaction = snapbundle_helpers.base_url_object_interaction
base_url_metadata_objects = snapbundle_helpers.base_url_metadata_objects
base_url_metadata_objects_query = snapbundle_helpers.base_url_metadata_objects_query
base_url_devicess = snapbundle_helpers.base_url_devicess
# == End Snapbundle URLs ==


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def check_for_object(urn_to_check_for):
    return_value = snapbundle_helpers.check_for_object(urn_to_check_for)
    if not return_value:
        logging.info("Instagram user Object (" + str(urn_to_check_for) + ") does not yet exist in SnapBundle")
    return return_value


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def get_object(urn_to_check_for):
    return_value = snapbundle_helpers.get_object(urn_to_check_for)
    if not return_value:
        logging.info("Instagram user Object (" + str(urn_to_check_for) + ") does not yet exist in SnapBundle")
    return return_value


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def get_object_metadata(urn_to_check_for):
    return_value = snapbundle_helpers.get_object_metadata(urn_to_check_for)
    if not return_value:
        logging.info("Instagram user Object Metadata (" + str(urn_to_check_for) + ") does not yet exist in SnapBundle")
    return return_value


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_object_metadata_dictionary(urn_to_check_for):
    return_value = snapbundle_helpers.get_object_metadata_dictionary(urn_to_check_for)
    if not return_value:
        logging.info("Instagram user Object Metadata (" + str(urn_to_check_for) + ") does not yet exist in SnapBundle")
    return return_value


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def check_update_user_profile_pic(username, current_pic_url):
    url = base_url_metadata_objects_query + '/' + snapbundle_base_urn_instagram_user + username + "?key=profile_picture&view=Full"
    logging.info("Looking for object profile pic metadata at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response.json()))
    try:
        if response.status_code == 200:
            logging.info("Profile Pic Metadata Exists for User " + username)
            # The URL metadata exists, as it should, now let's:
            # 1) Decode the existing value and compare it to the value passed in
            # 2) If the value is the same, make sure the actual file lives in SnapBundle
            # 3) If the value is different, we need to create a new File object in SnapBundle, and get the file in there
            existing_stored_urn = str(response.json()['urn'])
            existing_stored_url = snapbundle_helpers.get_raw_value_decoded(response.json()['rawValue'], 'String')
            need_to_upload_url = False
            if existing_stored_url == current_pic_url:
                logging.info("Existing stored profile pic URL matches current URL for user " + username + ".  Checking to see if file exists in SnapBundle")
                # Check to see if a file exists in SB for this
                try:
                    existing_stored_file_urn = str(response.json()['moniker'])
                    if existing_stored_file_urn in ("None", ''):
                        logging.info("Moniker key not set in metadata: No file urn found, need to upload the file")
                        need_to_upload_url = True
                    else:
                        logging.info("Moniker found.  Existing profile pic urn: " + str(existing_stored_file_urn))
                except KeyError:
                    logging.info("Moniker key not set in metadata: No file urn found, need to upload the file")
                    need_to_upload_url = True
            else:
                # Need to create a new File object with this picture
                need_to_upload_url = True

            need_to_upload_url = True
            if need_to_upload_url:
                file_urn = snapbundle_helpers.add_file_from_url_jpg("Metadata", existing_stored_urn, current_pic_url)
                if not file_urn:
                    logging.info("File could not be uploaded for some reason.")
                    return 'n/a'
                else:
                    logging.info("File uploaded, urn: " + file_urn)
                    reference_urn = snapbundle_base_urn_instagram_user + username
                    logging.info("Updating profile pic metadata to include latest file urn")
                    snapbundle_helpers.add_update_metadata("Object", reference_urn, "String", "profile_picture", current_pic_url, file_urn)
                    return file_urn
        else:
            return False
    except KeyError:
        logging.info("Instagram user Object Profile Pic Metadata does not yet exist in SnapBundle")
        return False


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def get_object_relationships(urn_to_check_for, relationship):
    following_string = 'FOLLOWING'
    followed_by_string = 'FOLLOWED_BY'
    if relationship.upper() == followed_by_string:
        relationship = 'FollowedBy'
    elif relationship.upper() == following_string:
        relationship = 'Follows'

    temp_dict = snapbundle_helpers.get_object_relationship_urn_list(urn_to_check_for, relationship)
    # we're going to remove the prefix to the instagram user names here
    return_dict = {}
    for current in temp_dict.keys():
        reduced = current.replace(snapbundle_base_urn_instagram_user, '')
        return_dict[reduced] = temp_dict[current]
    return return_dict


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def delete_relationship(urn_to_delete):
    return snapbundle_helpers.delete_relationship(urn_to_delete)


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def set_instagram_tags(referenceURN, tag_list):
    for tag in tag_list:
        snapbundle_helpers.create_tag_association("ObjectAssociation", referenceURN, tag)


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def set_filter_tag(referenceURN, filter_name):
    tag_name = snapbundle_base_instagram_filter_name + filter_name.upper()
    return snapbundle_helpers.create_tag_association("ObjectAssociation", referenceURN, tag_name)


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def add_update_new_instagram_user_object(instagram_handle, instagram_user_sb_object_urn):
    return snapbundle_helpers.add_update_object(instagram_handle, instagram_user_sb_object_urn, "Person")


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
def add_update_new_instagram_post_object(post):

    if post['location'] is None:
        hasGeo = False
    else:
        hasGeo = True

    moniker = snapbundle_base_urn_instagram_post + ":" + post['id']
    object_interaction = {'objectUrn': post['parent_urn'],
                          'moniker': moniker,
                          'identification': moniker,
                          'data': post['link'],
                          'recordedTimestamp': post['created_time'],
                          'hasGeoLocation': hasGeo,
                          'lat': '',
                          'lon': '',
                          'alt': ''
                          }

    url = base_url_object_interaction
    headers = {'content-type': 'application/json'}
    payload = json.dumps(object_interaction)
    print "Sending to URL: " + str(url)
    print "Submitting Payload: " + str(payload)
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    logging.info("Response (for objectURN " + moniker + "): " + str(response.status_code) + " <--> " + str(response.json()))
    if response.status_code == 201:
        # Created new user
        logging.info("Created new post")
    elif response.status_code == 200:
        # Updating user
        logging.info("Post existed")
    post_urn = response.json()['message']

    ## -- The additional metadata portion of the tweet


## ----------------------------------- FXN ------------------------------------------------------------------------
def check_add_update_followed_by(reference_urn, relatedReferenceURN):
    return snapbundle_helpers.check_add_update_relationship('Object', reference_urn, 'FollowedBy', 'Object', relatedReferenceURN)


## ----------------------------------- FXN ------------------------------------------------------------------------
def check_add_update_follows(reference_urn, relatedReferenceURN):
    return snapbundle_helpers.check_add_update_relationship('Object', reference_urn, 'Follows', 'Object', relatedReferenceURN)


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_urn_from_username(username):
    return snapbundle_base_urn_instagram_user + username



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
