__author__ = 'prad'
__version__ = '1.0'

import instagram
import logging
import ConfigParser
import requests
import simplejson
import urlparse
import snapbundle_instagram_fxns
import traceback

logging.debug('Starting: ' + __name__)

# == Import all the account information that is stored in a local file (not sync'd wih public github)
config_file = 'accounts.txt'
config = ConfigParser.RawConfigParser()
config.read(config_file)

# == Snapbundle Variables ==
snapbundle_base_urn_instagram_user = "urn:instagram:users:"
# == End Snapbundle Variables ==

# == Instagram Variables ==
# number of records to get per request
instagram_record_count = 100
# number of feed records to get per request
instagram_feed_record_count = 100
# If the follows/following count is higher than this, don't bother going down the chain
instagram_max_follow_count = 50
# number of layers out to go when recursively searching
instagram_max_search_depth = 2
# == End Instagram Variables ==

# == Global Variables ==
# Need this one to save us calls to the instagram API (limited to 5000 per hour)
global_instagram_user_dictionary = {}
global_count_saved_api_calls = 0

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
            'following_dict':               None,
            'followedby_dict':              None,
            'api':                          None,
            'snapbundle_user_object':       None,
            'snapbundle_username':          None,
            'snapbundle_password':          None,
            'instagram_user_sb_object_urn': None,
            'instagram_user_sb_urn':        None,
            'current_search_depth':         instagram_max_search_depth}

        for (param, default) in param_defaults.iteritems():
            setattr(self, param, kwargs.get(param, default))

        if self._username is not None:
            self._instagram_user_sb_object_urn = snapbundle_instagram_fxns.snapbundle_base_urn_instagram_user + self._username

## ----------------------------------- FXN ------------------------------------------------------------------------
    def authenticate(self):
        logging.info("Authenticating and setting up Instagram API connection")
        self.api = instagram.client.InstagramAPI(access_token=self.access_token)

## ----------------------------------- FXN ------------------------------------------------------------------------
    def get_id_of_authenticated_user(self):
        return self.api.user().id

## ----------------------------------- FXN ------------------------------------------------------------------------
    def set_user_data_from_instagram(self, user_id):
        logging.info("Setting SocialStash Instagram User info from Instagram for user " + self.api.user(user_id).username)
        self.id = self.api.user(user_id).id
        self.username = self.api.user(user_id).username
        self.full_name = self.api.user(user_id).full_name
        self.profile_picture = self.api.user(user_id).profile_picture
        self.bio = self.api.user(user_id).bio
        self.website = self.api.user(user_id).website
        self.counts = self.api.user(user_id).counts
        self._instagram_user_sb_object_urn = snapbundle_instagram_fxns.snapbundle_base_urn_instagram_user + self._username
        logging.info("Initial user (" + self._username + ") search depth: " + str(self.current_search_depth))
        global global_instagram_user_dictionary
        if self._username not in global_instagram_user_dictionary:
            global_instagram_user_dictionary[self._username] = self

## ----------------------------------- FXN ------------------------------------------------------------------------
    def set_user_data_from_snapbundle_data(self):
        logging.info("Setting SocialStash Instagram User info from SnapBundle for user " + self.username)
        data = self.get_user_data_in_snapbundle()
        metadata = data['metadata']
        self.id = metadata['id']
        self.full_name = metadata['full_name']
        self.profile_picture = metadata['profile_picture']
        self.bio = metadata['bio']
        self.website = metadata['website']
        self.counts = metadata['counts']

        global global_instagram_user_dictionary
        global global_count_saved_api_calls
        global_count_saved_api_calls += 7
        if self._username not in global_instagram_user_dictionary:
            global_instagram_user_dictionary[self._username] = self

## ----------------------------------- FXN ------------------------------------------------------------------------
    def check_for_user_in_snapbundle(self):
        logging.info("Checking SnapBundle for URN: " + self._instagram_user_sb_object_urn)
        return snapbundle_instagram_fxns.check_for_object(self._instagram_user_sb_object_urn)

