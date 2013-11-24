__author__ = 'prad'

import ConfigParser
import ast
import requests
import instagram
import snapbundle_instagram_fxns

# == Import all the account information that is stored in a local file (not sync'd wih public github)
config_file = 'accounts.txt'
config = ConfigParser.RawConfigParser()
config.read(config_file)

# == Twitter OAuth Authentication ==
# This mode of authentication is the new preferred way
# of authenticating with Twitter.
pr_client_id = config.get('InstagramApplicationAccounts', 'clientID')
pr_client_secret = config.get('InstagramApplicationAccounts', 'clientSecret')
instagrame_access_tokens = ast.literal_eval(config.get('InstagramUserOAuthTokens', 'instagram_access_tokens'))
# == End Twitter OAuth Authentication ==

# == Snapbundle Variables ==
snapbundle_username = config.get('SnapbundleCredentials', 'snapbundle_username')
snapbundle_password = config.get('SnapbundleCredentials', 'snapbundle_password')
snapbundle_base_url_objects = 'https://snapbundle.tagdynamics.net/v1/app/objects'
snapbundle_user_object = 'paulr'
# == End Snapbundle Variables ==


def instagram_authenticate(access_token):
    my_api = instagram.client.InstagramAPI(access_token=access_token)
    return my_api


#---------------------------------------------------------------------------------------------------------------------
def instagram_pull_user_data(passed_in_api):
    user = dict()
    user['id'] = passed_in_api.user().id
    user['username'] = passed_in_api.user().username
    user['full_name'] = passed_in_api.user().full_name
    user['profile_picture'] = passed_in_api.user().profile_picture
    user['bio'] = passed_in_api.user().bio
    user['website'] = passed_in_api.user().website
    user['counts'] = passed_in_api.user().counts
    return user


#---------------------------------------------------------------------------------------------------------------------
def update_snapbundle_tweets(parent_object_urn, tweet_list):
    for current_tweet in tweet_list:
        #print str(current_tweet.retweeted) + " " + current_tweet.source
        #snapbundle_twitter_fxns.add_new_twitter_tweet(parent_object_urn, current_tweet)
        return
##-------------------------------------------------------------------------------------------------------------------##

#instagram_handle = 'AnEloquentDane'
instagram_handle = 'praddc'

urn_to_check_for = snapbundle_user_object + ":instagram:" + instagram_handle
print "Looking for URN: " + str(urn_to_check_for)
response = requests.get(snapbundle_base_url_objects + '/' + urn_to_check_for, auth=(snapbundle_username, snapbundle_password))
try:
    if response.json()['objectUrn'] != urn_to_check_for:
        print "ObjectURN not found!"
    else:
        print "Object Exists!!"
        print response.json()
except KeyError:
    print "Instagram user Object does not yet exist, creating..."
    snapbundle_instagram_fxns.add_new_instagram_user_object(instagram_handle, snapbundle_user_object, instagram_handle + "'s Instagram Account")


print "Setting up API"
api = instagram_authenticate(instagrame_access_tokens[instagram_handle]['access_token'])

print "Pulling Instagram user data"
userData = instagram_pull_user_data(api)
print userData

print "Updating Twitter user data in Snapbundle"
snapbundle_instagram_fxns.update_instagram_user_object(urn_to_check_for, userData)

#print "Getting Twitter user timeline 20"
#userTimeline = api.user_timeline()
#update_snapbundle_tweets(urn_to_check_for, userTimeline)
exit()
#print str(userData)
