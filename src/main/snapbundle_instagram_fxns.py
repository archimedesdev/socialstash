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
base_url_object_interaction = snapbundle_helpers.base_url_object_interactions
base_url_metadata_objects = snapbundle_helpers.base_url_metadata_objects
base_url_devices = snapbundle_helpers.base_url_devices
# == End Snapbundle URLs ==

global_following_string = 'FOLLOWING'
global_followed_by_string = 'FOLLOWED_BY'
global_likes_string = 'LIKES'

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
def get_object_metadata(urn_to_check_for, reference_type='Object'):
    return_value = snapbundle_helpers.get_object_metadata(urn_to_check_for, reference_type)
    if not return_value:
        logging.info("Instagram user Object Metadata (" + str(urn_to_check_for) + ") does not yet exist in SnapBundle")
    return return_value


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_object_metadata_dictionary(urn_to_check_for):
    return_value = snapbundle_helpers.get_object_metadata_dictionary(urn_to_check_for, 'Object')
    if not return_value:
        logging.info("Instagram user Object Metadata (" + str(urn_to_check_for) + ") does not yet exist in SnapBundle")
    return return_value


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def check_update_user_profile_pic(username, current_pic_url):
    url = snapbundle_helpers.base_url_metadata + '/Object/' + snapbundle_base_urn_instagram_user + username + "?key=profile_picture&view=Full"
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
                file_urns = snapbundle_helpers.search_for_file_object('Metadata', existing_stored_urn)
                if not file_urns:
                    logging.info("No associated file urns found, need to upload the file")
                    need_to_upload_url = True
                else:
                    logging.info(str(len(file_urns)) + " Associated files found.")
            else:
                # Need to create a new File object with this picture
                need_to_upload_url = True

            #need_to_upload_url = True # for testing only
            if need_to_upload_url:
                file_urn = snapbundle_helpers.add_file_from_url_jpg("Metadata", existing_stored_urn, current_pic_url)
                if not file_urn:
                    logging.info("File could not be uploaded for some reason.")
                    return 'n/a'
                else:
                    logging.info("File uploaded, urn: " + file_urn)
                    return file_urn
        else:
            return False
    except KeyError:
        logging.info("Instagram user Object Profile Pic Metadata does not yet exist in SnapBundle")
        return False


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def get_object_relationships(urn_to_check_for, relationship, reverse=False):
    if relationship.upper() == global_followed_by_string:
        relationship = 'FollowedBy'
    elif relationship.upper() == global_following_string:
        relationship = 'Follows'
    elif relationship.upper() == global_likes_string:
        relationship = 'Likes'

    if reverse:
        temp_dict = snapbundle_helpers.get_object_relationship_urn_list(urn_to_check_for, relationship, reverse=True)
    else:
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
        snapbundle_helpers.create_tag_association("Object", referenceURN, tag)


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def set_filter_tag(referenceURN, filter_name):
    tag_name = snapbundle_base_instagram_filter_name + filter_name.upper()
    return snapbundle_helpers.create_tag_association("Object", referenceURN, tag_name)


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def get_tag_list_by_post(post_urn):
    response = snapbundle_helpers.get_all_tags_linked_to_object('Object', post_urn)
    tag_list = {}
    if response:
        for current in response:
            tag_list[current['tag']['name']] = current['tag']['urn']
    return tag_list


## --------------------------------------------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def add_update_new_instagram_user_object(instagram_handle, instagram_user_sb_object_urn):
    return snapbundle_helpers.add_update_object(instagram_handle, instagram_user_sb_object_urn, "Person",
                                                description='Instagram User')


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
def check_add_update_followed_by(reference_urn, relatedReferenceURN):
    return snapbundle_helpers.check_add_update_relationship('Object', reference_urn, 'FollowedBy', 'Object', relatedReferenceURN)


## ----------------------------------- FXN ------------------------------------------------------------------------
def check_add_update_follows(reference_urn, relatedReferenceURN):
    return snapbundle_helpers.check_add_update_relationship('Object', reference_urn, 'Follows', 'Object', relatedReferenceURN)


