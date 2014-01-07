__author__ = 'prad'
__version__ = '1.0'

import tweepy
import logging
import ConfigParser
import requests
import json
import urlparse
import snapbundle_instagram_fxns
import traceback
import networkx as nx
import matplotlib.pyplot as plt
import pylab
import snapbundle_twitter_fxns

logging.debug('Starting: ' + __name__)

# == Import all the account information that is stored in a local file (not sync'd wih public github)
config_file = 'accounts.txt'
config = ConfigParser.RawConfigParser()
config.read(config_file)

# == Twitter API URLs ==

# == Twitter Variables ==
# number of records to get per request
twitter_record_count = 100
# number of feed records to get per request
twitter_feed_record_count = 100
# If the follows/following count is higher than this, don't bother going down the chain
twitter_max_follow_count = 50
# number of layers out to go when recursively searching
max_search_depth = 2
# == End Instagram Variables ==

# == Global Variables ==
# Need this one to save us calls to the instagram API (limited to 5000 per hour)
global_twitter_user_dictionary = {}
global_snapbundle_user_dictionary = {}
global_count_saved_api_calls = 0
global_relationship_edge_list = []
global_relationship_node_list = []
global_counts_dictionary = {}
global_counts_dictionary['api_calls'] = 0
global_counts_dictionary['snapbundle_calls'] = 0
global_counts_dictionary['cache_calls'] = 0
global_counts_dictionary['snapbundle_deletes'] = 0

global_following_string = 'FOLLOWING'
global_followed_by_string = 'FOLLOWED_BY'

class User(object):
    '''A class representing the Instagram User structure used by SocialStash.

    '''

    def __init__(self, access_token, **kwargs):
        logging.info("Creating SocialStash Twitter User")
        self.access_token = access_token
        param_defaults = {
            'id': None,
            'id_str': None,
            'screen_name': None,
            'location': None,
            'name': None,
            'profile_background_color': None,
            'profile_background_image_url': None,
            'profile_background_image_url_https': None,
            'profile_background_tile': None,
            'profile_banner_url': None,
            'profile_image_url': None,
            'profile_image_url_https': None,
            'profile_link_color': None,
            'profile_sidebar_border_color': None,
            'profile_sidebar_fill_color': None,
            'profile_text_color': None,
            'profile_use_background_image': None,
            'protected': None,
            'show_all_inline_media': None,
            'status': None,
            'statuses_count': None,
            'time_zone': None,
            'url': None,
            'utc_offset': None,
            'listed_count': None,
            'lang': None,
            'verified': None,
            'withheld_in_countries': None,
            'withheld_scope': None,
            'is_translator': None,
            'geo_enabled': None,
            'friends_count': None,
            'followers_count': None,
            'follow_request_sent': None,
            'favourites_count': None,
            'entities': None,
            'description': None,
            'default_profile_image': None,
            'default_profile': None,
            'created_at': None,
            'contributors_enabled': None,
            'following_dict': None,
            'followedby_dict': None,
            'api': None,
            'consumer_key': None,
            'consumer_secret': None,
            'access_token': None,
            'access_token_secret': None,
            'snapbundle_user_object': None,
            'snapbundle_username': None,
            'snapbundle_password': None,
            'twitter_user_sb_object_urn': None,
            'twitter_user_sb_urn': None,
            'current_search_depth': max_search_depth}

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

        if self._username is not None:
            self._instagram_user_sb_object_urn = snapbundle_instagram_fxns.snapbundle_base_urn_instagram_user + self._username

## ----------------------------------- FXN ------------------------------------------------------------------------
    def authenticate(self, consumer_key, consumer_secret, access_token, access_token_secret):
        logging.info("Authenticating and setting up Twitter API connection")
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

## ----------------------------------- FXN ------------------------------------------------------------------------
    def get_id_of_authenticated_user(self):
        return self.api.me().id

