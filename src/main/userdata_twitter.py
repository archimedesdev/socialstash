__author__ = 'prad'

import ConfigParser
import ast
import tweepy
import json
import snapbundle_twitter_fxns
import requests


# == Import all the account information that is stored in a local file (not sync'd wih public github)
config_file = 'accounts.txt'
config = ConfigParser.RawConfigParser()
config.read(config_file)

# == Twitter OAuth Authentication ==
# This mode of authentication is the new preferred way
# of authenticating with Twitter.
pr_consumer_key = config.get('TwitterApplicationAccounts', 'consumerKey')
pr_consumer_secret = config.get('TwitterApplicationAccounts', 'consumerSecret')
twitter_access_tokens = ast.literal_eval(config.get('TwitterUserOAuthTokens', 'twitter_access_tokens'))
# == End Twitter OAuth Authentication ==

# == Snapbundle Variables ==
snapbundle_username = config.get('SnapbundleCredentials', 'snapbundle_username')
snapbundle_password = config.get('SnapbundleCredentials', 'snapbundle_password')
snapbundle_base_url_objects = 'https://snapbundle.tagdynamics.net/v1/app/objects'
snapbundle_user_object = 'paulr'
# == End Snapbundle Variables ==



def twitter_authenticate(consumer_key, consumer_secret, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    my_api = tweepy.API(auth)
    return my_api


#---------------------------------------------------------------------------------------------------------------------
def twitter_pull_user_data(passed_in_api):
    user = dict()
    user['contributors_enabled'] = passed_in_api.me().contributors_enabled
    user['created_at'] = passed_in_api.me().created_at
    user['default_profile'] = passed_in_api.me().default_profile
    user['default_profile_image'] = passed_in_api.me().default_profile_image
    user['description'] = passed_in_api.me().description
    user['entities'] = passed_in_api.me().entities
    user['favourites_count'] = passed_in_api.me().favourites_count
    user['follow_request_sent'] = passed_in_api.me().follow_request_sent
    user['followers_count'] = passed_in_api.me().followers_count
    user['friends_count'] = passed_in_api.me().friends_count
    user['geo_enabled'] = passed_in_api.me().geo_enabled
    user['id'] = passed_in_api.me().id
    user['id_str'] = passed_in_api.me().id_str
    user['is_translator'] = passed_in_api.me().is_translator
    user['lang'] = passed_in_api.me().lang
    user['listed_count'] = passed_in_api.me().listed_count
    user['location'] = passed_in_api.me().location
    user['name'] = passed_in_api.me().name
    user['profile_background_color'] = passed_in_api.me().profile_background_color
    user['profile_background_image_url'] = passed_in_api.me().profile_background_image_url
    user['profile_background_image_url_https'] = passed_in_api.me().profile_background_image_url_https
    user['profile_background_tile'] = passed_in_api.me().profile_background_tile

    try:
        user['profile_banner_url'] = passed_in_api.me().profile_banner_url
    except AttributeError:
        user['profile_banner_url'] = ''

    user['profile_image_url'] = passed_in_api.me().profile_image_url
    user['profile_image_url_https'] = passed_in_api.me().profile_image_url_https
    user['profile_link_color'] = passed_in_api.me().profile_link_color
    user['profile_sidebar_border_color'] = passed_in_api.me().profile_sidebar_border_color
    user['profile_sidebar_fill_color'] = passed_in_api.me().profile_sidebar_fill_color
    user['profile_text_color'] = passed_in_api.me().profile_text_color
    user['profile_use_background_image'] = passed_in_api.me().profile_use_background_image
    user['protected'] = passed_in_api.me().protected
    user['screen_name'] = passed_in_api.me().screen_name

    try:
        user['show_all_inline_media'] = api.me().show_all_inline_media
    except AttributeError:
        user['show_all_inline_media'] = ''

    try:
        user['status'] = passed_in_api.me().status
    except AttributeError:
        user['status'] = ''

    user['statuses_count'] = passed_in_api.me().statuses_count
    user['time_zone'] = passed_in_api.me().time_zone
    user['url'] = passed_in_api.me().url
    user['utc_offset'] = passed_in_api.me().utc_offset
    user['verified'] = passed_in_api.me().verified

    try:
        user['withheld_in_countries'] = api.me().withheld_in_countries
    except AttributeError:
        user['withheld_in_countries'] = ''

    try:
        user['withheld_scope'] = api.me().withheld_scope
    except AttributeError:
        user['withheld_scope'] = ''

    return user


#---------------------------------------------------------------------------------------------------------------------
def twitter_user_update_snapbundle(reference_urn, user):
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Boolean", "contributors_enabled", user['contributors_enabled'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "created_at", user['created_at'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Boolean", "contributors_enabled", user['contributors_enabled'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Boolean", "default_profile", user['default_profile'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Boolean", "default_profile_image", user['default_profile_image'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "description", user['description'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Integer", "favourites_count", user['favourites_count'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Boolean", "follow_request_sent", user['follow_request_sent'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Integer", "followers_count", user['followers_count'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Integer", "friends_count", user['friends_count'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Boolean", "geo_enabled", user['geo_enabled'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Long", "id", user['id'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "id_str", user['id_str'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Boolean", "is_translator", user['is_translator'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "lang", user['lang'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Integer", "listed_count", user['listed_count'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "location", user['location'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "name", user['name'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "profile_background_color", user['profile_background_color'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "profile_background_image_url", user['profile_background_image_url'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "profile_background_image_url_https", user['profile_background_image_url_https'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Boolean", "profile_background_tile", user['profile_background_tile'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "profile_banner_url", user['profile_banner_url'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "profile_image_url", user['profile_image_url'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "profile_image_url_https", user['profile_image_url_https'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "profile_link_color", user['profile_link_color'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "profile_sidebar_border_color", user['profile_sidebar_border_color'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "profile_sidebar_fill_color", user['profile_sidebar_fill_color'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "profile_text_color", user['profile_text_color'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Boolean", "profile_use_background_image", user['profile_use_background_image'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Boolean", "protected", user['protected'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "screen_name", user['screen_name'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Boolean", "show_all_inline_media", user['show_all_inline_media'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Integer", "statuses_count", user['statuses_count'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "time_zone", user['time_zone'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "url", user['url'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Integer", "utc_offset", user['utc_offset'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "Boolean", "verified", user['verified'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "withheld_in_countries", user['withheld_in_countries'])
    snapbundle_twitter_fxns.add_update_metadata("Object", reference_urn, "String", "withheld_scope", user['withheld_scope'])

    ## STILL NEED TO DO
    #user['entities'] = passed_in_api.me().entities
    #user['status'] = passed_in_api.me().status


#---------------------------------------------------------------------------------------------------------------------
def update_snapbundle_tweets(parent_object_urn, tweet_list):
    for current_tweet in tweet_list:
        #print str(current_tweet.retweeted) + " " + current_tweet.source
        snapbundle_twitter_fxns.add_new_twiter_tweet(parent_object_urn, current_tweet)
        return
##-------------------------------------------------------------------------------------------------------------------##

twitter_handle = 'AnEloquentDane'
#twitter_handle = 'praddc'

urn_to_check_for = snapbundle_user_object + ":twitter:" + twitter_handle
print "Looking for URN: " + str(urn_to_check_for)
response = requests.get(snapbundle_base_url_objects + '/' + urn_to_check_for, auth=(snapbundle_username, snapbundle_password))
try:
    if response.json()['objectUrn'] != urn_to_check_for:
        print "ObjectURN not found!"
    else:
        print "Object Exists!!"
        print response.json()
except KeyError:
    print "Twitter user Object does not yet exist, creating..."
    snapbundle_twitter_fxns.add_new_twiter_user_object(twitter_handle, snapbundle_user_object, twitter_handle + "'s Twitter Account")


print "Setting up API"
api = twitter_authenticate(pr_consumer_key, pr_consumer_secret, twitter_access_tokens[twitter_handle]['token'], twitter_access_tokens[twitter_handle]['token_secret'])

#print "Pulling Twitter user data"
#userData = twitter_pull_user_data(api)
#print userData

#print "Updating Twitter user data in Snapbundle"
#twitter_user_update_snapbundle(urn_to_check_for, userData)

print "Getting Twitter user timeline 20"
userTimeline = api.user_timeline()
update_snapbundle_tweets(urn_to_check_for, userTimeline)
exit()
#print str(userData)

#user_json_encoded = json.dumps(userData)
#user_json_decoded = json.loads(user_json_encoded)
