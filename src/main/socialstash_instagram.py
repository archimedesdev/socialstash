__author__ = 'prad'
__version__ = '1.0'

import instagram
import logging
import ConfigParser
import requests
import ast

logging.debug('Starting: ' + __name__)

# == Import all the account information that is stored in a local file (not sync'd wih public github)
config_file = 'accounts.txt'
config = ConfigParser.RawConfigParser()
config.read(config_file)

# == Snapbundle Variables ==
snapbundle_base_url_objects = 'https://snapbundle.tagdynamics.net/v1/app/objects'
# == End Snapbundle Variables ==


class User(object):
    '''A class representing the Instagram User structure used by SocialStash.

    The User structure exposes the following properties:
      user.id
      user.username
      user.full_name
      user.profile_picture_url
      user.bio
      user.website_url
      user.counts_media
      user.counts_followed_by
      user.counts_follows
      user.api
      user.access_token
    '''

    def __init__(self, **kwargs):
        logging.info("Creating SocialStash Instagram User")
        param_defaults = {
            'id':                           None,
            'usernmae':                     None,
            'full_name':                    None,
            'profile_picture':              None,
            'bio':                          None,
            'website':                      None,
            'counts':                       None,
            'access_token':                 None,
            'api':                          None,
            'snapbundle_user_object':       None,
            'snapbundle_username':          None,
            'snapbundle_password':          None}

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    def authenticate(self):
        logging.info("Authenticating and setting up Instagram API connection")
        self._api = instagram.client.InstagramAPI(access_token=self._access_token)

    def set_user_data_from_instagram(self):
        logging.info("Setting SocialStash Instagram User info from Instagram")
        self._id = self._api.user().id
        self._username = self._api.user().username
        self._full_name = self._api.user().full_name
        self._profile_picture = self._api.user().profile_picture
        self._bio = self._api.user().bio
        self._website = self._api.user().website
        self._counts = self._api.user().counts

    def check_for_user_in_snapbundle(self):
        urn_to_check_for = "urn:" + self._snapbundle_user_object + ":instagram:" + self._username
        logging.info("Checking SnapBundle for URN: " + str(urn_to_check_for))
        response = requests.get(snapbundle_base_url_objects + '/' + urn_to_check_for, auth=(self._snapbundle_username, self._snapbundle_password))
        try:
            if response.json()['objectUrn'] != urn_to_check_for:
                logging.info("ObjectURN not found!")
            else:
                logging.info("Object Exists!!")
                logging.info(response.json())
        except KeyError:
            logging.info("Instagram user Object does not yet exist in SnapBundle, creating...")
            instagram_user_sb_urn = snapbundle_instagram_fxns.add_new_instagram_user_object(instagram_handle, self._snapbundle_user_object, instagram_handle + "'s Instagram Account")

    def get_api(self):
        return self._api

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

    def __str__(self):
        '''A string representation of this twitter.User instance.

        The return value is the same as the JSON string representation.

        Returns:
          A string representation of this twitter.User instance.
        '''
        return self.AsJsonString()

    def AsJsonString(self):
        '''A JSON string representation of this twitter.User instance.

        Returns:
          A JSON string representation of this twitter.User instance
        '''
        return simplejson.dumps(self.AsDict(), sort_keys=True)

    def AsDict(self):
        '''A dict representation of this twitter.User instance.

        The return value uses the same key names as the JSON representation.

        Return:
          A dict representing this twitter.User instance
        '''
        data = {}
        if self.id:
          data['id'] = self.id
        if self.username:
          data['username'] = self.userame
        if self.full_name:
          data['full_name'] = self.full_name
        if self.profile_picture:
          data['profile_picture'] = self.profile_picture
        if self.bio:
          data['bio'] = self.bio
        if self.website:
          data['website'] = self.website
        if self.counts is not None:
          data['counts'] = self.counts

        return data
