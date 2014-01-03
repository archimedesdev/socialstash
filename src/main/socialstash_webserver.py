__author__ = 'Dev'

import time
import os
import BaseHTTPServer
import snapbundle_instagram_fxns
import snapbundle_helpers
import datetime

HOST_NAME = 'localhost'
PORT_NUMBER = 9000


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    @staticmethod
    def write_instagram_user_info(s, urn):
        s.wfile.write('<TABLE BORDER="3" BORDERCOLOR="00FF00">')
        s.wfile.write('<CAPTION>' + "<b>User Object Info</b></CAPTION>")
        s.wfile.write('<TR VALIGN=TOP><TD>')
        MyHandler.write_instagram_object_info(s, urn)
        s.wfile.write('</TD><TD>')
        MyHandler.write_instagram_metadata_info(s, urn)
        s.wfile.write('</TD></TR></TABLE>')

    @staticmethod
    def write_instagram_object_info(s, urn):
        response = snapbundle_instagram_fxns.check_for_object(urn)
        if response:
            s.wfile.write('<table border="1">')
            s.wfile.write('<CAPTION>' + "<b>Object Info (" + str(len(response)) + ")" + '</b></CAPTION>')
            s.wfile.write('<TR><TH>Key</TH><TH>Value</TH></TR>')
            for current in sorted(response.keys()):
                s.wfile.write("<TR><TD>" + str(current) + "</TD><TD>" + str(response[current]) + "</TD></TR>")
            s.wfile.write('</table><BR>')
        else:
            s.wfile.write('<BR>No Object Info Found <BR>')

    ################## FXN ######################################################################################################
    @staticmethod
    def write_instagram_metadata_info(s, urn):
        response = snapbundle_instagram_fxns.get_object_metadata(urn)
        if response:
            s.wfile.write('<TABLE BORDER="1">')
            s.wfile.write('<CAPTION>' + "<b>Metadata Info (" + str(len(response)) + ")" + '</b></CAPTION>')
            s.wfile.write('<TR><TH>Key</TH><TH>Decoded Value</TH><TH>URN</TH><TH>Associated Files</TH></TR>')
            for current in response:
                decoded_value = snapbundle_helpers.get_raw_value_decoded(current['rawValue'], current['dataType'])
                if current['dataType'] == 'StringType':
                    decoded_value = decoded_value.encode("utf-8")
                else:
                    decoded_value = str(decoded_value)
                s.wfile.write("<TR><TD>" + str(current['key'])
                              + "</TD><TD>" + decoded_value
                              + "</TD><TD>" + str(current['urn'])
                              + "</TD><TD>")
                file_urns = snapbundle_helpers.search_for_file_object('Metadata', current['urn'])
                if file_urns:
                    s.wfile.write('<TABLE BORDER="1">')
                    s.wfile.write('<TR><TH>Urn</TH><TH>File</TH></TR>')
                    for current_key in sorted(file_urns.keys()):
                        time_sec = current_key / 1000
                        time_string = datetime.datetime.fromtimestamp(time_sec).strftime('%Y-%m-%d %H:%M:%S')
                        image_file = snapbundle_helpers.get_file_object_contents(str(file_urns[current_key]), check_cache=True)
                        s.wfile.write("<TR><TD>" + str(file_urns[current_key]) + "<BR>@<BR>" + time_string + "</TD>")
                        s.wfile.write("<TD>" + '<IMG SRC="' + str(image_file) + '">' + "</TD></TR>")
                    s.wfile.write("</TABLE>")
                s.wfile.write("</TD></TR>")
            s.wfile.write('</TABLE><BR>')
        else:
            s.wfile.write('<BR>No Metadata Info Found <BR>')

    ################## FXN ######################################################################################################
    @staticmethod
    def write_instagram_user_relationships(s, urn):
        s.wfile.write('<TABLE BORDER="3" BORDERCOLOR="0000FF">')
        s.wfile.write('<CAPTION>' + "<b>User Relationship Info</b></CAPTION>")
        s.wfile.write('<TR VALIGN=TOP><TD>')
        MyHandler.write_instagram_user_relationships_following(s, urn)
        s.wfile.write('</TD><TD>')
        MyHandler.write_instagram_user_relationships_followedby(s, urn)
        s.wfile.write('</TD></TR></TABLE>')

    ################## FXN ######################################################################################################
    @staticmethod
    def write_instagram_user_relationships_following(s, urn):
        response = snapbundle_instagram_fxns.get_object_relationships(urn, 'FOLLOWING')
        if response:
            s.wfile.write('<TABLE BORDER="1">')
            s.wfile.write('<CAPTION>' + "<b>Following Users (" + str(len(response)) + ")" + '</b></CAPTION>')
            s.wfile.write('<TR><TH>User</TH><TH>URN</TH></TR>')

            for current in sorted(response.keys()):
                s.wfile.write("<TR><TD>" + str(current) + "</TD><TD>" + str(response[current]) + "</TD></TR>")
            s.wfile.write('</TABLE><BR>')
        else:
            s.wfile.write('<BR>No Following Users Info Found <BR>')

    ################## FXN ######################################################################################################
    @staticmethod
    def write_instagram_user_relationships_followedby(s, urn):
        response = snapbundle_instagram_fxns.get_object_relationships(urn, 'FOLLOWED_BY')
        if response:
            s.wfile.write('<TABLE BORDER="1">')
            s.wfile.write('<CAPTION>' + "<b>Followed By Users (" + str(len(response)) + ")" + '</b></CAPTION>')
            s.wfile.write('<TR><TH>User</TH><TH>URN</TH></TR>')
            for current in sorted(response.keys()):
                s.wfile.write("<TR><TD>" + str(current) + "</TD><TD>" + str(response[current]) + "</TD></TR>")
            s.wfile.write('</TABLE><BR>')
        else:
            s.wfile.write('<BR>No Followed By Users Info Found <BR>')

    ################## FXN ###############################################################################es#######################
    @staticmethod
    def write_instagram_object_relationships_likes(s, urn):
        response = snapbundle_instagram_fxns.get_object_relationships(urn, 'Likes', reverse=True)
        if response:
            s.wfile.write('<TABLE BORDER="1">')
            s.wfile.write('<CAPTION>' + "<b>Object Like (" + str(len(response)) + ")" + '</b></CAPTION>')
            s.wfile.write('<TR><TH>User</TH><TH>URN</TH></TR>')

            for current in sorted(response.keys()):
                s.wfile.write("<TR><TD>" + str(current) + "</TD><TD>" + str(response[current]) + "</TD></TR>")
            s.wfile.write('</TABLE><BR>')
        else:
            s.wfile.write('<BR>No Object Likes Found <BR>')

    ################## FXN ###############################################################################es#######################
    @staticmethod
    def write_instagram_object_relationships_references(s, urn, reverse=False):
        response = snapbundle_instagram_fxns.get_object_relationships(urn, 'References', reverse=reverse)
        if response:
            s.wfile.write('<TABLE BORDER="1">')
            s.wfile.write('<CAPTION>' + "<b>Object References (" + str(len(response)) + ")" + '</b></CAPTION>')
            s.wfile.write('<TR><TH>Object</TH><TH>URN</TH><TH>URN</TH></TR>')

            for current in sorted(response.keys()):
                s.wfile.write("<TR><TD>" + str(current) + "</TD><TD>" + str(response[current]) + "</TD></TR>")
            s.wfile.write('</TABLE><BR>')
        else:
            s.wfile.write('<BR>No Object References Found <BR>')

    ################## FXN ###############################################################################es#######################
    @staticmethod
    def write_instagram_object_tags(s, urn):
        response = snapbundle_instagram_fxns.get_tag_list_by_post(urn)
        if response:
            s.wfile.write('<TABLE BORDER="1">')
            s.wfile.write('<CAPTION>' + "<b>Object Tags (" + str(len(response)) + ")" + '</b></CAPTION>')
            s.wfile.write('<TR><TH>Tag</TH><TH>URN</TH></TR>')

            for current in sorted(response.keys()):
                s.wfile.write("<TR><TD>" + str(current) + "</TD><TD>" + str(response[current]) + "</TD></TR>")
            s.wfile.write('</TABLE><BR>')
        else:
            s.wfile.write('<BR>No Object Tags Found <BR>')

    ################## FXN ######################################################################################################
    @staticmethod
    def write_instagram_user_object_interactions(s, urn):
        response = snapbundle_helpers.get_object_interactions(urn)
        if response:
            s.wfile.write('<TABLE BORDER="3" BORDERCOLOR="FF0000">')
            s.wfile.write('<CAPTION>' + "<b>Object Interactions Info (" + str(len(response)) + ")" + '</b></CAPTION>')
            s.wfile.write('<TR><TH>ReferenceURN</TH><TH>URN</TH><TH>Recorded Timestamp</TH><TH>Associated Object</TH><TH>Object Metadata</TH></TR>')
            for current in response:
                time_sec = current['recordedTimestamp']
                time_string = datetime.datetime.fromtimestamp(time_sec).strftime('%Y-%m-%d %H:%M:%S')
                s.wfile.write("<TR VALIGN=TOP><TD>" + str(current['referenceURN'])
                              + "</TD><TD>" + str(current['urn'])
                              + "</TD><TD>" + str(time_string)
                              + "</TD><TD>")

                MyHandler.write_instagram_object_info(s, current['referenceURN'])
                s.wfile.write("<BR>")
                MyHandler.write_instagram_object_relationships_likes(s, current['referenceURN'])
                s.wfile.write("<BR>")
                MyHandler.write_instagram_object_relationships_references(s, current['referenceURN'], reverse=True)
                s.wfile.write("<BR>")
                MyHandler.write_instagram_object_relationships_references(s, current['referenceURN'], reverse=False)
                s.wfile.write("<BR>")
                MyHandler.write_instagram_object_tags(s, current['referenceURN'])

                s.wfile.write("</TD>")
                s.wfile.write("<TD>")
                MyHandler.write_instagram_metadata_info(s, current['referenceURN'])
                s.wfile.write("</TD>")
                s.wfile.write("</TR>")

            s.wfile.write('</TABLE><BR>')
        else:
            s.wfile.write('<BR>No Object Interactions Info Found <BR>')

    ########################################################################################################################
    ########################################################################################################################
    ############# FXN ######################################################################################################
    @staticmethod
    def index_write_all_users(s):
        response = snapbundle_helpers.check_for_objects_options(snapbundle_instagram_fxns.snapbundle_base_urn_instagram_user,objectUrnLike=True)
        if response:
            s.wfile.write('<TABLE BORDER="3">')
            s.wfile.write('<CAPTION>' + "<b>Instagram User Object Info (" + str(len(response)) + ")" + '</b></CAPTION>')
            s.wfile.write('<TR><TH>objectType</TH><TH>objectUrn</TH><TH>Name</TH><TH>urn</TH></TR>')
            for current in response:
                s.wfile.write("<TR><TD>" + str(current['objectType'])
                              + '</TD><TD><a href="/instagram/' + str(current['objectUrn']) + '">' + str(current['objectUrn']) + '</a>'
                              + '</TD><TD>' + str(current['name'])
                              + "</TD><TD>" + str(current['urn'])
                              + "</TD></TR>")
            s.wfile.write('</TABLE><BR>')
        else:
            s.wfile.write('<BR>No Object Info Found <BR>')

    ################## FXN ######################################################################################################
    @staticmethod
    def index_write_all_posts(s):
        response = snapbundle_helpers.check_for_objects_options(snapbundle_instagram_fxns.snapbundle_base_urn_instagram_post, objectUrnLike=True)
        if response:
            s.wfile.write('<TABLE BORDER="3">')
            s.wfile.write('<CAPTION>' + "<b>Instagram Post Object Info (" + str(len(response)) + ")" + '</b></CAPTION>')
            s.wfile.write('<TR><TH>objectType</TH><TH>objectUrn</TH><TH>Name</TH><TH>urn</TH></TR>')
            for current in response:
                s.wfile.write("<TR><TD>" + str(current['objectType'])
                              + '</TD><TD><a href="/instagram/' + str(current['objectUrn']) + '">' + str(current['objectUrn']) + '</a>'
                              + '</TD><TD>' + str(current['name'])
                              + "</TD><TD>" + str(current['urn'])
                              + "</TD></TR>")
            s.wfile.write('</TABLE><BR>')
        else:
            s.wfile.write('<BR>No Object Info Found <BR>')

    ################## FXN ######################################################################################################
    @staticmethod
    def index_write_all_comments(s):
        response = snapbundle_helpers.check_for_objects_options(snapbundle_instagram_fxns.snapbundle_base_urn_instagram_comment, objectUrnLike=True)
        if response:
            s.wfile.write('<TABLE BORDER="3">')
            s.wfile.write('<CAPTION>' + "<b>Instagram Comment Object Info (" + str(len(response)) + ")" + '</b></CAPTION>')
            s.wfile.write('<TR><TH>objectType</TH><TH>objectUrn</TH><TH>Name</TH><TH>urn</TH></TR>')
            for current in response:
                s.wfile.write("<TR><TD>" + str(current['objectType'])
                              + '</TD><TD><a href="/instagram/' + str(current['objectUrn']) + '">' + str(current['objectUrn']) + '</a>'
                              + '</TD><TD>' + str(current['name'])
                              + "</TD><TD>" + str(current['urn'])
                              + "</TD></TR>")
            s.wfile.write('</TABLE><BR>')
        else:
            s.wfile.write('<BR>No Object Info Found <BR>')

    ################## FXN ######################################################################################################
    @staticmethod
    def index_write_all_locations(s):
        response = snapbundle_helpers.check_geospacial_by_name(snapbundle_instagram_fxns.snapbundle_base_instagram_location_name)
        if response:
            s.wfile.write('<TABLE BORDER="3">')
            s.wfile.write('<CAPTION>' + "<b>Instagram Geospatial Info (" + str(len(response)) + ")" + '</b></CAPTION>')
            s.wfile.write('<TR><TH>georectificationType</TH><TH>name</TH><TH>description</TH><TH>urn</TH></TR>')
            for current in response:
                s.wfile.write("<TR><TD>" + str(current['georectificationType'])
                              + '</TD><TD>' + str(current['name'])
                              + '</TD><TD>' + str(current['description'])
                              + "</TD><TD>" + str(current['urn'])
                              + "</TD></TR>")
            s.wfile.write('</TABLE><BR>')
        else:
            s.wfile.write('<BR>No Object Info Found <BR>')

    ###################################################################################################################
    ###################################################################################################################
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

    def do_GET(s):
        """Respond to a GET request."""

        path_list = s.path
        path_list = path_list.split('/')
        # First we check to see if it's an image we need to serve up
        if s.path.endswith(".jpg"):
            path_list = path_list[2:]
            path_to_use = ''
            for current in path_list:
                path_to_use += current
                path_to_use += os.sep
            path_to_use = path_to_use[:-1]
            f = open(path_to_use, 'rb')
            s.send_response(200)
            s.send_header('Content-type',        'image/jpg')
            s.end_headers()
            s.wfile.write(f.read())
            f.close()
            return

        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write("<html><head><title>Social Stash Test Web Server.</title></head>")
        s.wfile.write("<body>")
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".

        application = path_list[1]
        if application == 'instagram':
            try:
                urn = path_list[2]
                s.wfile.write("<b><CENTER>Object urn: %s</CENTER></b><br>" % urn)
                MyHandler.write_instagram_user_info(s, urn)
                MyHandler.write_instagram_user_relationships(s, urn)
                MyHandler.write_instagram_user_object_interactions(s, urn)
                MyHandler.write_instagram_object_relationships_references(s, urn, reverse=False)
            except IndexError:
                MyHandler.index_write_all_users(s)
                MyHandler.index_write_all_posts(s)
                MyHandler.index_write_all_comments(s)
                MyHandler.index_write_all_locations(s)
        s.wfile.write("</body></html>")

    ###################################################################################################################
    ###################################################################################################################

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)