__author__ = 'prad'

import ConfigParser
import ast
import requests
import snapbundle_instagram_fxns
import socialstash_instagram
import logging

logging.debug('Starting: ' + __name__)

# == Import all the account information that is stored in a local file (not sync'd wih public github)
config_file = 'accounts.txt'
config = ConfigParser.RawConfigParser()
config.read(config_file)

# == Instagram OAuth Authentication ==
# This mode of authentication is the new preferred way
# of authenticating with Twitter.
pr_client_id = config.get('InstagramApplicationAccounts', 'clientID')
pr_client_secret = config.get('InstagramApplicationAccounts', 'clientSecret')
instagrame_access_tokens = ast.literal_eval(config.get('InstagramUserOAuthTokens', 'instagram_access_tokens'))
# == End Twitter OAuth Authentication ==

# == Snapbundle Variables ==
snapbundle_username = config.get('SnapbundleCredentials', 'snapbundle_username')
snapbundle_password = config.get('SnapbundleCredentials', 'snapbundle_password')
snapbundle_user_object = 'paulr'
# == End Snapbundle Variables ==


#---------------------------------------------------------------------------------------------------------------------
#instagram_handle = 'AnEloquentDane'
instagram_handle = 'praddc'

instagram_user = socialstash_instagram.User(access_token = instagrame_access_tokens[instagram_handle]['access_token'])


urn_to_check_for = "urn:" + snapbundle_user_object + ":instagram:" + instagram_handle
logging.info("Looking for URN: " + str(urn_to_check_for))
response = requests.get(snapbundle_base_url_objects + '/' + urn_to_check_for, auth=(snapbundle_username, snapbundle_password))
try:
    if response.json()['objectUrn'] != urn_to_check_for:
        logging.info("ObjectURN not found!")
    else:
        logging.info("Object Exists!!")
        logging.info(response.json())
except KeyError:
    logging.info("Instagram user Object does not yet exist in SnapBundle, creating...")
    instagram_user_sb_urn = snapbundle_instagram_fxns.add_new_instagram_user_object(instagram_handle, snapbundle_user_object, instagram_handle + "'s Instagram Account")



logging.info("Creating/Updating Instagram user data in Snapbundle")
snapbundle_instagram_fxns.update_instagram_user_object(instagram_user_sb_urn, userData)

exit()
