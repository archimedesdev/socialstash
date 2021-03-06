__author__ = 'prad'

import ConfigParser
import ast
import tweepy
import snapbundle_twitter_fxns
import requests
import logging

logging.debug('Starting: ' + __name__)


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
def twitter_pull_user_data(passed_in_user):
    user = dict()
    user['contributors_enabled'] = passed_in_user.contributors_enabled
    user['created_at'] = passed_in_user.created_at
    user['default_profile'] = passed_in_user.default_profile
    user['default_profile_image'] = passed_in_user.default_profile_image
    user['description'] = passed_in_user.description
    user['entities'] = passed_in_user.entities
    user['favourites_count'] = passed_in_user.favourites_count
    user['follow_request_sent'] = passed_in_user.follow_request_sent
    user['followers_count'] = passed_in_user.followers_count
    user['friends_count'] = passed_in_user.friends_count
    user['geo_enabled'] = passed_in_user.geo_enabled
    user['id'] = passed_in_user.id
    user['id_str'] = passed_in_user.id_str
    user['is_translator'] = passed_in_user.is_translator
    user['lang'] = passed_in_user.lang
    user['listed_count'] = passed_in_user.listed_count
    user['location'] = passed_in_user.location
    user['name'] = passed_in_user.name
    user['profile_background_color'] = passed_in_user.profile_background_color
    user['profile_background_image_url'] = passed_in_user.profile_background_image_url
    user['profile_background_image_url_https'] = passed_in_user.profile_background_image_url_https
    user['profile_background_tile'] = passed_in_user.profile_background_tile

    try:
        user['profile_banner_url'] = passed_in_user.profile_banner_url
    except AttributeError:
        user['profile_banner_url'] = ''

    user['profile_image_url'] = passed_in_user.profile_image_url
    user['profile_image_url_https'] = passed_in_user.profile_image_url_https
    user['profile_link_color'] = passed_in_user.profile_link_color
    user['profile_sidebar_border_color'] = passed_in_user.profile_sidebar_border_color
    user['profile_sidebar_fill_color'] = passed_in_user.profile_sidebar_fill_color
    user['profile_text_color'] = passed_in_user.profile_text_color
    user['profile_use_background_image'] = passed_in_user.profile_use_background_image
    user['protected'] = passed_in_user.protected
    user['screen_name'] = passed_in_user.screen_name

    try:
        user['show_all_inline_media'] = api.show_all_inline_media
    except AttributeError:
        user['show_all_inline_media'] = ''

    try:
        user['status'] = passed_in_user.status
    except AttributeError:
        user['status'] = ''

    user['statuses_count'] = passed_in_user.statuses_count
    user['time_zone'] = passed_in_user.time_zone
    user['url'] = passed_in_user.url
    user['utc_offset'] = passed_in_user.utc_offset
    user['verified'] = passed_in_user.verified

    try:
        user['withheld_in_countries'] = api.withheld_in_countries
    except AttributeError:
        user['withheld_in_countries'] = ''

    try:
        user['withheld_scope'] = api.withheld_scope
    except AttributeError:
        user['withheld_scope'] = ''

    return user


#---------------------------------------------------------------------------------------------------------------------
def update_snapbundle_tweets(parent_object_urn, tweet_list):
    for current_tweet in tweet_list:
        print str(current_tweet.retweet_count) + ":" + current_tweet.source + ":" + current_tweet.text
        #snapbundle_twitter_fxns.add_new_twitter_tweet(parent_object_urn, current_tweet)
        #return
##-------------------------------------------------------------------------------------------------------------------##

#twitter_handle = 'AnEloquentDane'
twitter_handle = 'praddc'

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
    #snapbundle_twitter_fxns.add_new_twitter_user_object(twitter_handle, snapbundle_user_object, twitter_handle + "'s Twitter Account")


print "Setting up API"
api = twitter_authenticate(pr_consumer_key, pr_consumer_secret, twitter_access_tokens[twitter_handle]['token'], twitter_access_tokens[twitter_handle]['token_secret'])

print "Pulling Twitter user data"
userData = twitter_pull_user_data(api.me())
print userData

#print "Updating Twitter user data in Snapbundle"
#snapbundle_twitter_fxns.update_twiter_user_object(urn_to_check_for, userData)

print "checking other user data"
userData = twitter_pull_user_data(api.get_user("ggreenwald"))
print userData


print "Getting Twitter user timeline 20"
userTimeline = api.user_timeline("ggreenwald")
update_snapbundle_tweets(urn_to_check_for, userTimeline)


exit()
#print str(userData)
