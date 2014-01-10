__author__ = 'prad'

import ConfigParser
import logging
import ast
import socialstash_instagram


logging.debug('Starting: ' + __name__)

# == Import all the account information that is stored in a local file (not sync'd wih public github)
config_file = 'accounts.txt'
config = ConfigParser.RawConfigParser()
config.read(config_file)

# == Instagram OAuth Authentication ==
# This mode of authentication is the new preferred way
# of authenticating with Twitter.
#pr_client_id = config.get('InstagramApplicationAccounts', 'clientID')
#pr_client_secret = config.get('InstagramApplicationAccounts', 'clientSecret')
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

print "Getting my authenticated ID"
my_id = instagram_user.get_id_of_authenticated_user()
print "My ID: " + str(my_id)

print "Setting SocialStash user data from API"
instagram_user.set_user_data_from_instagram(my_id)

print "SocialStash Instagram User Info:"
print str(instagram_user.AsDict())

print "Checking for SocialStash Instagram User in SnapBundle"
response = instagram_user.check_for_user_in_snapbundle()

if not response:
    print "User not found!  Creating New User"
    print "User URN: " + str(instagram_user.create_update_user_in_snapbundle(new_user=True))
else:
    print "User exists!"
    print "SnapBundle Data: " + str(response)
    #print "Updating anyway"
    #print "Updated URN: " + str(instagram_user.create_update_user_in_snapbundle())

#print "Get data stored in SnapBundle"
#print str(instagram_user.get_user_data_in_snapbundle())

#################################################################################################################
#instagram_user.print_relationship_node_list(manual_pull_from_snapbundle=True, relationship='FOLLOWING', depth=1)
#instagram_user.print_relationship_node_list(manual_pull_from_snapbundle=True, relationship='FOLLOWED_BY', depth=1)
filename = 'test.gml'
#instagram_user.output_relationship_node_gml(filename=filename, depth=2)
#instagram_user.graph_relationship_gml(filename=filename)

#instagram_user.check_recent_media_exists_in_snapbundle(update_if_found=True)
update_user = 'chelsey_dc'
updates = instagram_user.update_user_feed_in_snapbundle(update_user, update_if_found=False, max_update_count=550)
print "Made " + str(updates) + " post updates for user " + str(update_user)
#instagram_user.update_cached_users_media_feed(max_media=60, update_if_found=False)
exit()


#################################################################################################################
print "Saved API Calls: " + str(instagram_user.get_global_count_saved_api_calls())
print "checking for users I'm following"
instagram_user.check_relationship_users_exist_in_snapbundle(relationship='FOLLOWING',
                                                            update_user_profile_if_found=False,
                                                            update_user_following_if_found=True,
                                                            update_user_followedby_if_found=True,
                                                            go_to_max_depth=True)

print "Saved API Calls: " + str(instagram_user.get_global_count_saved_api_calls())
print "Calls Dictionary: " + str(instagram_user.get_global_counts_dict())

#exit()


#################################################################################################################
# print 'checking for users following me'
instagram_user.check_relationship_users_exist_in_snapbundle(relationship='FOLLOWED_BY',
                                                            update_user_profile_if_found=False,
                                                            update_user_following_if_found=True,
                                                            update_user_followedby_if_found=True,
                                                            go_to_max_depth=True)

print "Saved API Calls: " + str(instagram_user.get_global_count_saved_api_calls())

#print "Getting recent media, count = 1"
#instagram_user.get_feed_from_instagram(1)

exit()