## ----------------------------------- FXN ------------------------------------------------------------------------
    def set_user_data_from_twitter(self):
        logging.info("Setting SocialStash Twitter User info from Twitter for user " + self.api.me().username)
        self.contributors_enabled = self.api.me().contributors_enabled
        self.created_at = self.api.me().created_at
        self.default_profile = self.api.me().default_profile
        self.default_profile_image = self.api.me().default_profile_image
        self.description = self.api.me().description
        self.entities = self.api.me().entities
        self.favourites_count = self.api.me().favourites_count
        self.follow_request_sent = self.api.me().follow_request_sent
        self.followers_count = self.api.me().followers_count
        self.friends_count = self.api.me().friends_count
        self.geo_enabled = self.api.me().geo_enabled
        self.id = self.api.me().id
        self.id_str = self.api.me().id_str
        self.is_translator = self.api.me().is_translator
        self.lang = self.api.me().lang
        self.listed_count = self.api.me().listed_count
        self.location = self.api.me().location
        self.name = self.api.me().name
        self.profile_background_color = self.api.me().profile_background_color
        self.profile_background_image_url = self.api.me().profile_background_image_url
        self.profile_background_image_url_https = self.api.me().profile_background_image_url_https
        self.profile_background_tile = self.api.me().profile_background_tile

        try:
            self.profile_banner_url = self.api.me().profile_banner_url
        except AttributeError:
            self.profile_banner_url = ''

        self.profile_image_url = self.api.me().profile_image_url
        self.profile_image_url_https = self.api.me().profile_image_url_https
        self.profile_link_color = self.api.me().profile_link_color
        self.profile_sidebar_border_color = self.api.me().profile_sidebar_border_color
        self.profile_sidebar_fill_color = self.api.me().profile_sidebar_fill_color
        self.profile_text_color = self.api.me().profile_text_color
        self.profile_use_background_image = self.api.me().profile_use_background_image
        self.protected = self.api.me().protected
        self.screen_name = self.api.me().screen_name

        try:
            self.show_all_inline_media = self.api.show_all_inline_media
        except AttributeError:
            self.show_all_inline_media = ''

        try:
            self.status = self.api.me().status
        except AttributeError:
            self.status = ''

        self.statuses_count = self.api.me().statuses_count
        self.time_zone = self.api.me().time_zone
        self.url = self.api.me().url
        self.utc_offset = self.api.me().utc_offset
        self.verified = self.api.me().verified

        try:
            self.withheld_in_countries = self.api.withheld_in_countries
        except AttributeError:
            self.withheld_in_countries = ''

        try:
            self.withheld_scope = self.api.withheld_scope
        except AttributeError:
            self.withheld_scope = ''

        self.twitter_user_sb_object_urn = snapbundle_twitter_fxns.snapbundle_base_urn_twitter_user + self.username
        global global_twitter_user_dictionary
        global global_counts_dictionary
        global_counts_dictionary['api_calls'] += 7
        if self.username not in global_twitter_user_dictionary:
            global_twitter_user_dictionary[self.username] = self

## ----------------------------------- FXN ------------------------------------------------------------------------
    def check_for_user_in_snapbundle(self):
        global global_counts_dictionary
        global global_snapbundle_user_dictionary
        global_counts_dictionary['snapbundle_calls'] += 1
        logging.info("Checking SnapBundle (cache, then database) for URN: " + self._instagram_user_sb_object_urn)
        # No need to check SB every time with an HTTP request, so let's check our cache first
        if self.twitter_user_sb_object_urn in global_snapbundle_user_dictionary:
            return True
        else:
            # Not in cache, so let's get the value
            return_value = snapbundle_instagram_fxns.check_for_object(self.twitter_user_sb_object_urn)

        # For the next time we get asked, put it in the cache
        if return_value:
            global_snapbundle_user_dictionary[self.twitter_user_sb_object_urn] = True
        return return_value


## ----------------------------------- FXN ------------------------------------------------------------------------
    def create_update_user_in_snapbundle(self, new_user=False):
        self.twitter_user_sb_urn = snapbundle_twitter_fxns.add_update_new_twitter_user_object(self.username, self.twitter_user_sb_object_urn)
        snapbundle_twitter_fxns.update_twitter_user_object(self.twitter_user_sb_object_urn, self.AsDict(), new_user)
        return self.twitter_user_sb_urn

