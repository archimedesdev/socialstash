__author__ = 'prad'
__version__ = '1.0'

import instagram
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

logging.debug('Starting: ' + __name__)

# == Import all the account information that is stored in a local file (not sync'd wih public github)
config_file = 'accounts.txt'
config = ConfigParser.RawConfigParser()
config.read(config_file)

# == Instagram API URLs ==
base_instagram_url_media = "https://api.instagram.com/v1/media/"
base_instagram_url_locations = "https://api.instagram.com/v1/locations/"

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
        global global_counts_dictionary
        global_counts_dictionary['api_calls'] += 7
        if self._username not in global_instagram_user_dictionary:
            global_instagram_user_dictionary[self._username] = self

## ----------------------------------- FXN ------------------------------------------------------------------------
    def set_user_data_from_cached_or_snapbundle_data(self):
        global global_instagram_user_dictionary
        global global_count_saved_api_calls
        global global_counts_dictionary
        global_count_saved_api_calls += 6
        if self._username in global_instagram_user_dictionary.keys():
            logging.info("Setting SocialStash Instagram User info from Cached Data for user " + self.username)
            cache_data = global_instagram_user_dictionary[self._username]
            self.id = cache_data.id
            self.full_name = cache_data.full_name
            self.profile_picture = cache_data.profile_picture
            self.bio = cache_data.bio
            self.website = cache_data.website
            self.counts = cache_data.counts
            global_counts_dictionary['cache_calls'] += 6
            return

        logging.info("Setting SocialStash Instagram User info from SnapBundle for user " + self.username)
        data = self.get_user_data_in_snapbundle()
        #print str(data)
        metadata = data['metadata']
        self.id = metadata['id']
        self.full_name = metadata['full_name']
        self.profile_picture = metadata['profile_picture']
        self.bio = metadata['bio']
        self.website = metadata['website']
        self.counts = metadata['counts']
        global_counts_dictionary['snapbundle_calls'] += 6
        if self._username not in global_instagram_user_dictionary:
            global_instagram_user_dictionary[self._username] = self

## ----------------------------------- FXN ------------------------------------------------------------------------
    def check_for_user_in_snapbundle(self):
        global global_counts_dictionary
        global_counts_dictionary['snapbundle_calls'] += 1
        logging.info("Checking SnapBundle for URN: " + self._instagram_user_sb_object_urn)
        return snapbundle_instagram_fxns.check_for_object(self._instagram_user_sb_object_urn)

## ----------------------------------- FXN ------------------------------------------------------------------------
    def get_user_data_in_snapbundle(self):
        global global_counts_dictionary
        global_counts_dictionary['snapbundle_calls'] += 1
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
    def create_update_user_in_snapbundle_object_only(self):
        self._instagram_user_sb_urn = snapbundle_instagram_fxns.add_update_new_instagram_user_object(self._username, self._instagram_user_sb_object_urn)
        return self._instagram_user_sb_urn

## ----------------------------------- FXN ------------------------------------------------------------------------
    def check_and_update_profile_pic(self):
        return snapbundle_instagram_fxns.check_update_user_profile_pic(self._username, self._profile_picture)

## ----------------------------------- FXN ------------------------------------------------------------------------
    def update_relationship_node_list_snapbundle(self, relationship, depth=1, user=None, user_dictionary=None):
        global global_counts_dictionary
        global global_relationship_edge_list
        global global_relationship_node_list
        global_counts_dictionary['snapbundle_calls'] += 1
        if not user:
            user = str(self.username)

        if not user_dictionary:
            user_dictionary = snapbundle_instagram_fxns.get_object_relationships(self._instagram_user_sb_object_urn,
                                                                                 relationship)
        print relationship + " " + str(len(user_dictionary)) + " pairs (SnapBundle)"

        # Add the current node name into the node list if it doesn't exist
        if user not in global_relationship_node_list:
            global_relationship_node_list.append(user)

        for current_name in user_dictionary.keys():
            if relationship.upper() == global_followed_by_string:
                temp_set = (current_name, user)
            elif relationship.upper() == global_following_string:
                temp_set = (user, current_name)

            # Add the node into the node list if it doesn't exist
            if current_name not in global_relationship_node_list:
                global_relationship_node_list.append(current_name)

            # Add the edge into the edge list if it doesn't exist
            if temp_set not in global_relationship_edge_list:
                global_relationship_edge_list.append(temp_set)

            if (depth - 1) > 0:
                sub_sb_object_urn = snapbundle_instagram_fxns.get_urn_from_username(current_name)
                subuser_dictionary = snapbundle_instagram_fxns.get_object_relationships(sub_sb_object_urn, relationship)
                if subuser_dictionary != {}:
                    self.update_relationship_node_list_snapbundle(relationship, depth-1, current_name, subuser_dictionary)

        print "Global Relationship Node List length: " + str(len(global_relationship_edge_list))