## ----------------------------------- FXN ------------------------------------------------------------------------
def add_user_likes_post(user_urn, post_urn):
    return snapbundle_helpers.check_add_update_relationship('Object', user_urn, 'Likes', 'Object', post_urn)


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_urn_from_username(username):
    return snapbundle_base_urn_instagram_user + username


## ----------------------------------- FXN ------------------------------------------------------------------------
def check_for_file_upload_url(referenceType, urn, url):
    file_urns = snapbundle_helpers.search_for_file_object(referenceType, urn)
    if not file_urns:
        logging.info("No associated file urns found for " + urn + ", need to upload the file")
        file_urn = snapbundle_helpers.add_file_from_url_jpg(referenceType, urn, url)
        if not file_urn:
            logging.info("File could not be uploaded for some reason.")
            return 'n/a'
        else:
            logging.info("File uploaded, urn: " + file_urn)
            return file_urn
    else:
        logging.info(str(len(file_urns)) + " Associated files found.")


## ----------------------------------- FXN ------------------------------------------------------------------------
def add_new_instagram_post_object(post):
    data_urn = snapbundle_base_urn_instagram_post + post['id']

    # First check to see if the Post Object Interaction exists.  If so, get its URN
    post_object_urn = snapbundle_base_urn_instagram_post + post['id']
    post_urn = snapbundle_helpers.add_update_object(name=post['id'], objectUrn=post_object_urn, objectType='Post',
                                                    description='Instagram Post')
    # Now we need to start adding all the additional data
    snapbundle_helpers.add_update_metadata("Object", post_urn, "String", "id", post['id'])
    snapbundle_helpers.add_update_metadata("Object", post_urn, "String", "created_time", post['created_time'])
    snapbundle_helpers.add_update_metadata("Object", post_urn, "String", "type", post['type'])
    snapbundle_helpers.add_update_metadata("Object", post_urn, "Boolean", "user_has_liked", post['user_has_liked'])

    # Take care of the pictures and videos
    if post['type'] == 'image':
        pic_url = post['images']['low_resolution']['url']
        metadata_urn = snapbundle_helpers.add_update_metadata("Object", post_urn, "String", "image:low_resolution", pic_url)
        file_urn = check_for_file_upload_url('Metadata', metadata_urn, pic_url)

        pic_url = post['images']['thumbnail']['url']
        metadata_urn = snapbundle_helpers.add_update_metadata("Object", post_urn, "String", "image:thumbnail", pic_url)
        file_urn = check_for_file_upload_url('Metadata', metadata_urn, pic_url)

        pic_url = post['images']['standard_resolution']['url']
        metadata_urn = snapbundle_helpers.add_update_metadata("Object", post_urn, "String", "image:standard_resolution", pic_url)
        file_urn = check_for_file_upload_url('Metadata', metadata_urn, pic_url)
    elif post['type'] == 'video':
        pic_url = post['videos']['low_resolution']['url']
        metadata_urn = snapbundle_helpers.add_update_metadata("Object", post_urn, "String", "video:low_resolution", pic_url)
        file_urn = check_for_file_upload_url('Metadata', metadata_urn, pic_url)

        pic_url = post['videos']['standard_resolution']['url']
        metadata_urn = snapbundle_helpers.add_update_metadata("Object", post_urn, "String", "video:standard_resolution", pic_url)
        file_urn = check_for_file_upload_url('Metadata', metadata_urn, pic_url)

    # Now add the tags, including the filters:
    filter_tag = snapbundle_base_instagram_filter_name + post['filter']
    snapbundle_helpers.create_tag_association('Object', post_urn, filter_tag)
    for tag in post['tags']:
        snapbundle_helpers.create_tag_association('Object', post_urn, tag)

    # Now let's add the Like relationships
    snapbundle_helpers.add_update_metadata("Object", post_urn, "Integer", "likes_count", post['likes']['count'])

    # Now we need to see if the Interaction already exists:
    interaction_urn = snapbundle_helpers.check_object_interactions_for_urn(post_urn)

    if not interaction_urn:
        # Now we need to create an Interaction between the parent object and this post object
        interaction_urn = snapbundle_helpers.create_object_interaction('Object', post['parent_urn'],
                                                                       post['created_time'], post_urn)

    print "posturn: " + str(post_urn)
    print "inerurn: " + str(interaction_urn)
    return post_urn


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
