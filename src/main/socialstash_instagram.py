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
                    temp_social_stash_i_user.set_user_data_from_cached_or_snapbundle_data()

                if new_user or update_user_following_if_found or update_user_followedby_if_found:
                    self.create_update_snapbundle_relationships(relationship, temp_social_stash_i_user)

                # Check to see if we need to keep going down this follower/following thing recursively
                if go_to_max_depth and ((self.current_search_depth - 1) > 0):
                    temp_counts = temp_social_stash_i_user.get_counts()
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
            except instagram.bind.InstagramAPIError, error:
                print "Unable to pull data for user " + current.username + ": " + str(error) + ". Creating/Updating User with no metadata"
                logging.info("Unable to pull data for user " + current.username + ": " + str(error) + ". Creating/Updating User with no metadata")
                print "Added/Updated User URN: " + str(temp_social_stash_i_user.create_update_user_in_snapbundle_object_only())
                self.create_update_snapbundle_relationships(relationship, temp_social_stash_i_user)
            except instagram.bind.InstagramClientError, error:
                print "Unable to pull data for user " + current.username + ": " + str(error)
                logging.info("Unable to pull data for user " + current.username + ": " + str(error))
            except KeyError:
                print "Unable to pull data from SnapBundle for user " + current.username + ". User probably has no metadata associated with them (permission error in Instagram)"
                logging.info("Unable to pull data for user " + current.username + ". User probably has no metadata associated with them (permission error in Instagram)")
            except Exception, err:
                print Exception, err
                print traceback.format_exc()

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

        # Now let's deal with each individual post in the dictionary of posts we've gotten!!
        for key in post_dictionary:
            url = base_instagram_url_media + str(key) + '?access_token=' + self.access_token
            logging.info("Looking for file object at URL: " + str(url))
            response = requests.get(url)
            logging.info(str(response))
            try:
                if response.status_code != 200:
                    logging.debug("Response wasn't a 200, so skipping this media")
                    pass
                else:
                    current = response.json()['data']
                    # Check to make sure everything is kosher with this post
                    if current['user']['username'] == self.username:
                        logging.debug("Username on post and parent object match! (" + self.username + ")")
                    else:
                        logging.debug("Username on post and parent object don't match! ("
                                      + current['user']['username'] + " != " + self.username + " )")
                        continue # Skip this post

                    temp_post = {}
                    # This is the info that goes into the object interaction
                    temp_post['parent_urn'] = self._instagram_user_sb_object_urn
                    temp_post['attribution'] = current['attribution']
                    temp_post['id'] = current['id']
                    temp_post['created_time'] = current['created_time']

                    # This information will become metadata
                    temp_post['type'] = current['type']
                    temp_post['link'] = current['link']
                    temp_post['user_has_liked'] = current['user_has_liked']
#                    temp_post['images'] = current['images']

                    # This will become tags
                    temp_post['filter'] = current['filter']
                    temp_post['tags'] = current['tags']

                    # This will become a relationship
#                    temp_post['users_in_photo'] = current['users_in_photo']
#                    temp_post['likes'] = current['likes']

                    # These will become objects associated with it
#                    temp_post['location'] = current['location']
#                    temp_post['comments'] = current['comments']
#                    temp_post['caption'] = current['caption']

                    post_urn = snapbundle_instagram_fxns.add_new_instagram_post_object(temp_post)
                    print "post urn: " + str(post_urn)
                    exit()


                    print str(temp_post)
            except KeyError:
                pass
            exit()


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
