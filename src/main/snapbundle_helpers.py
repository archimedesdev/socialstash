__author__ = 'prad'

import json
import requests
import ConfigParser

# == Import all the account information that is stored in a local file (not sync'd wih public github)
config_file = 'accounts.txt'
config = ConfigParser.RawConfigParser()
config.read(config_file)

# == Snapbundle Variables ==
snapbundle_username = config.get('SnapbundleCredentials', 'snapbundle_username')
snapbundle_password = config.get('SnapbundleCredentials', 'snapbundle_password')
base_url_objects = 'https://snapbundle.tagdynamics.net/v1/app/objects'
base_url_object_interaction = 'https://snapbundle.tagdynamics.net/v1/app/interaction'
base_url_metadata_objects = 'https://snapbundle.tagdynamics.net/v1/app/metadata/Object'
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
    payload = str(var_passed_in)
    if payload == '':
        payload = 'NULL'
    headers = {'content-type': 'text/plain'}
    print "Get_raw_value: Submitting --> " + str(url) + " " + str(payload)
    response = requests.post(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    if response.status_code == '404':
        print "uh oh, 404 error!!"
    else:
        print "Get_raw_value: Encoded Response: " + str(response)
        print "Get_raw_value: Encoded Response JSON: " + str(response.json())
        return response.json()['rawValue']


## ----------------------------------- FXN ------------------------------------------------------------------------
def get_raw_value_decoded(var_passed_in, var_type):
    url = base_url_metadata_mapper_decode + metadataDataTypes[var_type.upper()]
    payload = {'rawValue': var_passed_in}
    payload = json.dumps(payload)
    headers = {'content-type': 'application/json'}
    print "Get_raw_value decoded: Submitting --> " + str(url) + " " + str(payload)
    response = requests.post(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    if response.status_code == '404':
        print "uh oh, 404 error!!"
    else:
        print "Get_raw_value: Decoded Response: " + str(response)
        print "Get_raw_value: Decoded Response JSON: " + str(response.json())
        return response.json()['rawValue']


## ----------------------------------- FXN ------------------------------------------------------------------------
def add_update_metadata(reference_type, referenceURN, dataType, key, value):
    raw_value = get_raw_value_encoded(value, dataType)
    temp_meta_data = dict(
        entityReferenceType=reference_type,
        referenceURN=referenceURN,
        dataType=metadataDataTypes[dataType.upper()],
        #type=metadataDataTypes[dataType.upper()],
        key=key,
        rawValue=str(raw_value)
    )
    url = base_url_metadata_objects + '/' + referenceURN
    headers = {'content-type': 'application/json'}
    payload = json.dumps([temp_meta_data])
    print "user: " + snapbundle_username
    print "pass: " + snapbundle_password
    print "Sending to URL: " + str(url)
    print "Submitting Payload: " + str(payload)
    response = requests.put(url, data=payload, headers=headers, auth=(snapbundle_username, snapbundle_password))
    print "Response: " + str(response.status_code) + " <--> "
    print response
    print str(response.json())

## ----------------------------------- END ------------------------------------------------------------------------
## ----------------------------------- END ------------------------------------------------------------------------

#raw = get_raw_value_encoded("True", "Boolean")
#val = get_raw_value_decoded(raw, "Boolean")
#add_update_metadata("Object", 'paulr:twitter:praddc', "String", "test_metadata", 'Test Successful')