## ----------------------------------- FXN ------------------------------------------------------------------------
    def create_update_user_in_snapbundle_object_only(self):
        self.twitter_user_sb_urn = snapbundle_instagram_fxns.add_update_new_instagram_user_object(self._username, self._instagram_user_sb_object_urn)
        return self.twitter_user_sb_urn





## ----------------------------------- FXN ------------------------------------------------------------------------
    def get_instagrame_user_sb_urn(self):
        return self._instagram_user_sb_urn

    def get_instagrame_user_sb_object_urn(self):
        return self._instagram_user_sb_object_urn

    def get_api(self):
        return self.api

    def get_snapbundle_user_object(self):
        return self._snapbundle_user_object

    def set_snapbundle_user_object(self, id):
        self._snapbundle_user_object = id

    snapbundle_user_object = property(get_snapbundle_user_object, set_snapbundle_user_object, doc='The unique id of this user.')

    def get_snapbundle_username(self):
        return self._snapbundle_username

    def set_snapbundle_username(self, id):
        self._snapbundle_username = id

    snapbundle_username = property(get_snapbundle_username, set_snapbundle_username, doc='The unique id of this user.')

    def get_snapbundle_password(self):
        return self._snapbundle_password

    def set_snapbundle_password(self, id):
        self._snapbundle_password = id

    snapbundle_password = property(get_snapbundle_password, set_snapbundle_password, doc='The unique id of this user.')

    def get_id(self):
        return self._id

    def set_id(self, id):
        self._id = id

    id = property(get_id, set_id, doc='The unique id of this user.')

    def get_username(self):
        return self._username

    def set_username(self, name):
        self._username = name

    username = property(get_username, set_username, doc='The user name of this user.')

    def get_full_name(self):
        return self._full_name

    def set_full_name(self, name):
        self._full_name = name

    full_name = property(get_full_name, set_full_name, doc='The full name of this user.')

    def get_profile_picture(self):
        return self._profile_picture

    def set_profile_picture(self, name):
        self._profile_picture = name

    profile_picture = property(get_profile_picture, set_profile_picture, doc='The profile picture of this user.')

    def get_bio(self):
        return self._bio

    def set_bio(self, bio):
        self._bio = bio

    bio = property(get_bio, set_bio, doc='The bio of this user.')

    def get_website(self):
        return self._website

    def set_website(self, website):
        self._website = website

    website = property(get_website, set_website, doc='The website of this user.')

    def get_counts(self):
        return self._counts

    def set_counts(self, counts):
        self._counts = counts

    counts = property(get_counts, set_counts, doc='The counts of this user.')

    def get_following_dict(self):
        return self.following_dict

    def set_following_dict(self, dict):
        self.following_dict = dict

    def get_followedby_dict(self):
        return self.followedby_dict

    def set_followedby_dict(self, dict):
        self.followedby_dict = dict

    def get_current_search_depth(self):
        return self.current_search_depth

    def set_current_search_depth(self, depth):
        self.current_search_depth = depth

## ----------------------------------- FXN ------------------------------------------------------------------------
    def __str__(self):
        '''A string representation of this twitter.User instance.

        The return value is the same as the JSON string representation.

        Returns:
          A string representation of this twitter.User instance.
        '''
        return self.AsJsonString()

## ----------------------------------- FXN ------------------------------------------------------------------------
    def AsJsonString(self):
        '''A JSON string representation of this twitter.User instance.

        Returns:
          A JSON string representation of this twitter.User instance
        '''
        return json.dumps(self.AsDict(), sort_keys=True)

