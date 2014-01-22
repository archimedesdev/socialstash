__author__ = 'prad'

import ConfigParser
import logging
import ast
import socialstash_instagram
import time
import datetime
import cmd

logging.debug('Starting: ' + __name__)



class userdata_instagram(cmd.Cmd):

    ###################################################################################################################
    def do_start(self, instagram_handle):
        """ start [instagram_handle]
        First thing you need to do to start everything
        """
        # == Import all the account information that is stored in a local file (not sync'd wih public github)
        config_file = 'accounts.txt'
        self.config = ConfigParser.RawConfigParser()
        self.config.read(config_file)

        # == Instagram OAuth Authentication ==
        # This mode of authentication is the new preferred way
        # of authenticating with Twitter.
        #pr_client_id = config.get('InstagramApplicationAccounts', 'clientID')
        #pr_client_secret = config.get('InstagramApplicationAccounts', 'clientSecret')
        self.instagrame_access_tokens = ast.literal_eval(self.config.get('InstagramUserOAuthTokens', 'instagram_access_tokens'))
        # == End Twitter OAuth Authentication ==

        # == Snapbundle Variables ==
        self.snapbundle_username = self.config.get('SnapbundleCredentials', 'snapbundle_username')
        self.snapbundle_password = self.config.get('SnapbundleCredentials', 'snapbundle_password')
        self.snapbundle_user_object = 'paulr'
        # == End Snapbundle Variables ==

        #instagram_handle = 'praddc'

        print "Creating SocialStash Instagram User"
        self.instagram_user = socialstash_instagram.User(access_token=self.instagrame_access_tokens[instagram_handle]['access_token'],
                                                         snapbundle_user_object=self.snapbundle_user_object,
                                                         snapbundle_username=self.snapbundle_username,
                                                         snapbundle_password=self.snapbundle_password,
                                                         username=instagram_handle)
        print "Authenticating to Instagram API"
        self.instagram_user.authenticate()
        self.do_setUserData(self)

    ###################################################################################################################
    def do_setUserData(self, line):
        """ setUserData
            Authenticate and set the user data
        """

        print "Getting my authenticated ID"
        my_id = self.instagram_user.get_id_of_authenticated_user()
        print "My ID: " + str(my_id)

        print "Setting SocialStash user data from API"
        self.instagram_user.set_user_data_from_instagram(my_id)

        print "SocialStash Instagram User Info:"
        print str(self.instagram_user.AsDict())

    ###################################################################################################################
    def do_checkUpdateUser(self, line):
        print "Checking for SocialStash Instagram User in SnapBundle"
        response = self.instagram_user.check_for_user_in_snapbundle()

        if not response:
            print "User not found!  Creating New User"
            print "User URN: " + str(self.instagram_user.create_update_user_in_snapbundle(new_user=True))
        else:
            print "User exists!"
            print "SnapBundle Data: " + str(response)
            print "Updating anyway"
            print "Updated URN: " + str(self.instagram_user.create_update_user_in_snapbundle())

    ###################################################################################################################
    def do_updateMedia(self, line):
        #instagram_user.check_recent_media_exists_in_snapbundle(update_if_found=True)
        #update_user = 'loshea17'
        start_time = time.time()
        update_user_list = ['cgaginis']
        update_user_updates = {}
        total_posts_made = 0
        for update_user in update_user_list:
            updates = self.instagram_user.update_user_feed_in_snapbundle(update_user, update_if_found=False, max_update_count=1000)
            update_user_updates[update_user] = updates
            total_posts_made += updates
            print "Made " + str(updates) + " post updates for user " + str(update_user)

        print "Updates made: " + str(update_user_updates)
        #instagram_user.update_cached_users_media_feed(max_media=60, update_if_found=False)
        end_time = time.time()
        elapsed_time = round(end_time - start_time)
        posts_per_min = total_posts_made / (elapsed_time / 60)
        print "Start Time: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
        print "End Time: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
        print "Running Time: " + str(datetime.timedelta(seconds=elapsed_time))
        print "Posts per minute: " + str(posts_per_min)

    ###################################################################################################################
    def do_updateFollowing(self, line):
        print "checking for users I'm following"
        self.instagram_user.check_relationship_users_exist_in_snapbundle(relationship='FOLLOWING',
                                                                         update_user_profile_if_found=False,
                                                                         update_user_following_if_found=True,
                                                                         update_user_followedby_if_found=True,
                                                                         go_to_max_depth=True)
        print "Saved API Calls: " + str(self.instagram_user.get_global_count_saved_api_calls())
        print "Calls Dictionary: " + str(self.instagram_user.get_global_counts_dict())

    ###################################################################################################################
    def de_updateFollowedBy(self, line):
        self.instagram_user.check_relationship_users_exist_in_snapbundle(relationship='FOLLOWED_BY',
                                                                         update_user_profile_if_found=False,
                                                                         update_user_following_if_found=True,
                                                                         update_user_followedby_if_found=True,
                                                                         go_to_max_depth=True)
        print "Saved API Calls: " + str(self.instagram_user.get_global_count_saved_api_calls())
        print "Calls Dictionary: " + str(self.instagram_user.get_global_counts_dict())

    ###################################################################################################################
    def do_EOF(self, line):
        return True

    ###################################################################################################################
    def do_exit(self, line):
        return True

#---------------------------------------------------------------------------------------------------------------------

#instagram_handle = 'AnEloquentDane'

#print "Get data stored in SnapBundle"
#print str(instagram_user.get_user_data_in_snapbundle())

#################################################################################################################
#instagram_user.print_relationship_node_list(manual_pull_from_snapbundle=True, relationship='FOLLOWING', depth=1)
#instagram_user.print_relationship_node_list(manual_pull_from_snapbundle=True, relationship='FOLLOWED_BY', depth=1)
filename = 'test.gml'
#instagram_user.output_relationship_node_gml(filename=filename, depth=2)
#instagram_user.graph_relationship_gml(filename=filename)


if __name__ == '__main__':
    ui = userdata_instagram()
    ui.cmdloop()