## ----------------------------------- FXN ------------------------------------------------------------------------
    def get_follow_list_snapbundle(self, relationship):
        global global_counts_dictionary
        global_counts_dictionary['snapbundle_calls'] += 1
        user_dictionary = snapbundle_instagram_fxns.get_object_relationships(self._instagram_user_sb_object_urn,
                                                                             relationship)
        print relationship + " " + str(len(user_dictionary)) + " people (SnapBundle)"
        return user_dictionary

## ----------------------------------- FXN ------------------------------------------------------------------------
    def get_follow_list_instagram(self, relationship, use_cached_users=True):
        global global_instagram_user_dictionary
        global global_count_saved_api_calls
        global global_counts_dictionary
        # We might already have this information cached in our current Python session, and if told to, let's use it
        if use_cached_users:
            if ((relationship.upper() == global_followed_by_string) and
                    (global_instagram_user_dictionary[self.username].get_followedby_dict() is not None)):
                global_count_saved_api_calls += 1
                global_counts_dictionary['cache_calls'] += 1
                print "Using cached copy of Followed By for " + self.username
                return global_instagram_user_dictionary[self.username].get_followedby_dict()
            elif ((relationship.upper() == global_following_string) and
                    (global_instagram_user_dictionary[self.username].get_following_dict() is not None)):
                global_count_saved_api_calls += 1
                global_counts_dictionary['cache_calls'] += 1
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
            if relationship.upper() == global_followed_by_string:
                response, next_url = self.api.user_followed_by(user_id=self._id, count=instagram_record_count, cursor=next_cursor)
            elif relationship.upper() == global_following_string:
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

        print relationship + " " + str(len(user_dictionary)) + " people (Instagram)"

        # Set or add the info to the global dictionary
        if relationship.upper() == global_followed_by_string:
            self.set_followedby_dict(user_dictionary)
            global_instagram_user_dictionary[self.username] = self
        elif relationship.upper() == global_following_string:
            self.set_following_dict(user_dictionary)
            global_instagram_user_dictionary[self.username] = self

        global_counts_dictionary['api_calls'] += 1
        return user_dictionary

