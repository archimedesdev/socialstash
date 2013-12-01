__author__ = 'prad'
__version__ = '1.0'

import instagram
import logging
import ConfigParser
import requests
import snapbundle_instagram_fxns

logging.debug('Starting: ' + __name__)

# == Import all the account information that is stored in a local file (not sync'd wih public github)
config_file = 'accounts.txt'
config = ConfigParser.RawConfigParser()
config.read(config_file)

# == Snapbundle Variables ==
snapbundle_base_url_objects = 'https://snapbundle.tagdynamics.net/v1/app/objects'
snapbundle_base_urn_instagram_user = "urn:instagram:users:"
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

    def __init__(self, access_token, **kwargs):
        logging.info("Creating SocialStash Instagram User")
        self.access_token = access_token
        param_defaults = {
            'id':                           None,
            'username':                     None,
            'full_name':                    '',
            'profile_picture':              None,
            'bio':                          None,
            'website':                      None,
            'counts':                       None,
            'api':                          None,
            'snapbundle_user_object':       None,
            'snapbundle_username':          None,
            'snapbundle_password':          None,
            'instagram_user_sb_object_urn': None,
            'instagram_user_sb_urn':        None}

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

    def authenticate(self):
        logging.info("Authenticating and setting up Instagram API connection")
        self._api = instagram.client.InstagramAPI(access_token=self.access_token)

    def get_id_of_authenticated_user(self):
        return self._api.user().id

    def set_user_data_from_instagram(self, user_id):
        logging.info("Setting SocialStash Instagram User info from Instagram")
        self._id = self._api.user(user_id).id
        self._username = self._api.user(user_id).username
        self._full_name = self._api.user(user_id).full_name
        self._profile_picture = self._api.user(user_id).profile_picture
        self._bio = self._api.user(user_id).bio
        self._website = self._api.user(user_id).website
        self._counts = self._api.user(user_id).counts
        #self._instagram_user_sb_object_urn = "urn:" + self._snapbundle_user_object + ":instagram:" + self._username
        self._instagram_user_sb_object_urn = snapbundle_base_urn_instagram_user + self._username

    def check_for_user_in_snapbundle(self):
        logging.info("Checking SnapBundle for URN: " + self._instagram_user_sb_object_urn)
        return snapbundle_instagram_fxns.check_for_object(self._instagram_user_sb_object_urn)

    def get_user_data_in_snapbundle(self):
        logging.info("Getting SnapBundle data for URN: " + self._instagram_user_sb_object_urn)
        object_data = snapbundle_instagram_fxns.get_object(self._instagram_user_sb_object_urn)
        object_metadata = snapbundle_instagram_fxns.get_object_metadata(self._instagram_user_sb_object_urn)
        return_data = {'object': object_data, 'metadata': object_metadata}
        return return_data

    def create_update_user_in_snapbundle(self, new_user=False):
        self._instagram_user_sb_urn = snapbundle_instagram_fxns.add_update_new_instagram_user_object(self._username, self._instagram_user_sb_object_urn)
        snapbundle_instagram_fxns.update_instagram_user_object(self._instagram_user_sb_object_urn, self.AsDict(), new_user)
        return self._instagram_user_sb_urn

    def check_all_users_followed_by_exist_in_snapbundle(self, update_if_found=False):
        response, next = self._api.user_followed_by()
        for current in response:
            try:
                temp_social_stash_i_user = User(access_token=self.access_token,
                                                snapbundle_user_object=self._snapbundle_user_object,
                                                snapbundle_username=self._snapbundle_username,
                                                snapbundle_password=self._snapbundle_password,
                                                username=current.username)
                temp_social_stash_i_user.authenticate()
                temp_social_stash_i_user.set_user_data_from_instagram(current.id)
                print "Checking for SocialStash Instagram User " + current.username+" in SnapBundle"
                response = temp_social_stash_i_user.check_for_user_in_snapbundle()
                if not response:
                    print "User not found!  Creating New User"
                    print "User URN: " + str(temp_social_stash_i_user.create_update_user_in_snapbundle(new_user=True))
                else:
                    print "User exists!"
                    if update_if_found:
                        print "Updating User " + current.username + " anyway"
                        print "Updated URN: " + str(temp_social_stash_i_user.create_update_user_in_snapbundle())
                del temp_social_stash_i_user
            except instagram.bind.InstagramAPIError:
                print "Unable to pull data for user " + current.username

    def check_all_users_following_exist_in_snapbundle(self, update_if_found=False):
        response, next = self._api.user_follows()
        for current in response:
            print "Following: " + str(current.username)
            try:
                temp_social_stash_i_user = User(access_token=self.access_token,
                                                snapbundle_user_object=self._snapbundle_user_object,
                                                snapbundle_username=self._snapbundle_username,
                                                snapbundle_password=self._snapbundle_password,
                                                username=current.username)
                temp_social_stash_i_user.authenticate()
                temp_social_stash_i_user.set_user_data_from_instagram(current.id)
                print "Checking for SocialStash Instagram User " + current.username+" in SnapBundle"
                response = temp_social_stash_i_user.check_for_user_in_snapbundle()
                if not response:
                    print "User not found!  Creating New User"
                    print "User URN: " + str(temp_social_stash_i_user.create_update_user_in_snapbundle(new_user=True))
                else:
                    print "User exists!"
                    if update_if_found:
                        print "Updating User " + current.username + " anyway"
                        print "Updated URN: " + str(temp_social_stash_i_user.create_update_user_in_snapbundle())
                del temp_social_stash_i_user
            except instagram.bind.InstagramAPIError:
                print "Unable to pull data for user " + current.username

    def get_feed_from_instagram(self, count):
        recent_media, url= self._api.user_recent_media(count=count)
        print recent_media
        response = requests.get(url)
        print response.json()
        return

    def get_instagrame_user_sb_urn(self):
        return self._instagram_user_sb_urn

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
          data['username'] = self.username
        data['full_name'] = self.full_name
        if self.profile_picture:
          data['profile_picture'] = self.profile_picture
        data['bio'] = self.bio
        data['website'] = self.website
        if self.counts is not None:
          data['counts'] = self.counts

        return data

