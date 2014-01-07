__author__ = 'prad'

import json
import requests
import ConfigParser
import logging
import ast
import os
import urllib2
import poster.encode
import poster.streaminghttp

# == Start the logger ==
# == Because of this logger, this should be the first library we import ==
logging.basicConfig(filename='socialStash.log', level=logging.DEBUG, format='%(levelname)s: %(asctime)s [%(filename)s:%(lineno)s - %(funcName)20s()]: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

logging.debug('Starting: ' + __name__)
 # Reset the level of logging coming from the Requests library
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

# == Import all the account information that is stored in a local file (not sync'd wih public github)
config_file = 'accounts.txt'
config = ConfigParser.RawConfigParser()
config.read(config_file)

# == Local directories
cache_directory = 'cache' + os.sep + 'instagram'

# == Snapbundle Variables ==
snapbundle_username = config.get('SnapbundleCredentials', 'snapbundle_username')
snapbundle_password = config.get('SnapbundleCredentials', 'snapbundle_password')
snapbundle_user_object = config.get('SnapbundleCredentials', 'snapbundle_user_object')
base_url_server = 'snapbundle'
#base_url_server = 'stage'
url_server = 'http://' + base_url_server + '.tagdynamics.net:8080'
base_url_objects = url_server + '/objects'
base_url_object_interactions = url_server + '/interactions'
base_url_relationship = url_server + '/relationships'
base_url_relationship_query_object = url_server + '/relationships/Object'
base_url_metadata = url_server + '/metadata'
base_url_metadata_objects = url_server + '/metadata/Object'
base_url_metadata_mapper_encode = url_server + '/metadata/mapper/encode/'
base_url_metadata_mapper_decode = url_server + '/metadata/mapper/decode/'
base_url_files_metadata_query = url_server + '/files/Metadata/'
base_url_files = url_server + '/files'
# The application/octet-stream endpoint is located at a POST at /files/{urn}/octet
# If you want to continue to try and figure out the multi-part, the endpoint is at /files/{urn}/multipart
base_url_tags = url_server + '/tags'
base_url_geospatial = url_server + '/geospatial'
base_url_devices = url_server + '/devices'
# == End Snapbundle Variables ==

metadataDataTypes = {'STRING': 'StringType',
                     'STRINGTYPE': 'StringType',
                     'DATE': 'DataType',
                     'DATETYPE': 'DataType',
                     'INTEGER': 'IntegerType',
                     'INTEGERTYPE': 'IntegerType',
                     'LONG': 'LongType',
                     'LONGTYPE': 'LongType',
                     'BOOLEAN': 'BooleanType',
                     'BOOLEANTYPE': 'BooleanType',
                     'FLOAT': 'FloatType',
                     'FLOATTYPE': 'FloatType',
                     'DOUBLE': 'DoubleType',
                     'DOUBLETYPE': 'DoubleType',
                     'JSON': 'JSONType',
                     'JSONTYPE': 'JSONType',
                     'XML': 'XMLType',
                     'XMLTYPE': 'XMLType'
                     }


## ----------------------------------- FXN ------------------------------------------------------------------------
def check_for_objects_options(text, objectUrnLike=False, nameLike=False, monikerLike=False, modifiedAfter=False):
    #/objects?objectUrnLike=foo
    #/objects?nameLike=foo
    #/objects?monikerLike=foo&view=Full
    #/objects?modifiedAfter=1388629875
    if objectUrnLike:
        url = base_url_objects + '?objectUrnLike=' + text
    elif nameLike:
        url = base_url_objects + '?nameLike=' + text
    elif monikerLike:
        url = base_url_objects + '?monikerLike=' + text + "&view=Full"
    elif modifiedAfter:
        url = base_url_objects + '?modifiedAfter=' + text
    else:
        return False
    logging.info("Looking for object at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if (response.status_code == 404) or (response.status_code == 204):
            logging.info("No records found not found!")
            return False
        else:
            size = len(response.json())
            logging.info(str(size) + " Matching Objects Exist!!")
            return response.json()
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def check_for_object(urn_to_check_for):
    url = base_url_objects + '/object/' + urn_to_check_for
    logging.info("Looking for object at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if (response.status_code == 404) or (response.json()['objectUrn'] != urn_to_check_for):
            logging.info("ObjectURN not found!")
            return False
        else:
            logging.info("Object Exists!!")
            logging.info(response.json())
            return response.json()
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def add_update_object(name, objectUrn, objectType, description=None):
    json_info = {"name": name,
                 "active": "true",
                 "objectUrn": objectUrn,
                 "objectType": objectType,
                 "description": description
                 }
    url = base_url_objects
    headers = {'content-type': 'application/json'}
    payload = json.dumps(json_info)
    logging.info("Submitting Payload: " + str(payload))
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    logging.info("Response (for objectURN " + objectUrn + "): " + str(response.status_code) + " <--> " + str(response.json()))
    urn = response.json()['message']
    if response.status_code == 201:
        # Created new user
        logging.info("Created new object, urn=" + str(urn))
    elif response.status_code == 200:
        # Updating user
        logging.info("Object existed, updated, urn=" + str(urn))
    return urn


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_object(urn_to_check_for):
    url = base_url_objects + '/object/' + urn_to_check_for
    logging.info("Looking for object at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if (response.status_code == 404) or (response.json()['objectUrn'] != urn_to_check_for):
            logging.info("ObjectURN not found!")
            return False
        else:
            logging.info("Object Exists!!")
            logging.info(response.json())
            return response.json()
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_object_metadata(urn_to_check_for, reference_type):
    url = base_url_metadata + '/' + reference_type + '/' + urn_to_check_for + "?view=Full"
    logging.info("Looking for object metadata at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.status_code == 200:
            return response.json()
        else:
            return False
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_object_metadata_dictionary(urn_to_check_for, reference_type):
    url = base_url_metadata + '/' + reference_type + '/' + urn_to_check_for
    logging.info("Looking for object metadata at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.status_code == 200:
            temp_dict = {}
            for current in response.json():
                value = get_raw_value_decoded(current['rawValue'], str(current['dataType']))
                # Check to see if it's really a dictionary stored as a string
                # If so, clear off all the unicode u'' crap from the beginning
                if isinstance(value, basestring) and (value[0] == '{') and (value[-1] == '}'):
                    value = ast.literal_eval(value)
                    non_unicode_value = {}
                    for key in value.keys():
                        non_unicode_value[str(key)] = str(value[key])
                    value = non_unicode_value
                temp_dict[str(current['key'])] = value
            return temp_dict
        else:
            return False
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_raw_value_encoded(var_passed_in, var_type):
    url = base_url_metadata_mapper_encode + metadataDataTypes[var_type.upper()]
    try:
        if isinstance(var_passed_in, basestring):
            payload = var_passed_in.encode('utf-8')
        else:
            payload = str(var_passed_in)
    except UnicodeEncodeError:
        logging.critical("GAH, UnicodeEncodeError, don't know what to do!")
        payload = ''
        #payload = var_passed_in.encode("utf-8")
        #payload = unicode(var_passed_in, 'utf8')
    if payload == '':
        payload = 'NULL'
    headers = {'content-type': 'text/plain'}
    #print "Get_raw_value: Submitting --> " + str(url) + " " + str(payload)
    response = requests.post(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    if response.status_code == '404':
        logging.critical("uh oh, 404 error when trying to get raw value encoded!!")
    else:
        logging.debug("Get_raw_value: Encoded Response: " + str(response))
        logging.debug("Get_raw_value: Encoded Response JSON: " + str(response.json()))
        return response.json()['rawValue']


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_raw_value_decoded(var_passed_in, var_type):
    url = base_url_metadata_mapper_decode + metadataDataTypes[var_type.upper()]
    payload = {'rawValue': var_passed_in}
    payload = json.dumps(payload)
    headers = {'content-type': 'application/json'}
    #print "Get_raw_value decoded: Submitting --> " + str(url) + " " + str(payload)
    response = requests.post(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    if response.status_code == '404':
        logging.critical("uh oh, 404 error when trying to get raw value decoded!!")
    else:
        logging.debug("Get_raw_value: Decoded Response: " + str(response))
        logging.debug("Get_raw_value: Decoded Response JSON: " + str(response.json()))
        return response.json()['decodedValue']


## ----------------------------------- FXN ------------------------------------------------------------------------
def add_update_metadata(reference_type, referenceURN, dataType, key, value, moniker=None):
    # Moniker check test hopefully temp
    if moniker is None:
        # First need to see if this object even has any metadata, if not, don't want to cause a 500 response
        url = base_url_metadata + '/' + reference_type + '/' + referenceURN + '?view=Full'
        response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
        if response.status_code == 200:
            for list_item in response.json():
                if list_item['key'] == 'moniker':
                    moniker = list_item['rawValue']
                    break

    # Back to normal application

    # We need to check to make sure if it's a string type, that it's not too long.
    # If so, we need to store it as a text file
    # 1) Create the metadata with some placeholder value in the value, get the urn
    # 2) Create the file, referencing the urn of the metadata we made, get the urn for the file
    # 3) Update the metadata to have the urn of the file name in it
    contents_in_file = False
    if (metadataDataTypes[dataType.upper()] == 'StringType') and (len(value) > 512):
        logging.info("Found some metadata that was too long, ignoring for now!! --> ")
        print "Found some metadata that was too long, ignoring for now!! --> "
        return False
        new_value = '<contents_in_file_pending>'
        raw_value = get_raw_value_encoded(new_value, dataType)
        contents_in_file = True
        print "Text: " + str(value)
    else:
        raw_value = get_raw_value_encoded(value, dataType)

    temp_meta_data = dict(
        entityReferenceType=reference_type,
        referenceURN=referenceURN,
        dataType=metadataDataTypes[dataType.upper()],
        key=key,
        rawValue=str(raw_value)
    )

    if moniker is not None:
        temp_meta_data['moniker'] = moniker

    url = base_url_metadata + '/' + reference_type + '/' + referenceURN
    headers = {'content-type': 'application/json'}
    payload = json.dumps([temp_meta_data])
    logging.debug("Sending to URL: " + str(url))
    logging.debug("Submitting Payload: " + str(payload))
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    try:
        if response.status_code in (200, 201):
            logging.info("Response (for key/value " + str(key) + "/" + str(value) + "): " + str(response.status_code) + " <--> " + str(response.json()))
            metadata_urn = response.json()[0]['message']
            if contents_in_file:
                print "Metadata URN pre contents file doing: " + str(metadata_urn)
                text_filename = 'text_for_metadata_urn_' + str(metadata_urn) + '.txt'
                file_urn = add_file_from_text('Metadata', metadata_urn, text_filename, value)
                print "File_urn: " + str(file_urn)
                if file_urn:
                    new_value = '<contents_in_file_urn_' + str(file_urn) + '>'
                    newly_updated_metadata_urn = add_update_metadata(reference_type, referenceURN, dataType, key, new_value, moniker)
                    print "Metadata URN of post contents file doing: " + str(newly_updated_metadata_urn)
                    exit()
                    return newly_updated_metadata_urn
                else:
                    logging.info("Uh oh, something bad happened trying to add the file!")
                    return metadata_urn
            else:
                return metadata_urn
        else:
            return False
    except UnicodeEncodeError:
        logging.info("Response (for key/value " + str(key) + "/" + "UnicodeEncodeError Value Here" + "): " + str(response.status_code) + " <--> " + str(response.json()))
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def check_add_update_relationship(entityReferenceType, referenceURN, relationshipType, relatedEntityReferenceType, relatedReferenceURN):
    # First check to see if it exists before add/update
    url = base_url_relationship + '/' + entityReferenceType + '/' + referenceURN + '/' + relatedEntityReferenceType + '/' + relatedReferenceURN + '/' + relationshipType
    logging.debug("Checking for URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info("Response: " + str(response.status_code))
    if response.status_code in (204, 404):
        # Relationship doesn't exist, do it
        temp_meta_data = dict(
            entityReferenceType=entityReferenceType,
            referenceURN=referenceURN,
            relationshipType=relationshipType,
            relatedEntityReferenceType=relatedEntityReferenceType,
            relatedReferenceUrn=relatedReferenceURN
        )

        url = base_url_relationship + '/' + entityReferenceType + '/' + referenceURN
        headers = {'content-type': 'application/json'}
        payload = json.dumps(temp_meta_data)
        logging.debug("Sending to URL: " + str(url))
        logging.debug("Submitting Payload: " + str(payload))
        response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
        try:
            logging.info("Response (for relationship " + str(referenceURN) + " " + str(relationshipType) + " " + str(relatedReferenceURN) + "): " + str(response.status_code) + " <--> " + str(response.json()))
        except UnicodeEncodeError:
            logging.info("Response (for relationship " + str(referenceURN) + " " + str(relationshipType) + " " + str(relatedReferenceURN) + "): " + str(response.status_code) + " <--> " + str(response.json()))
    elif response.status_code == 200:
        return True
    elif response.status_code == 201:
        return True
    else:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_object_relationship_urn_list(urn_to_check_for, relationship, reverse=False):
    url = base_url_relationship_query_object + '/' + urn_to_check_for + '/' + relationship
    # Reverse happens when we want to see who have that relationship with US, not who we have the relationship with
    # For example: We send in the URN of a post, and want to see who Likes the Post Object, not who the Post Likes
    if reverse:
        url += '?reverse=true'

    logging.info("Looking for object relationships at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.status_code == 200:
            temp_dict = {}
            for current in response.json():
                if reverse:
                    value = str(current['referenceURN'])
                else:
                    value = str(current['relatedReferenceURN'])
                temp_dict[str(value)] = str(current['urn'])
            return temp_dict
        else:
            return {}
    except KeyError:
        return {}


## ----------------------------------- FXN ------------------------------------------------------------------------
def delete_relationship(urn_to_delete):
    url = base_url_relationship + '/' + urn_to_delete
    logging.info("Looking to delete relationship at URL: " + str(url))
    response = requests.delete(url, auth=(snapbundle_username, snapbundle_password))
    logging.info("Response for url (" + str(url) + "): " + str(response.status_code))
    if response.status_code == 204:
        return True
    else:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def create_object_interaction(entityReferenceType, entityUrn, recordedTimestamp, interactedUrn):
    # Back to normal application
    temp_meta_data = {"entityReferenceType": entityReferenceType,
                      "objectUrn": entityUrn,
                      "recordedTimestamp": recordedTimestamp,
                      "referenceUrn": interactedUrn,
                      "data": interactedUrn
                     }
    url = base_url_object_interactions
    headers = {'content-type': 'application/json'}
    #payload = temp_meta_data
    payload = json.dumps(temp_meta_data)
    logging.debug("Sending to URL: " + str(url))
    logging.debug("Submitting Payload: " + str(payload))
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    logging.info("Response (for objectInteractionURN " + str(interactedUrn) + "): " + str(response.status_code) + " <--> " + str(response.json()))
    urn = response.json()['message']
    if response.status_code == 201:
        # Created new user
        logging.info("Created new interaction, urn=" + str(urn))
    return urn


## ----------------------------------- FXN ------------------------------------------------------------------------
def check_object_interactions_for_urn(data_search):
    url = base_url_object_interactions + "?dataLike=" + data_search + "%25"
    logging.info("Looking for object interactions at url: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.status_code == 200:
            return response.json()[0]['urn']
        elif response.status_code == 204:
            return False
        else:
            return False
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_object_interactions(urn_to_check_for):
    url = base_url_object_interactions + "?objectUrn=" + urn_to_check_for
    logging.info("Looking for object interactions at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.status_code == 200:
            return response.json()
        else:
            return False
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def add_file_from_text(reference_type, referenceURN, text_filename, text):
    mimeType = 'text/plain'
    temp_data = {"entityReferenceType": reference_type,
                 "referenceUrn": referenceURN,
                 "mimeType": mimeType}
    url = base_url_files
    headers = {'content-type': 'application/json'}
    payload = json.dumps(temp_data)
    logging.debug("Sending to URL: " + str(url))
    logging.debug("Submitting Payload: " + str(payload))
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    logging.info("Response for url, before uploading content (" + str(url) + "): " + str(response.status_code) + " <--> " + str(response.json()))
    if response.status_code in (200, 201):
        file_urn = response.json()['message']
        # Now we need to upload the actual file
        url = base_url_files + '/' + str(file_urn)
        headers = {'content-type': 'multipart/form-data', 'Accept': 'application/json'}
        files = {'file': ('no_name.txt', open('test.txt'), 'text/plain', {})}
        print str(file_urn)
        print str(url)
        print str(headers)
        print str(files)
        response = requests.post(url, headers=headers, files=files, auth=(snapbundle_username, snapbundle_password))
        if response.status_code in (200, 201):
            logging.info("Response uploading file, for url (" + str(url) + "): " + str(response.status_code) + " <--> " + str(response.json()))
            print response.status_code
            print response.text
            return file_urn
        else:
            print response.headers
            print response.text
            exit()
            return False
    else:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def add_file_from_file(reference_type, referenceURN, mimeType, filename):
    temp_data = {"entityReferenceType": reference_type,
                 "referenceUrn": referenceURN,
                 "mimeType": mimeType}
    url = base_url_files
    headers = {'content-type': 'application/json'}
    payload = json.dumps(temp_data)
    logging.debug("Sending to URL: " + str(url))
    logging.debug("Submitting Payload: " + str(payload))
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    logging.info("Response for url, before uploading content (" + str(url) + "): " + str(response.status_code) + " <--> " + str(response.json()))
    if response.status_code in (200, 201):
        file_urn = response.json()['message']
        # Now we need to upload the actual file
        url = base_url_files + '/' + str(file_urn) + '/octet'
        data = open(filename, 'rb').read()
        headers = {'Content-Type': 'application/octet-stream'}
#        headers = {'Accept': 'application/json'}
#        files = {'file': ('', open(filename), mimeType, {})}
#        print "File URN: " + str(file_urn)
#        print "URL: " + str(url)
#        print "Headers: " + str(headers)
#        print "Filename: " + str(filename)
        #response = requests.post(url, headers=headers, files=files, auth=(snapbundle_username, snapbundle_password))
        response = requests.post(url=url, data=data, headers=headers, auth=(snapbundle_username, snapbundle_password))
        if response.status_code in (200, 201):
            logging.info("Response uploading file, for url (" + str(url) + "): " + str(response.status_code) + " <--> " + str(response.json()))
            print response.status_code
            print response.text
            return file_urn
        else:
            print "Return: " + str(response.headers)
            print "Return: " + str(response.text)
            exit()
            return False
    else:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
## ----------------------------------- FXN ------------------------------------------------------------------------
def add_file_from_url(reference_type, referenceURN, mimeType, source_url):
    temp_data = {"entityReferenceType": reference_type,
                 "referenceUrn": referenceURN,
                 "mimeType": mimeType,
                 "contentUrl": source_url}
    url = base_url_files
    headers = {'content-type': 'application/json'}
    payload = json.dumps(temp_data)
    #print payload
    logging.debug("Sending to URL: " + str(url))
    logging.debug("Submitting Payload: " + str(payload))
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    #print response
    logging.info("Response for url (" + str(url) + "): " + str(response.status_code) + " <--> " + str(response.json()))
    if response.status_code in (200, 201):
        return response.json()['message']
    else:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def add_file_from_url_jpg(reference_type, referenceURN, source_url):
    return add_file_from_url(reference_type, referenceURN, "image/jpeg", source_url)


## ----------------------------------- FXN ------------------------------------------------------------------------
def add_file_from_url_mp4(reference_type, referenceURN, source_url):
    return add_file_from_url(reference_type, referenceURN, "video/mp4", source_url)


## ----------------------------------- FXN ------------------------------------------------------------------------
def search_for_file_object(reference_type, reference_urn):
    # returns a dictionary of urns and timestamps
    url = base_url_files + "/" + reference_type + "/" + reference_urn
    logging.info("Looking for file objects at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if (response.status_code == 200) and (response.json() != {}):
            return_dict = {}
            for current in response.json():
                return_dict[current['timestamp']] = current['urn']
            return return_dict
        else:
            return False
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_file_object(file_urn):
    url = base_url_files + "/" + file_urn
    logging.info("Looking for file object at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.status_code == 200:
            return response.json()
        else:
            return False
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_file_object_contents(file_urn, check_cache=False):
    url = base_url_files + "/" + file_urn + "/contents"
    logging.info("Looking for file object at URL: " + str(url))
#   It's crucial that we add the "stream=True" part to the following response request.
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password), stream=True)
    logging.info(str(response))
    try:
        if response.status_code == 200:
            content_disposition = response.headers['content-disposition']
            index = content_disposition.index('filename="') + 10
            r_fileName, r_fileExtension = os.path.splitext(content_disposition[index:-1])
            fileName_use = r_fileName.split('/')
            fileName_use = fileName_use[len(fileName_use)-1]
            outFilePath = cache_directory + os.sep + fileName_use + r_fileExtension
            # If we want to use the cache, and the file already exists there, just use it
            if check_cache:
                logging.debug("Checked cache for file: " + outFilePath)
                if os.path.isfile(outFilePath):
                    logging.debug("Found file " + outFilePath + " in cache!  Not re-downloading it!")
                    return outFilePath
                else:
                    logging.debug("File " + outFilePath + " NOT found in cache!")

            logging.debug("Pulling file: " + fileName_use + r_fileExtension + " from stream")
            with open(outFilePath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()
            logging.info("Successfully wrote file: " + outFilePath)
            return outFilePath
        else:
            return ''
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def create_tag_association(entity_reference_type, reference_urn, name):
    temp_data = dict(name=name)
    url = base_url_tags + "/" + entity_reference_type + "/" + reference_urn
    headers = {'content-type': 'application/json'}
    payload = json.dumps([temp_data])
    logging.debug("Sending to URL: " + str(url))
    logging.debug("Submitting Payload: " + str(payload))
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    logging.info("Response for tag association of (" + entity_reference_type + '/' + reference_urn + "): " + str(response.status_code) + " <--> " + str(response.json()))
    if response.status_code in (200, 201):
        return True
    else:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_all_tags_linked_to_object(entity_reference_type, reference_urn):
    url = base_url_tags + "?entityReferenceType=" + entity_reference_type + "&referenceUrn=" + reference_urn
    logging.debug("Sending to URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.status_code == 200:
            return response.json()
        else:
            return False
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_all_objects_linked_to_tag(entity_reference_type, tag_name):
    url = base_url_tags + "?entityReferenceType=" + entity_reference_type + "&tagName=" + tag_name
    logging.debug("Sending to URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.status_code == 200:
            return response.json()
        else:
            return False
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def create_geospacial(name, description, georectificationType, geometricShape):
    temp_meta_data = {"name": name,
                      "description": description,
                      "georectificationType": georectificationType,
                      "geometricShape": geometricShape
                      }
    url = base_url_geospatial
    headers = {'content-type': 'application/json'}
    payload = json.dumps(temp_meta_data)
    logging.debug("Sending to URL: " + str(url))
    logging.debug("Submitting Payload: " + str(payload))
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    logging.info("Response (for geospacial name " + str(name) + "): " + str(response.status_code) + " <--> " + str(response.json()))
    urn = response.json()['message']
    if response.status_code == 201:
        # Created new place
        logging.info("Created new place, urn=" + str(urn))
    return urn


## ----------------------------------- FXN ------------------------------------------------------------------------
def create_geospacial_place(name, description, geometricShape):
    return create_geospacial(name=name, description=description,
                             georectificationType='Place', geometricShape=geometricShape)


## ----------------------------------- FXN ------------------------------------------------------------------------
def create_geospacial_place_point(name, description, x, y):
    temp_geo_json = {"type": 'Point',
                     "coordinates": [float(x), float(y)]
                     }
    return create_geospacial_place(name=name, description=description, geometricShape=temp_geo_json)


## ----------------------------------- FXN ------------------------------------------------------------------------
def check_or_create_geospacial_place_point(name, description, x, y):
    url = base_url_geospatial + "?nameLike=" + name
    logging.info("Looking for file geospacial object at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.status_code == 200:
            return response.json()[0]['urn']
        else:
            return create_geospacial_place_point(name, description, x, y)
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def check_geospacial_by_name(search_name):
    url = base_url_geospatial + "?nameLike=" + search_name
    logging.info("Looking for file geospacial object at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.status_code == 200:
            return response.json()
        else:
            return False
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def check_geospacial_by_urn(search_urn):
    url = base_url_geospatial + "/" + search_urn
    logging.info("Looking for file geospacial object at URL: " + str(url))
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    logging.info(str(response))
    try:
        if response.status_code == 200:
            return response.json()
        else:
            return False
    except KeyError:
        return False


## ----------------------------------- FXN ------------------------------------------------------------------------
def count_objects():
    url = base_url_objects
    count = 0
    response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
    for record in response.json():
        count += 1
    return response.json()

## ----------------------------------- END ------------------------------------------------------------------------
## ----------------------------------- END ------------------------------------------------------------------------

#urn = add_file_from_file('Object', 'urn:instagram:user:praddc', 'image/jpeg', 'test.jpg')

#count_objects()

#raw = get_raw_value_encoded("True", "Boolean")
#print raw
#val = get_raw_value_decoded("Nzk4NjM1Ng==", "String")
#print val
#add_update_metadata("Object", 'paulr:twitter:praddc', "String", "test_metadata", 'Test Successful')

#urn_to_check_for = snapbundle_user_object + ":twitter:" + "praddc"
#print "Looking for URN: " + str(urn_to_check_for)
#response = requests.get(base_url_objects + '/' + urn_to_check_for, auth=(snapbundle_username, snapbundle_password))
#print response.json()

#urn_to_check_for = snapbundle_user_object + ":twitter:" + "praddc"
#url = base_url_object_interaction + '/' + 'urn:uuid:3f893a56-f145-46f8-9b32-17d515190df9' #urn_to_check_for
#print response.json()['moniker']

#urn_to_check_for = snapbundle_user_object + ":instagram:" + "praddc"
#url = base_url_metadata_objects_query + '/' + urn_to_check_for + "/id"
#print "Looking at URL: " + str(url)
#response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
##logging.debug(response.json())
#print response
#exit()
#temp = list((response.json()))
#for item in temp:
#    print str(item)
#    url = base_url_metadata_objects + '/Object/' + urn_to_check_for + "/urn:uuid:e9894cb1-e7ea-4be9-9830-40054302cda7"    #urn_to_check_for
#    print "Looking at URL: " + str(url)
#    #response = requests.delete(url, auth=(snapbundle_username, snapbundle_password))
#    exit()