## ----------------------------------- FXN ------------------------------------------------------------------------
    def check_relationship_users_exist_in_snapbundle(self, relationship,
                                                     update_user_profile_if_found=False,
                                                     update_user_following_if_found=False,
                                                     update_user_followedby_if_found=False,
                                                     go_to_max_depth=False,
                                                     use_cached_users=True):

        instagram_follow_user_dictionary = self.get_follow_list_instagram(relationship, use_cached_users)
        snapbundle_follow_user_dictoinary = self.get_follow_list_snapbundle(relationship)

        print str(snapbundle_follow_user_dictoinary)

        # Now start going through all the users and checking to see if they exist
        # We will do this recursively, using the search_follow_depth variable
        for key in instagram_follow_user_dictionary:
            current = instagram_follow_user_dictionary[key]
            if relationship.upper() == global_followed_by_string:
                print "Followed by: " + str(current.username)
            elif relationship.upper() == global_following_string:
                print "Following: " + str(current.username)

            # We need to keep track of any users that are in SnapBundle and not Instagram, so if we see him in
            # Instagram list we can make note of it so we don't later delete that relationship from SnapBundle
            if current.username in snapbundle_follow_user_dictoinary.keys():
                snapbundle_follow_user_dictoinary[current.username] = 'VALID'

            temp_social_stash_i_user, new_user = self.check_users_exist_in_snapbundle(current.username, current.id, update_user_profile_if_found, self.current_search_depth, relationship)
            if temp_social_stash_i_user != False:
                if new_user or update_user_following_if_found or update_user_followedby_if_found:
                    self.create_update_snapbundle_relationships(relationship, temp_social_stash_i_user)

                # Check to see if we need to keep going down this follower/following thing recursively
                if go_to_max_depth and ((self.current_search_depth - 1) > 0):
                    temp_counts = temp_social_stash_i_user.get_counts()
                    if temp_counts is not None:
                        count_to_check = int(temp_counts['followed_by'])
                        logging.info(current.username + "'s followed_by count: " + str(count_to_check) + " (max_follow: " + str(instagram_max_follow_count) + "), depth: " + str((self.current_search_depth-1)))
                        if count_to_check <= instagram_max_follow_count:
                            logging.info(current.username + "'s followed_by count: " + str(count_to_check) + "<=" + str(instagram_max_follow_count) + ", depth: " + str((self.current_search_depth-1)) + ">0")
                            logging.info("Continuing down the follow recursion")
                            temp_social_stash_i_user.check_relationship_users_exist_in_snapbundle(global_followed_by_string,
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
                            temp_social_stash_i_user.check_relationship_users_exist_in_snapbundle(global_following_string,
                                                                                                  update_user_profile_if_found,
                                                                                                  update_user_following_if_found,
                                                                                                  update_user_followedby_if_found,
                                                                                                  go_to_max_depth)
                        else:
                            logging.info(current.username + "'s follows count: " + str(count_to_check) + ">" + str(instagram_max_follow_count) + ", depth: " + str((self.current_search_depth-1)) + ">0")
                else:
                    logging.info("Not continuing down the follow recursion...  (max_follow: " + str(instagram_max_follow_count) + "), depth: " + str((self.current_search_depth-1)))

                del temp_social_stash_i_user

        # Time to go through our snapbundle relationships dictionary to see if there are any we need to delete
        global global_counts_dictionary
        for current_check_delete in snapbundle_follow_user_dictoinary.keys():
            if snapbundle_follow_user_dictoinary[current_check_delete] != 'VALID':
                # This relationship needs to be deleted in SnapBundle
                logging.info("Deleting SnapBundle relationship: " + self.username + ' ' + relationship + ' ' + current_check_delete)
                snapbundle_instagram_fxns.delete_relationship(snapbundle_follow_user_dictoinary[current_check_delete])
                global_counts_dictionary['snapbundle_deletes'] += 1

## ----------------------------------- FXN ------------------------------------------------------------------------
    def create_update_snapbundle_relationships(self, relationship, temp_social_stash_i_user):
        # Time to check and add a relationships.  Remember, they actually go both ways, so either way,
        # we're adding/updating two relationships
        # A -- Follows ------> B
        # B -- Followed by --> A
        if relationship.upper() == global_followed_by_string:
            snapbundle_instagram_fxns.check_add_update_followed_by(self.get_instagrame_user_sb_object_urn(),
                                                                   temp_social_stash_i_user.get_instagrame_user_sb_object_urn())
            snapbundle_instagram_fxns.check_add_update_follows(temp_social_stash_i_user.get_instagrame_user_sb_object_urn(),
                                                               self.get_instagrame_user_sb_object_urn())
        elif relationship.upper() == global_following_string:
            snapbundle_instagram_fxns.check_add_update_follows(self.get_instagrame_user_sb_object_urn(),
                                                               temp_social_stash_i_user.get_instagrame_user_sb_object_urn())
            snapbundle_instagram_fxns.check_add_update_followed_by(temp_social_stash_i_user.get_instagrame_user_sb_object_urn(),
                                                                   self.get_instagrame_user_sb_object_urn())

## ----------------------------------- FXN ------------------------------------------------------------------------
    def check_users_exist_in_snapbundle(self, username, id, update_user_profile_if_found, search_depth, relationship=None):
        try:
            temp_social_stash_i_user = User(access_token=self.access_token,
                                            snapbundle_user_object=self._snapbundle_user_object,
                                            snapbundle_username=self._snapbundle_username,
                                            snapbundle_password=self._snapbundle_password,
                                            username=username,
                                            current_search_depth=(search_depth - 1))
            print "Checking for SocialStash Instagram User " + username + " in SnapBundle"
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
                    print "Updating User " + username + " anyway"
                    do_profile_update = True

            if do_profile_update:
                temp_social_stash_i_user.authenticate()
                temp_social_stash_i_user.set_user_data_from_instagram(id)
                print "Added/Updated User URN: " + \
                      str(temp_social_stash_i_user.create_update_user_in_snapbundle(new_user=new_user))
                # Time to check the profile pic
                temp_social_stash_i_user.check_and_update_profile_pic()
            else:
                # We need to pull the data from SnapBundle instead of the Instagram API
                temp_social_stash_i_user.set_user_data_from_cached_or_snapbundle_data()

            return temp_social_stash_i_user, new_user
        except instagram.bind.InstagramAPIError, error:
            print "Unable to pull data for user " + username + ": " + str(error) + ". Creating/Updating User with no metadata"
            logging.info("Unable to pull data for user " + username + ": " + str(error) + ". Creating/Updating User with no metadata")
            print "Added/Updated User URN: " + str(temp_social_stash_i_user.create_update_user_in_snapbundle_object_only())
            if relationship is not None:
                self.create_update_snapbundle_relationships(relationship, temp_social_stash_i_user)
            return temp_social_stash_i_user, new_user
        except instagram.bind.InstagramClientError, error:
            print "Unable to pull data for user " + username + ": " + str(error)
            logging.info("Unable to pull data for user " + username + ": " + str(error))
            return False, False
        except KeyError:
            print "Unable to pull data from SnapBundle for user " + username + ". User probably has no metadata associated with them (permission error in Instagram)"
            logging.info("Unable to pull data for user " + username + ". User probably has no metadata associated with them (permission error in Instagram)")
            return False, False
        except Exception, err:
            print Exception, err
            print traceback.format_exc()
            return False, False

## ----------------------------------- FXN ------------------------------------------------------------------------
    def print_relationship_node_list(self, manual_pull_from_snapbundle=False, relationship=None, depth=1):
        if manual_pull_from_snapbundle and (relationship is not None):
            self.update_relationship_node_list_snapbundle(relationship, depth)

        graph = self.get_global_relationship_node_list()
        print str(graph)


        # extract nodes from graph
        nodes = set([n1 for n1, n2 in graph] + [n2 for n1, n2 in graph])

        # create networkx graph
        G = nx.Graph()

        # add nodes
        for node in nodes:
            G.add_node(node)

        # add edges
        for edge in graph:
            G.add_edge(edge[0], edge[1])

        # draw graph
        pos = nx.shell_layout(G)
        nx.draw(G, pos)

        # show graph
        plt.show()

## ----------------------------------- FXN ------------------------------------------------------------------------
    def output_relationship_node_gml(self, filename='output.gml', depth=1):
        global global_relationship_node_list
        global global_relationship_edge_list
        self.update_relationship_node_list_snapbundle('FOLLOWING', depth)
        self.update_relationship_node_list_snapbundle('FOLLOWED_BY', depth)

        tab = '\t'
        linesep = '\n'
        f = open(filename, 'w')
        f.write("graph [" + linesep)
        f.write(tab + 'comment "This is a sample graph"' + linesep)
        f.write(tab + 'directed 1' + linesep)
        f.write(tab + 'id 42' + linesep)
        f.write(tab + 'label "Hello, I am a sample graph"' + linesep)

        for current_node in global_relationship_node_list:
            f.write(tab + "node [" + linesep)
            f.write(tab + tab + "id " + str(global_relationship_node_list.index(current_node)) + linesep)
            f.write(tab + tab + 'label "' + current_node + '"' + linesep)
            f.write(tab + ']' + linesep)

        for current_edge in global_relationship_edge_list:
            f.write(tab + "edge [" + linesep)
            f.write(tab + tab + "source " + str(global_relationship_node_list.index(current_edge[0])) + linesep)
            f.write(tab + tab + "target " + str(global_relationship_node_list.index(current_edge[1])) + linesep)
            f.write(tab + tab + 'label "' + current_edge[0] + ' follows ' + current_edge[1] + '"' + linesep)
            f.write(tab + ']' + linesep)

        f.write("]" + linesep)
        f.close()

## ----------------------------------- FXN ------------------------------------------------------------------------
    @staticmethod
    def graph_relationship_gml(filename='output.gml'):
        # read the graph (gml format)
        G = nx.read_gml(filename, relabel=True)

        # drawing the full network
        pylab.figure(1)
        nx.draw_spring(G, node_size=0, node_color='w', edge_color='b', alpha=.2, font_size=8, iterations=50)
        pylab.show()

## ----------------------------------- FXN ------------------------------------------------------------------------
    def check_recent_media_exists_in_snapbundle(self, user_username=None, user_id=None, update_if_found=False):
        posts_udated = 0
        post_dictionary = {}
        keep_going = True
        # If no Instagram user id was passed in, we assume it's for us
        if not user_id:
            user_id = self.id
            user_username = self.username

        ## Need to find a way to set the next_max_id to be the latest post we already have in Snapbundle
        next_max_id = None
        while keep_going:
            # Get this set of posts
            response, next_url = self.api.user_recent_media(user_id=user_id, count=instagram_feed_record_count, max_id=next_max_id)

            # Add them to a dictionary
            for current in response:
                if current.id.encode() not in post_dictionary.keys():
                    post_dictionary[current.id.encode()] = current
            if next_url is None:
                keep_going = False
            else:
                # There are more we need to get, so here's the next cursor to start at
                #print str(next_url)
                #next_max_id = str(urlparse.parse_qs(urlparse.urlparse(next_url).query)['next_max_id'][0])
                next_max_id = str(urlparse.parse_qs(urlparse.urlparse(next_url).query)['max_id'][0])

        # Now let's deal with each individual post in the dictionary of posts we've gotten!!
        for key in post_dictionary:
            url = base_instagram_url_media + str(key) + '?access_token=' + self.access_token
            logging.info("Looking for Instagram Post at URL: " + str(url))
            response = requests.get(url)
            logging.info(str(response))
            try:
                if response.status_code != 200:
                    logging.debug("Response wasn't a 200, so skipping this media")
                    continue
                else:
                    current = response.json()['data']

                    # TEMP
                    just_use = '260216321725120589_9103023'
                    #just_use = '603233164163236582_9103023' #krom's long  comment text
                    #just_use = '620621129814330121_225958025' #alexpt48 picture
                    #just_use = '518265249027017009_225958025' #alexpt48 video
                    #just_use = '605971004470914431_513507874' #Winerly location
                    #just_use = '560874534243987153_513507874' #Post with no caption
                    #just_use = '560867689500569094_513507874' #Dolly sods with a comment
                    #just_use = '620310392478690795_513507874' #flashback friday shit eating grin
                    #if current['id'] != just_use:
                    #    continue

                    # First check to see if this post already exists, unless we're just going to update it anyway
                    if not update_if_found:
                        post_exists = snapbundle_instagram_fxns.check_for_post(current['id'])
                        if post_exists:
                            print "Skipping Post " + str(current['id'])
                            logging.info("Told not to update existing posts.  Post " + str(current['id']) + " found.  Skipping")
                            continue

                    # Check to make sure everything is kosher with this post
                    if current['user']['username'] == user_username:
                        logging.debug("Username on post and calling object match! (" + str(user_username) + ")")
                    else:
                        logging.debug("Username on post and calling object don't match! ("
                                      + current['user']['username'] + " != " + str(user_username) + " )")
                        continue # Skip this post

                    print "Working with Post: " + str(current['id'])
                    temp_post = {}
                    # This is the info that goes into the object interaction
                    temp_post['parent_urn'] = snapbundle_instagram_fxns.get_urn_from_username(user_username) #self._instagram_user_sb_object_urn
                    temp_post['attribution'] = current['attribution']
                    temp_post['id'] = current['id']
                    temp_post['created_time'] = current['created_time']

                    # This information will become metadata
                    temp_post['type'] = current['type']
                    temp_post['link'] = current['link']
                    temp_post['caption'] = current['caption']
                    temp_post['user_has_liked'] = current['user_has_liked']
                    if temp_post['type'] == 'image':
                        temp_post['images'] = current['images']
                    elif temp_post['type'] == 'video':
                        temp_post['videos'] = current['videos']
                    temp_post['likes'] = current['likes']
                    temp_post['comments'] = current['comments']

                    # This will become tags
                    temp_post['filter'] = current['filter']
                    temp_post['tags'] = current['tags']

                    # This will become a relationship
#                    temp_post['users_in_photo'] = current['users_in_photo']

                    # Need to create the post and get its URN back before we can do any additional relationships
                    post_urn = snapbundle_instagram_fxns.add_new_instagram_post_object(temp_post)

                    # Time to take care of our caption
                    if temp_post['caption'] is not None:
                        caption_urn = snapbundle_instagram_fxns.add_new_instagram_comment(temp_post['caption']['id'],
                                                                                          temp_post['caption']['created_time'],
                                                                                          temp_post['caption']['text'],
                                                                                          temp_post['caption']['from']['username'],
                                                                                          post_urn,
                                                                                          is_caption=True)
                        if caption_urn:
                            logging.debug("Succesfully created post caption with urn: " + str(caption_urn))
                        else:
                            logging.debug("Failed to successfully create the post caption")

                    # Time to go get our comments
                    if temp_post['comments']['count'] > 0:
                        url3 = base_instagram_url_media + str(key) + '/comments?access_token=' + self.access_token
                        logging.info("Looking for Instagram Post Comments at URL: " + str(url3))
                        response3 = requests.get(url3)
                        logging.info(str(response3))
                        if response3.status_code != 200:
                            logging.debug("Response wasn't a 200!!! WTF, so skipping this media likes")
                        else:
                            comments_data = response3.json()['data']
                            for current_comment in comments_data:
                                # First we'll check that the creator of the comment exists in SB
                                logging.debug("Checking into existance of user who commented on post: " + str(current_comment['from']['username']))
                                temp_social_stash_i_user, new_user = self.check_users_exist_in_snapbundle(str(current_comment['from']['username']),
                                                                                                          str(current_comment['from']['id']),
                                                                                                          update_user_profile_if_found=False,
                                                                                                          search_depth=1)
                                if temp_social_stash_i_user:
                                    # The user either exists or was created, so let's create this comment
                                    comment_urn = snapbundle_instagram_fxns.add_new_instagram_comment(current_comment['id'],
                                                                                                      current_comment['created_time'],
                                                                                                      current_comment['text'],
                                                                                                      current_comment['from']['username'],
                                                                                                      post_urn,
                                                                                                      is_caption=False)

                    likes_users = temp_post['likes']['data']
                    # Need to see if the number of likes in our data list is equal to the number stated.  Instagram will
                    # Only include a couple if there are many likes

                    #TEMP WORK AROUND UNTIL INSTAGRAM FIXES THE API
                    if False:
                    #if temp_post['likes']['count'] != len(likes_users):
                        # If the number of user likes in the post don't match the total, need to go get them!
                        url2 = base_instagram_url_media + str(key) + '/likes?access_token=' + self.access_token
                        logging.info("Numbers didn't match! Looking for Instagram Post Likes at URL: " + str(url2))
                        response2 = requests.get(url2)
                        logging.info(str(response2))
                        if response2.status_code != 200:
                            logging.debug("Response wasn't a 200!!! WTF, so skipping this media likes")
                        else:
                            likes_users = response2.json()['data']
                    for current_user in likes_users:
                        logging.debug("Checking into existance of user who liked post: " + str(current_user['username']))
                        temp_social_stash_i_user, new_user = self.check_users_exist_in_snapbundle(str(current_user['username']),
                                                                                                  str(current_user['id']),
                                                                                                  update_user_profile_if_found=False,
                                                                                                  search_depth=1)
                        if temp_social_stash_i_user:
                            like_user_urn = temp_social_stash_i_user.get_instagrame_user_sb_object_urn()
                            snapbundle_instagram_fxns.add_user_likes_post(like_user_urn, post_urn)
                    ####### End User Likes

                    # These will become objects associated with it
                    temp_post['location'] = current['location']
                    if temp_post['location'] is not None:
                        # As it turns out, some locations are just Lat Lon and don't have a location stored in Instagram
                        if 'name' not in temp_post['location']:
                            use_default_location_name = False
                            if 'id' in temp_post['location']:
                                # Check instagram for a name if there is one
                                url4 = base_instagram_url_locations + '/' + str(temp_post['location']['id']) + '?access_token=' + self.access_token
                                logging.info("Looking for Instagram at URL: " + str(url4))
                                response4 = requests.get(url4)
                                logging.info(str(response4))
                                if response4.status_code != 200:
                                    logging.debug("Response wasn't a 200!!! WTF, so skipping this media likes")
                                    use_default_location_name = True
                                else:
                                    location_info = response4.json()['data']
                                    if 'name' not in location_info:
                                        use_default_location_name = True
                                    else:
                                        temp_post['location']['name'] = location_info['name']
                                        temp_post['location']['latitude'] = location_info['latitude']
                                        temp_post['location']['longitude'] = location_info['longitude']
                            else:
                                use_default_location_name = True
                            if use_default_location_name:
                                temp_post['location']['name'] = "Location for post " + str(temp_post['id'] + " by user " + current['user']['username'])

                        if 'id' not in temp_post['location']:
                            temp_post['location']['id'] = 'post_' + str(temp_post['id'])

                        if ('latitude' not in temp_post['location']) or (temp_post['location']['latitude'] is None):
                            temp_post['location']['latitude'] = "0.0"

                        if ('longitude' not in temp_post['location']) or (temp_post['location']['longitude'] is None):
                            temp_post['location']['longitude'] = "0.0"

                        loc_urn = snapbundle_instagram_fxns.add_new_instagram_post_location(post_urn,
                                                                                            temp_post['location']['id'],
                                                                                            temp_post['location']['name'],
                                                                                            temp_post['location']['latitude'],
                                                                                            temp_post['location']['longitude'])
                    print "Finished with Post, URN: " + str(post_urn)
                    posts_udated += 1
                    #return posts_udated

            except KeyError, err:
                print KeyError, err
                print traceback.format_exc()
                logging.info("Key Error encountered")

        return posts_udated

## ----------------------------------- FXN ------------------------------------------------------------------------
    def update_user_feed_in_snapbundle(self, username, update_if_found=False):
        logging.info("Looking to update user " + str(username) + "'s media feed in SnapBundle")
        if username in global_instagram_user_dictionary:
            user = global_instagram_user_dictionary[username]
            if user.api is None:
                user.authenticate()
            logging.info("Using API from user X to update posts from user Y (" + str(user.username) + ":" + str(username) + ")")
            num_updates = user.check_recent_media_exists_in_snapbundle(update_if_found=update_if_found)
            return num_updates
        else:
            logging.info("User not found in cached user dictionary, seeing if we can pull their user id out of snapbundle")
            user_id = snapbundle_instagram_fxns.get_id_from_username(username)
            if user_id:
                logging.info("User ID for user " + username + " found: (" + str(user_id) + ")")
                logging.info("Using API from user X to update posts from user Y (" + str(self.username) + ":" + str(username) + ")")
                num_updates = self.check_recent_media_exists_in_snapbundle(user_username=username, user_id=user_id, update_if_found=update_if_found)
                return num_updates
        return 0

## ----------------------------------- FXN ------------------------------------------------------------------------
    def get_feed_from_instagram(self, count):
        recent_media, url= self.api.user_recent_media(count=count)
        print recent_media
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
        return json.dumps(self.AsDict(), sort_keys=True)

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