## ----------------------------------- FXN ------------------------------------------------------------------------
    def get_user_data_in_snapbundle(self):
        logging.info("Getting SnapBundle data for URN: " + self._instagram_user_sb_object_urn)
        object_data = snapbundle_instagram_fxns.get_object(self._instagram_user_sb_object_urn)
        object_metadata_dict = snapbundle_instagram_fxns.get_object_metadata_dictionary(self._instagram_user_sb_object_urn)
        return_data = {'object': object_data, 'metadata': object_metadata_dict}
        return return_data

## ----------------------------------- FXN ------------------------------------------------------------------------
    def create_update_user_in_snapbundle(self, new_user=False):
        self._instagram_user_sb_urn = snapbundle_instagram_fxns.add_update_new_instagram_user_object(self._username, self._instagram_user_sb_object_urn)
        snapbundle_instagram_fxns.update_instagram_user_object(self._instagram_user_sb_object_urn, self.AsDict(), new_user)
        self.check_and_update_profile_pic()
        return self._instagram_user_sb_urn

## ----------------------------------- FXN ------------------------------------------------------------------------
    def check_and_update_profile_pic(self):
        return snapbundle_instagram_fxns.check_update_user_profile_pic(self._username, self._profile_picture)

## ----------------------------------- FXN ------------------------------------------------------------------------
    def get_follow_list(self, relationship, use_cached_users=True):
        following_string = 'FOLLOWING'
        followed_by_string = 'FOLLOWED_BY'
        global global_instagram_user_dictionary
        global global_count_saved_api_calls
        if use_cached_users:
            if ((relationship.upper() == followed_by_string) and
                    (global_instagram_user_dictionary[self.username].get_followedby_dict() is not None)):
                global_count_saved_api_calls += 1
                print "Using cached copy of Followed By for " + self.username
                return global_instagram_user_dictionary[self.username].get_followedby_dict()
            elif ((relationship.upper() == following_string) and
                    (global_instagram_user_dictionary[self.username].get_following_dict() is not None)):
                global_count_saved_api_calls += 1
                print "Using cached copy of Following for " + self.username
                return global_instagram_user_dictionary[self.username].get_following_dict()

        # If we got here, we don't have this user info cached
        logging.debug("List of " + relationship + " for user " + self.username + " not found it cache, pulling it from API")
        user_dictionary = {}
        keep_going = True
        next_cursor = None
        # Check to make sure our API was initiated (it could not be b/c we pulled cached data out from SnapBundle
        if self.api is None:
            self.authenticate()
        while keep_going:
            # Get this set of users
            if relationship.upper() == followed_by_string:
                response, next_url = self.api.user_followed_by(user_id=self._id, count=instagram_record_count, cursor=next_cursor)
            elif relationship.upper() == following_string:
                response, next_url = self.api.user_follows(user_id=self._id, count=instagram_record_count, cursor=next_cursor)

            # Add them to a dictionarry
            for current in response:
                if current.username.encode() not in user_dictionary.keys():
                    user_dictionary[current.username.encode()] = current
            if next_url is None:
                keep_going = False
            else:
                # There are more we need to get, so here's the next cursor to start at
                next_cursor = str(urlparse.parse_qs(urlparse.urlparse(next_url).query)['cursor'][0])

        print relationship + " " + str(len(user_dictionary)) + " people"

        # Set or add the info to the global dictionary
        if relationship.upper() == followed_by_string:
            self.set_followedby_dict(user_dictionary)
            global_instagram_user_dictionary[self.username] = self
        elif relationship.upper() == following_string:
            self.set_following_dict(user_dictionary)
            global_instagram_user_dictionary[self.username] = self

        return user_dictionary