## ----------------------------------- FXN ------------------------------------------------------------------------
    def AsDict(self):
        '''A dict representation of this twitter.User instance.

        The return value uses the same key names as the JSON representation.

        Return:
          A dict representing this twitter.User instance
        '''
        data = {}

        data['contributors_enabled'] = self.contributors_enabled
        data['created_at'] = self.created_at
        data['default_profile'] = self.default_profile
        data['default_profile_image'] = self.default_profile_image
        data['description'] = self.description
        data['entities'] = self.entities
        data['favourites_count'] = self.favourites_count
        data['follow_request_sent'] = self.follow_request_sent
        data['followers_count'] = self.followers_count
        data['friends_count'] = self.friends_count
        data['geo_enabled'] = self.geo_enabled
        data['id'] = self.id
        data['id_str'] = self.id_str
        data['is_translator'] = self.is_translator
        data['lang'] = self.lang
        data['listed_count'] = self.listed_count
        data['location'] = self.location
        data['name'] = self.name
        data['profile_background_color'] = self.profile_background_color
        data['profile_background_image_url'] = self.profile_background_image_url
        data['profile_background_image_url_https'] = self.profile_background_image_url_https
        data['profile_background_tile'] = self.profile_background_tile
        data['profile_banner_url'] = self.profile_banner_url
        data['profile_image_url'] = self.profile_image_url
        data['profile_image_url_https'] = self.profile_image_url_https
        data['profile_link_color'] = self.profile_link_color
        data['profile_sidebar_border_color'] = self.profile_sidebar_border_color
        data['profile_sidebar_fill_color'] = self.profile_sidebar_fill_color
        data['profile_text_color'] = self.profile_text_color
        data['profile_use_background_image'] = self.profile_use_background_image
        data['protected'] = self.protected
        data['screen_name'] = self.screen_name
        data['show_all_inline_media'] = self.show_all_inline_media
        data['status'] = self.status
        data['statuses_count'] = self.statuses_count
        data['time_zone'] = self.time_zone
        data['url'] = self.url
        data['utc_offset'] = self.utc_offset
        data['verified'] = self.verified
        data['withheld_in_countries'] = self.withheld_in_countries
        data['withheld_scope'] = self.withheld_scope
        data['twitter_user_sb_object_urn'] = self.twitter_user_sb_object_urn
        return data

## ----------------------------------- FXN ------------------------------------------------------------------------
    @staticmethod
    def get_global_count_saved_api_calls():
        global global_count_saved_api_calls
        return global_count_saved_api_calls

## ----------------------------------- FXN ------------------------------------------------------------------------
    @staticmethod
    def get_global_counts_dict():
        global global_counts_dictionary
        return global_counts_dictionary

## ----------------------------------- FXN ------------------------------------------------------------------------
    @staticmethod
    def get_global_relationship_node_list():
        global global_relationship_edge_list
        return global_relationship_edge_list

## ----------------------------------- FXN ------------------------------------------------------------------------
    @staticmethod
    def update_cached_users_media_feed(max_media=50, update_if_found=False):
        total_num_updates = 0
        logging.info("Looking to update media posts of all users found in local cache into SnapBundle")
        for username in global_instagram_user_dictionary.keys():
            logging.info("Looking to update user " + str(username) + "'s media feed in SnapBundle")
            user = global_instagram_user_dictionary[username]
            if user.api is None:
                user.authenticate()

            if user.counts['media'] <= max_media:
                #logging.info("Using API from user X to update posts from user Y (" + str(user.username) + ":" + str(username) + ")")
                #num_updates = user.check_recent_media_exists_in_snapbundle(update_if_found=update_if_found)
                #logging.info("Updated " + str(num_updates) + "posts for user " + str(user.username))
                total_num_updates += 0 #num_updates
            else:
                logging.info("Not using API from user X to update posts from user Y (" + str(user.username) + ":" +
                             str(username) + ").  Media count was too high (" + str(user.counts['media']) + ">" +
                             str(max_media) + ")")

        return total_num_updates

## ----------------------------------- FXN ------------------------------------------------------------------------
    def test_one_thing(self):
        user_dictionary = {}
        keep_going = True
        next_cursor = None
        while keep_going:
            # Get this set of users
            response, next_url = self.api.user_follows(user_id=34379259, count=instagram_record_count, cursor=next_cursor)

            # Add them to a dictionarry
            for current in response:
                if current.username.encode() not in user_dictionary.keys():
                    user_dictionary[current.username.encode()] = current
            if next_url is None:
                keep_going = False
            else:
                # There are more we need to get, so here's the next cursor to start at
                next_cursor = str(urlparse.parse_qs(urlparse.urlparse(next_url).query)['cursor'][0])

        print "following " + str(len(user_dictionary)) + " people"
