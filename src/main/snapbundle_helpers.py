__author__ = 'prad'

import json
import requests
import ConfigParser
import logging

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

# == Snapbundle Variables ==
snapbundle_username = config.get('SnapbundleCredentials', 'snapbundle_username')
snapbundle_password = config.get('SnapbundleCredentials', 'snapbundle_password')
snapbundle_user_object = config.get('SnapbundleCredentials', 'snapbundle_user_object')
base_url_objects = 'https://snapbundle.tagdynamics.net/v1/app/objects'
base_url_object_interaction = 'https://snapbundle.tagdynamics.net/v1/app/interactions'
base_url_metadata_objects = 'https://snapbundle.tagdynamics.net/v1/app/metadata/Object'
base_url_metadata_objects_query = 'https://snapbundle.tagdynamics.net/v1/app/metadata/query/Object'
base_url_metadata_mapper_encode = 'https://snapbundle.tagdynamics.net/v1/public/metadata/mapper/encode/'
base_url_metadata_mapper_decode = 'https://snapbundle.tagdynamics.net/v1/public/metadata/mapper/decode/'
base_url_devicess = 'https://snapbundle.tagdynamics.net/v1/admin/devices'
# == End Snapbundle Variables ==

metadataDataTypes = {'STRING': 'StringType',
                     'DATE': 'DataType',
                     'INTEGER': 'IntegerType',
                     'LONG': 'LongType',
                     'BOOLEAN': 'BooleanType',
                     'FLOAT': 'FloatType',
                     'DOUBLE': 'DoubleType',
                     'JSON': 'JSONType',
                     'XML': 'XMLType'
                     }


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_raw_value_encoded(var_passed_in, var_type):
    url = base_url_metadata_mapper_encode + metadataDataTypes[var_type.upper()]
    try:
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
        return response.json()['rawValue']


## ----------------------------------- FXN ------------------------------------------------------------------------
def add_update_metadata(reference_type, referenceURN, dataType, key, value):
    raw_value = get_raw_value_encoded(value, dataType)
    temp_meta_data = dict(
        entityReferenceType=reference_type,
        referenceURN=referenceURN,
        dataType=metadataDataTypes[dataType.upper()],
        key=key,
        rawValue=str(raw_value)
    )
    url = base_url_metadata_objects + '/' + referenceURN
    headers = {'content-type': 'application/json'}
    payload = json.dumps([temp_meta_data])
    logging.debug("Sending to URL: " + str(url))
    logging.debug("Submitting Payload: " + str(payload))
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    try:
        logging.info("Response (for key/value " + str(key) + "/" + str(value) + "): " + str(response.status_code) + " <--> " + str(response.json()))
    except UnicodeEncodeError:
        logging.info("Response (for key/value " + str(key) + "/" + "UnicodeEncodeError Value Here" + "): " + str(response.status_code) + " <--> " + str(response.json()))

## ----------------------------------- END ------------------------------------------------------------------------
## ----------------------------------- END ------------------------------------------------------------------------

#raw = get_raw_value_encoded("True", "Boolean")
#print raw
#val = get_raw_value_decoded(raw, "Boolean")
#add_update_metadata("Object", 'paulr:twitter:praddc', "String", "test_metadata", 'Test Successful')

#urn_to_check_for = snapbundle_user_object + ":twitter:" + "praddc"
#print "Looking for URN: " + str(urn_to_check_for)
#response = requests.get(base_url_objects + '/' + urn_to_check_for, auth=(snapbundle_username, snapbundle_password))
#print response.json()

#urn_to_check_for = snapbundle_user_object + ":twitter:" + "praddc"
#url = base_url_object_interaction + '/' + 'urn:uuid:3f893a56-f145-46f8-9b32-17d515190df9' #urn_to_check_for
#print "Looking at URL: " + str(url)
#response = requests.get(url, auth=(snapbundle_username, snapbundle_password))
#print response.json()
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
