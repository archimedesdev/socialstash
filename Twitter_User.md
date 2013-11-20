# Twitter User Object
The Twitter User Object has its properties read using Tweepy, and then creates a SnapBundle Object, and associates multiple Metadata objects with the main user Object

## Tweepy User Object Fields
Field | Data Type
------------ | -------------
follow_request_sent | Boolean
profile_use_background_image | Boolean
geo_enabled | Boolean
description | String
verified | Boolean
profile_text_color | String
profile_image_url_https | String
profile_sidebar_fill_color | String
id | Long
entities | Entites
followers_count | Integer
protected | Boolean
location | String
default_profile_image | Boolean
withheld_scope | String
id_str | String
status | <tweepy.models.Status object at 0x000000000313A2E8>
utc_offset | Integer
statuses_count | Integer
profile_background_color | String
friends_count | Integer
profile_link_color | String
profile_image_url | String
withheld_in_countries | String
show_all_inline_media | String
profile_background_image_url_https | String
profile_banner_url | String
profile_background_image_url | String
screen_name | String
lang | String
profile_background_tile | Boolean
favourites_count | Integer
name | String
url | String
created_at | datetime.datetime(2010, 4, 19, 13, 49, 56)
contributors_enabled | Boolean
time_zone | String
profile_sidebar_border_color | String
default_profile | Boolean
is_translator | Boolean
listed_count | Integer


## SnapBundle Object Fields
Field | Data Type | Required | Can Update | Serialization Level | Default Value
------------ | ------------- | ------------ | ------------ | ------------ | ------------
uniqueId | long  | true | false | Restricted | Generated
urn | String  | true | false | Minimum | Generated
lastModifiedTimestamp | long   | true | false | Standard | Generated
moniker | String  | false | true | Standard | null
name | String  | true | true | Minimum | 
description | String  | false | true | Standard | 
activeFlag | Boolean  | true | false | Standard  | 
account | IAccount  | true | fase | Full | Generated
objectUrn | String | true | false | Minimum 
objectType | ObjectType | true | true | Minimum | Unknown 

For Twitter users, non-generated fields will be:
Field | Expected Value
------------ | -------------
name | The SnapBundle user account currently logged in
description | <Twitter Handle>'s Twitter Account
activeFlag | True
objectUrn | <SnapBundle_User_Account>:twitter:<twitter_handle>
objectType | 'Person'

## Example SnapBundle Twitter User Object
description': u"praddc's Twitter Account", 
urn': u'urn:uuid:3e36a308-9a6e-4b91-a4c7-75094d2822a2'
objectUrn': u'paulr:twitter:praddc'
name': u'paulr'
activeFlag': True
lastModifiedTimestamp': 1384822856192L
objectType': u'Person'}

## SnapBundle Metadata Fields

Field | Data Type | Required | Can Update | Serialization Level | Default Value
------------ | ------------- | ------------ | ------------ | ------------ | ------------
uniqueId | long  | true | false | Restricted | Generated
urn | String  | true | false | Minimum | Generated
lastModifiedTimestamp | long   | true | false | Standard | Generated
moniker | String  | false | true | Standard | null
account | IAccount  | true | fase | Full | Generated
entityReferenceType | EntityReferenceType | true | false | Minimum |
referenceURN | String | true | false | Minimum |
dataType | MetadataDataType | true | false | Minimum |
key | String | true | false | Minimum |
rawValue | byte[] | true | true | Minimum |

