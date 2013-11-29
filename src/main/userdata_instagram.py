__author__ = 'prad'

import ConfigParser
import ast
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

print "Creating SocialStash Instagram User"
instagram_user = socialstash_instagram.User(access_token=instagrame_access_tokens[instagram_handle]['access_token'],
                                            snapbundle_user_object=snapbundle_user_object,
                                            snapbundle_username=snapbundle_username,
                                            snapbundle_password=snapbundle_password,
                                            username=instagram_handle)

print "Authenticating to Instagram API"
instagram_user.authenticate()

print "Setting SocialStash user data from API"
instagram_user.set_user_data_from_instagram()

print "SocialStash Instagram User Info:"
print str(instagram_user.AsDict())

print "Checking for SocialStash Instagram User in SnapBundle"
response = instagram_user.check_for_user_in_snapbundle()
if not response:
    print "User not found!  Creating New User"
    print "User URN: " + str(instagram_user.create_update_user_in_snapbundle())
else:
    print "User exists!"
    print "SnapBundle Data: " + str(response)
    #print "Updating anyway"
    #print "Updated URN: " + str(instagram_user.create_update_user_in_snapbundle())

print "Get data stored in SnapBundle"
print str(instagram_user.get_user_data_in_snapbundle())


exit()