## ----------------------------------- FXN ------------------------------------------------------------------------
    def check_relationship_users_exist_in_snapbundle(self, relationship,
                                                     update_user_profile_if_found=False,
                                                     update_user_following_if_found=False,
                                                     update_user_followedby_if_found=False,
                                                     go_to_max_depth=False,
                                                     use_cached_users=True):

        following_string = 'FOLLOWING'
        followed_by_string = 'FOLLOWED_BY'
        user_dictionary = self.get_follow_list(relationship, use_cached_users)

        # Now start going through all the users and checking to see if they exist
        # We will do this recursively, using the search_follow_depth variable
        for key in user_dictionary:
            current = user_dictionary[key]
            if relationship.upper() == followed_by_string:
                print "Followed by: " + str(current.username)
            elif relationship.upper() == following_string:
                print "Following: " + str(current.username)

            try:
                temp_social_stash_i_user = User(access_token=self.access_token,
                                                snapbundle_user_object=self._snapbundle_user_object,
                                                snapbundle_username=self._snapbundle_username,
                                                snapbundle_password=self._snapbundle_password,
                                                username=current.username,
                                                current_search_depth=(self.current_search_depth - 1))
                print "Checking for SocialStash Instagram User " + current.username + " in SnapBundle"
                do_profile_update = False
                new_user = False
                user_data_response = temp_social_stash_i_user.check_for_user_in_snapbundle()
                if not user_data_response:
                    print "User not found!  Creating New User"
                    new_user = True
                    do_profile_update = True
                else:
                    print "User exists!"
                    if update_user_profile_if_found:
                        print "Updating User " + current.username + " anyway"
                        do_profile_update = True

                if do_profile_update:
                    temp_social_stash_i_user.authenticate()
                    temp_social_stash_i_user.set_user_data_from_instagram(current.id)
                    print "Added/Updated User URN: " + \
                          str(temp_social_stash_i_user.create_update_user_in_snapbundle(new_user=new_user))
                    # Time to check the profile pic
                    temp_social_stash_i_user.check_and_update_profile_pic()
                else:
                    # We need to pull the data from SnapBundle instead of the Instagram API
                    temp_social_stash_i_user.set_user_data_from_snapbundle_data()

                if new_user or update_user_following_if_found or update_user_followedby_if_found:
                    # Time to check and add a relationships.  Remember, they actually go both ways, so either way,
                    # we're adding/updating two relationships
                    # A -- Follows ------> B
                    # B -- Followed by --> A
                    if relationship.upper() == followed_by_string:
                        snapbundle_instagram_fxns.check_add_update_followed_by(self.get_instagrame_user_sb_object_urn(),
                                                                               temp_social_stash_i_user.get_instagrame_user_sb_object_urn())
                        snapbundle_instagram_fxns.check_add_update_follows(temp_social_stash_i_user.get_instagrame_user_sb_object_urn(),
                                                                           self.get_instagrame_user_sb_object_urn())
                    elif relationship.upper() == following_string:
                        snapbundle_instagram_fxns.check_add_update_follows(self.get_instagrame_user_sb_object_urn(),
                                                                           temp_social_stash_i_user.get_instagrame_user_sb_object_urn())
                        snapbundle_instagram_fxns.check_add_update_followed_by(temp_social_stash_i_user.get_instagrame_user_sb_object_urn(),
                                                                               self.get_instagrame_user_sb_object_urn())

                # Check to see if we need to keep going down this follower/following thing recursively
                if go_to_max_depth and ((self.current_search_depth - 1) > 0):
                    temp_counts = temp_social_stash_i_user.get_counts()
                    count_to_check = int(temp_counts['followed_by'])
                    logging.info(current.username + "'s followed_by count: " + str(count_to_check) + " (max_follow: " + str(instagram_max_follow_count) + "), depth: " + str((self.current_search_depth-1)))
                    if count_to_check <= instagram_max_follow_count:
                        logging.info(current.username + "'s followed_by count: " + str(count_to_check) + "<=" + str(instagram_max_follow_count) + ", depth: " + str((self.current_search_depth-1)) + ">0")
                        logging.info("Continuing down the follow recursion")
                        temp_social_stash_i_user.check_relationship_users_exist_in_snapbundle(followed_by_string,
                                                                                              update_user_profile_if_found,
                                                                                              update_user_following_if_found,
                                                                                              update_user_followedby_if_found,
                                                                                              go_to_max_depth)
                    else:
                        logging.info(current.username + "'s followed_by count: " + str(count_to_check) + ">" + str(instagram_max_follow_count) + ", depth: " + str((self.current_search_depth-1)) + ">0")

                    count_to_check = int(temp_counts['follows'])
                    logging.info(current.username + "'s follows count: " + str(count_to_check) + " (max_follow: " + str(instagram_max_follow_count) + "), depth: " + str((self.current_search_depth-1)))
                    if count_to_check <= instagram_max_follow_count:
                        logging.info(current.username + "'s follows count: " + str(count_to_check) + "<=" + str(instagram_max_follow_count) + ", depth: " + str((self.current_search_depth-1)) + ">0")
                        logging.info("Continuing down the follow recursion")
                        temp_social_stash_i_user.check_relationship_users_exist_in_snapbundle(following_string,
                                                                                              update_user_profile_if_found,
                                                                                              update_user_following_if_found,
                                                                                              update_user_followedby_if_found,
                                                                                              go_to_max_depth)
                    else:
                        logging.info(current.username + "'s follows count: " + str(count_to_check) + ">" + str(instagram_max_follow_count) + ", depth: " + str((self.current_search_depth-1)) + ">0")

                else:
                    logging.info("Not continuing down the follow recursion...  (max_follow: " + str(instagram_max_follow_count) + "), depth: " + str((self.current_search_depth-1)))

                del temp_social_stash_i_user
            except instagram.bind.InstagramAPIError:
                print "Unable to pull data for user " + current.username + ".  Possible permission error?"
                logging.info("Unable to pull data for user " + current.username + ".  Possible permission error?")
            except instagram.bind.InstagramClientError:
                print "Unable to pull data for user " + current.username + ".  Possible permission error?"
                logging.info("Unable to pull data for user " + current.username + ".  Possible permission error?")
            except Exception, err:
                print Exception, err
                print traceback.format_exc()
#            except KeyError:
#                print "Unable to pull data for user " + current.username + ".  Weird KeyError"
#                logging.info("Unable to pull data for user " + current.username + ".  Weird KeyError")

## ----------------------------------- FXN ------------------------------------------------------------------------
    def check_recent_media_exists_in_snapbundle(self, update_if_found=False):
        post_dictionary = {}
        keep_going = True

        ## Need to find a way to set the next_max_id to be the latest post we already have in Snapbundle
        next_max_id = None
        while keep_going:
            # Get this set of posts
            response, next_url = self.api.user_recent_media(count=instagram_feed_record_count, max_id=next_max_id)

            # Add them to a dictionary
            for current in response:
                if current.id.encode() not in post_dictionary.keys():
                    post_dictionary[current.id.encode()] = current
            if next_url is None:
                keep_going = False
            else:
                # There are more we need to get, so here's the next cursor to start at
                next_max_id = str(urlparse.parse_qs(urlparse.urlparse(next_url).query)['next_max_id'][0])

        # Now start going through all the users and checking to see if they exist
        # We will do this recursively, using the search_follow_depth variable
        for key in post_dictionary:
            current = post_dictionary[key]['data']
            temp_post = {}
            temp_post['parent_urn'] = self._instagram_user_sb_object_urn
            temp_post['id'] = current['id']
            temp_post['type'] = current['type']
            temp_post['created_time'] = current['created_time']
            temp_post['link'] = current['link']
            temp_post['user'] = current['user']
            temp_post['location'] = current['location']
            temp_post['attribution'] = current['attribution']

            #FIGURE OUT THE OTHER LOCATION INFO to send before creating t
            #FIGURE OUT THE ATTRIBUTION PART TOO

            #post_urn = FUNCTION CALL HERE
            #snapbundle_instagram_fxns.set_filter_tag(post_urn, current['filter'])


## ----------------------------------- FXN ------------------------------------------------------------------------
    def get_feed_from_instagram(self, count):
        recent_media, url= self.api.user_recent_media(count=count)
        print recent_media
        response = requests.get(url)
        print response.json()
        return

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
        return simplejson.dumps(self.AsDict(), sort_keys=True)

## ----------------------------------- FXN ------------------------------------------------------------------------
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

## ----------------------------------- FXN ------------------------------------------------------------------------
    @staticmethod
    def get_global_count_saved_api_calls(self):
        global global_count_saved_api_calls
        return global_count_saved_api_calls

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
