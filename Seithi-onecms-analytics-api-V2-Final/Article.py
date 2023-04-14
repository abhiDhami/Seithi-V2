"""
Details : OneCMS Seithi Stage Analytics-V2
Start time :
Finish Time :
Last Update :
Version : 1.0
Update :
Last Update by :  Abhishek Dhami
Contributors: Mrunmayi Saoji, Anubhav Sarangi, Yusuf Tan, Abhishek Dhami
"""
import re
import requests
import sys
import traceback
import json
from datetime import date
import calendar
from datetime import datetime, timezone, timedelta
import logging
import os
import html

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    print("Media ID: %s\n" % event["id"])
    try:
        try:
            resource_name = context.function_name
            return build_payload_seithi(event, resource_name)
        except Exception as exp:
            exception_type, exception_value, exception_traceback = sys.exc_info()
            traceback_string = traceback.format_exception(
                exception_type, exception_value, exception_traceback
            )
            err_msg = json.dumps(
                {
                    "mediaid": event["id"],
                    "errorType": exception_type.__name__,
                    "errorMessage": str(exception_value),
                    "stackTrace": traceback_string,
                }
            )
            logger.error(err_msg)
            return {"message": "Invalid ID"}
    except Exception as exp:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        traceback_string = traceback.format_exception(
            exception_type, exception_value, exception_traceback
        )
        err_msg = json.dumps(
            {
                "mediaid": event["id"],
                "errorType": exception_type.__name__,
                "errorMessage": str(exception_value),
                "stackTrace": traceback_string,
            }
        )
        logger.error(err_msg)
        return {"message": "Invalid Content type"}


def build_payload_seithi(event, resource_name):
    try:
        id = event["id"]
        platform = event["platform"]
        site = event["site"]
        path = event["path"]
        ##### Sitelang is harcoded because API was returning other language values according to the passed query string parameters
        sitelang = "ta"

        user_agent = get_useragent(resource_name, platform)
        headers = {
            "Content-Type": "application/json",
            "cache-control": "no-cache",
            "User-Agent": user_agent,
        }

        endpoint = (
            os.environ["CMS_DATA_API_END_POINT"]
            + "/api/v1/data/"
            + id
            + "?_format=json"
        )
        request_parameters = {}
        r = requests.get(endpoint, data=request_parameters, headers=headers, timeout=2)
        r.encoding = "utf-8"
        one_cms = json.loads(r.text)
        return build_payload(one_cms, id, platform, site, path, sitelang)

    except Exception as exp:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        traceback_string = traceback.format_exception(
            exception_type, exception_value, exception_traceback
        )
        err_msg = json.dumps(
            {
                "mediaid": id,
                "errorType": exception_type.__name__,
                "errorMessage": str(exception_value),
                "stackTrace": traceback_string,
            }
        )
        logger.error(err_msg)
        return {"message": "Network Error"}
        raise Exception


def build_payload(onecms, id, platform, site, path, sitelang):

    email_pattern = "[\w.-]+@[\w.-]+.\w+"
    timezone_offset = 8.0  # Singapore Standard Time (UTC 08:00)
    timezone_info = timezone(timedelta(hours=timezone_offset))
    date_now = datetime.now(timezone_info).date()

    try:
        contentid = str(onecms[0]["nid"])
    except:
        raise Exception("Invalid ID")
    try:
        contentname = html.unescape(onecms[0]["title"])
    except:
        contentname = "NA"
    try:
        contenturl = onecms[0]["url"]
    except:
        contenturl = get_siteurl(site) + path

    try:
        # Added logic for populating lastupdated date in case of Author pages where publishdate is NA
        if "publishdate" not in onecms[0]:
            contentpublishdate = str(onecms[0]["lastupdated"])[:10]
        else:
            contentpublishdate = str(onecms[0]["publishdate"])[:10]
    except:
        contentpublishdate = "NA"

    try:
        ciakeywords = (
            "NA" if onecms[0]["ciakeywords"] == "" or None else onecms[0]["ciakeywords"]
        )
    except:
        ciakeywords = "NA"

    """try:
        ciakeywords = 'NA' if onecms[0]["ciakeywords"] == '' or None else get_ciakeywords(onecms[0]["ciakeywords"])
    except:
        ciakeywords = 'NA"""
    try:
        categories = get_category(onecms[0]["category"])
    except:
        categories = "NA"

    try:
        cmkeywords = get_cmkeywords(onecms, categories)
    except:
        cmkeywords = "NA"

    try:
        sponsorname = (
            "NA"
            if onecms[0]["sponsor"] == [] or "" or None
            else get_sponsorname(onecms[0]["sponsor"])
        )
    except:
        sponsorname = "NA"

    try:
        section_parentcategory = get_parentcategory(path)
    except:
        section_parentcategory = "NA"

    try:
        source = "NA" if onecms[0]["source"] == None or "" else onecms[0]["source"]
    except:
        source = "NA"

    

    try:
        authorinfo = get_authorinfo(onecms, site)
    except:
        authorinfo = "NA"


    try:
        hotnews = get_hotnews(onecms)
    except:
        hotnews = "NA"

    try:
        channel = "sg:" + site + ":" + platform
    except:
        channel = "NA"
    try:
        subsection = section_parentcategory
    except:
        subsection = "NA"
    try:
        try:
            pncontentpublishdate = contentpublishdate.replace("-", "")
        except:
            pncontentpublishdate = "NA"

        pagename = channel + ":" + subsection
        pagename = (
            pagename + ":" + pncontentpublishdate + ":" + contentid + "_" + contentname
        )
    except:
        pagename = "NA"
    
    try:
        photos=build_photos_object(
                onecms,
                platform,
                site,
                contentpublishdate,
            )
        if len(photos) == 0 or (photos==[] or None):
            photos="NA"
    except:
        photos = "NA"
    
    website = site

    try:
        contentvariant = get_doctype(onecms[0]["type"])
    except:
        contentvariant = "NA"

    try:
        eight_hours_from_now = datetime.now() + timedelta(hours=8)
        hourofday = format(eight_hours_from_now, "%H:%M")
        ampm = "PM" if int(hourofday.split(":")[0]) >= 12 else "AM"
        hourofday = hourofday + " " + ampm

    except:
        hourofday = "NA"
    try:
        dayofweek = calendar.day_name[date_now.weekday()]
    except:
        dayofweek = "NA"
    try:
        weekno = date_now.weekday()
        if weekno < 5:
            daytype = "Weekday"
        else:
            daytype = "Weekend"
    except:
        daytype = "NA"
    try:
        if len(path.split("/")) > 3:
            subsection2 = "sg:" + site + ":" + platform + ":"+subsection + ":" + path.split("/")[2]
        else:
            subsection2 = "NA"
    except:
        subsection2 = "NA"
    try:
        if len(path.split("/")) > 4:
            subsection3 = subsection2 + ":" + path.split("/")[3]
        else:
            subsection3 = "NA"
    except: 
        subsection3 = "NA"
   

    try:
        playeros = get_os(platform)
    except:
        playeros = "NA"
    # print ('PLATFORM:',playeros)
    hier1 = "sg|" + site + "|" + platform
    hier1 = hier1 + "|" + subsection
    hier1 = hier1 + "|" + pncontentpublishdate + "|" + contentid + "_" + contentname

    try:
        uuid = str(onecms[0]["uuid"])
    except:
        uuid = "NA"
    pagePayLoad={
        "custompagename":pagename,
        "channel": channel,
        "hier1": hier1,
        "server": "seithi " + playeros,
        "division": "sg",
        "site": website,
        "subsection": "sg:" + site + ":" + platform + ":" + subsection,
        "subsection2": subsection2,
        "subsection3": subsection3,
        "pagesection": subsection,
        "sitesection": channel,
        "contenttype": "Detail Page",
        "hotnews":hotnews,
        "hourofday": uuid,
        "uuid": uuid,
        "dayofweek": dayofweek,
        "daytype": daytype,
        "pageurl": contenturl,
        "sitelanguage": sitelang,
        "cpv": "true",
        "contentid": contentid,
        "contenttitle": contentname,
        "contentpublishdate": contentpublishdate,
        "cmKeywords": cmkeywords,
        "ciaKeywords": ciakeywords,
        "sponsor": sponsorname,
        "contentsource": source,
        "doctype": contentvariant,
        "authorinfo": authorinfo

    }
    #Adding Prefix to the Key
    pagePayLoad = add_prefixTo_payload(pagePayLoad,playeros)
    comscore = {"c1": "2", "c2": "6154803"}
    cxense = {"id": "1146312927903700933", "pageurl.location": contenturl}
    lotame = {
        "ClientID": "7479",
        "seg": [
            "PageName: " + pagename,
            "DeviceType: " + site + ":" + platform,
            "Section: " + site + ":Section:" + subsection,
            "ContentType: " + site + ":" + "Detail Page",
            "ContentLanguage:" + site + ":" + sitelang,
            "DomainName:" + site + ":" + get_domain(site),
            "DeviceType:" + site + ":" + platform,
            "DeviceOS:" + site + ":" + playeros,
        ],
    }
    media={}
    media["page"]={
            "contentid": contentid,
            "contenttitle": contentname,
            "contentpublishdate": contentpublishdate,
            "contentsource": source,
            "custompagename":pagename,
            "channel": channel,
            "pagesection": subsection,
            "hier1": hier1,
            "server": "seithi " + playeros,
            "pageurl": contenturl,
            "pageurlevar": contenturl,
            "contenttype": "Detail Page",
            "doctype": contentvariant,
            "site": website,
            "authorinfo": authorinfo,                        
            "cmKeywords": cmkeywords,
            "ciaKeywords": ciakeywords,
            "sponsor": sponsorname,
            "sitelanguage": sitelang,
        }
    media["page"]=add_prefixTo_payload(media["page"],playeros) 
    media["photos"]=photos
    payload = {
            "omniture": {
                "page":pagePayLoad,
                "media":media
            },
            "comscore": comscore,
            "cxense": cxense,
            "lotame": lotame,
        }
    return payload

######################################################################
def get_thumbnailphoto_object(onecms, platform, site, contentpublishdate):
    photoitem = {}
    try:
        try:
            photoitem["mediatitle"] = (
                site + "_" + html.unescape(onecms[0]["image"]["name"])
            )
        except:
            photoitem["mediatitle"] = photoitem["mediatitle"]
        photoitem["a.media.name"]=photoitem["mediatitle"]
        try:
            photoitem["mediaid"] = onecms[0]["image"]["id"]
        except:
            photoitem["mediaid"] = "NA"
        try:
            photoitem["mediaasseturl"] = onecms[0]["image"]["media_image"]
        except:
            photoitem["mediaasseturl"] = "NA"
        
        photoitem["mediatype"] = "Photo"
        try:
            photoitem["mediacontenttype"] = site + "_Free_Photo_Photo"
        except:
            photoitem["mediacontenttype"] = "NA"
        try:
            photoitem["mediapublishdate"] = contentpublishdate
        except:
            photoitem["mediapublishdate"] = "NA"
        photoitem["mediacategory"] = "Photo"
        try:
            photoitem["mediaplayer"] = site + "_" + platform + "_photoviewer"
        except:
            photoitem["mediaplayer"] = "NA"
        photoitem["a.media.playername"] = photoitem["mediaplayer"]
        photoitem["mediaseriesname"] = "NA"
        photoitem["masrefid"] = "NA"
        photoitem["houseid"] = "NA" #mediareferenceid
        try:
            photoitem["mediainfo"] = (
                site
                + ":"
                + str(photoitem["mediaid"])
                + ":0:F:PH:NA:NA:NA:NA:NA:NA:NA:NA:NA"
            )
        except:
            photoitem["mediainfo"] = "NA"
    except:
        photoitem["mediaid"] = "NA"
    return photoitem


#####################################################################
def build_photos_object(
    onecms, platform, site, contentpublishdate
):
    photosObject = []
    # Get ThumbnailPhotoObject
    thumbnailPhoto_object=get_thumbnailphoto_object(onecms,platform,site,contentpublishdate)
    photosObject.append(thumbnailPhoto_object)

    #Get Hero Photos
    hero_gallery=onecms[0]["hero_gallery"]
    if hero_gallery != None:
        for i in range(len(hero_gallery["media_items"])):
            type = "hero"
            # print(hero_gallery['media_items'])
            photoitem1 = get_photoitem(
                hero_gallery["media_items"][i], platform, site
            )
            photosObject.append(photoitem1)
    else:
        pass
    content=onecms[0]["content"]
    if content != None:
        for i in range(len(content)):
            if content[i]["bundle"] == "gallery":
                for j in content[i]["media_items"]:
                    try:
                        photoitem2 = get_photoitem(
                            j, platform, site
                        )
                    except:
                        photoitem2 = get_photoitem(
                            content[i]["media_items"][j],
                            platform,
                            site
                        )
                    # print ('Photoitem',content[i]['media_items'][j]['name'])
                    photosObject.append(photoitem2)
    else:
        pass

    #Appending Prefix
    playeros=get_os(platform)
    for index in range(len(photosObject)):
        photosObject[index]=add_prefixTo_payload(photosObject[index],playeros)
    return photosObject

##################################################################
def get_photoitem(item, platform, site):
    try:
        photoitem = {}
        try:
            photoitem["mediatitle"] = site + "_" + html.unescape(item["name"])
        except:
            photoitem["mediatitle"] = "NA"
        photoitem["a.media.name"]=photoitem["mediatitle"]
        try:
            photoitem["mediaid"] = item["id"]
        except:
            photoitem["mediaid"] = "NA"
        try:
            photoitem["mediaasseturl"] = item["media_image"]
        except:
            photoitem["mediaasseturl"] = "NA"
        photoitem["mediatype"] = "Photo"
        try:
            photoitem["mediacontenttype"] = site + "_Free_Photo_Photo"
        except:
            photoitem["mediacontenttype"] = "NA"
        try:
            photoitem["mediapublishdate"] = str(item["created"])[:10].replace(
                "/", "-"
            )
        except:
            photoitem["mediapublishdate"] = "NA"
        photoitem["mediacategory"] = "Photo"
        photoitem["mediaseriesname"] = "NA"
        photoitem["masrefid"] = "NA"
        photoitem["houseid"] = "NA" #mediareferenceid
        try:
            photoitem["mediaplayer"] = site + "_" + platform + "_photoviewer"
        except:
            photoitem["mediaplayer"] = "NA"
        photoitem["a.media.playername"] = photoitem["mediaplayer"]
        try:
            photoitem["mediainfo"] = (
                site
                + ":"
                + str(photoitem["mediaid"])
                + ":0:F:PH:NA:NA:NA:NA:NA:NA:NA:NA:NA"
            )
        except:
            photoitem["mediainfo"] = "NA"

    except:
        photoitem = "NA"
    return photoitem



##############################################################
def get_cmkeywords(onecms, categories):
    cmkeywords = []
    if onecms[0]["topics"] == [] or None or "":
        joined_cmkeywords = "NA"
    else:
        for i in range(len(onecms[0]["topics"])):
            keyword = onecms[0]["topics"][i]["english_name"]

            if keyword is None:
                keyword = onecms[0]["topics"][i]["name"]

            cms_keyword = re.sub("  +", " ", keyword)
            cmkeywords.append(cms_keyword)

        joined_cmkeywords = ",".join(cmkeywords)
    if categories != "NA":
        final_cmkeywords = joined_cmkeywords + "," + categories
        return final_cmkeywords
    return joined_cmkeywords


##############################################################
def get_hotnews(onecms):
    for i in range(len(onecms[0]["flags"])):
        if onecms[0]["flags"][i]["name"] == "hotnews":
            hotnews_value = "True"
        else:
            hotnews_value = "False"
    return hotnews_value

############################################################
def get_category(categories):
    section = []
    for i in range(len(categories)):
        category = categories[i].get("english_name", "NA")
        modified_category = re.sub("[^a-zA-Z0-9 ]+", "", category)
        m_category = re.sub("  +", " ", modified_category)
        if i == 0:
            m_category = "cat:" + m_category
        section.append(m_category)
    joined_sections = ",cat:".join(section)
    print("joined_sections", joined_sections)
    return joined_sections


###############################################################
def get_os(platform):
    playeros = {
        "online": "Web",
        "tv_lg": "Web",
        "tv_samsung": "Web",
        "mobileandroidphone": "Android",
        "androidtv": "Android",
        "mobileandroidtablet": "Android",
        "mobileiphone": "iOS",
        "mobileipad": "iOS",
        "onlinechromecast": "Web",
        "mobileandroidphonechromecast": "Android",
        "mobileandroidtabletchromecast": "Android",
        "mobileiphonechromecast": "iOS",
        "mobileipadchromecast": "iOS",
        "mobileiphoneairplay": "iOS",
        "mobileipadairplay": "iOS",
    }
    try:
        playerosvalue = playeros[platform]
    except:
        playerosvalue = "NA"

    return playerosvalue


#########################################################
def get_domain(propertyval):
    if propertyval == "seithi":
        return "https://www.seithi.mediacorp.sg"
    else:
        return "NA"


#########################################################
def get_sponsorname(sponsors):
    sponsor = []
    for vals in sponsors:
        sponsor.append(vals["name"])
    joined_sponsors = ",".join(sponsor)
    return joined_sponsors


########################################################
def get_siteurl(site):
    if site == "seithi":
        siteurl = "https://www.seithi.mediacorp.sg"
    else:
        siteurl = "NA"
    return siteurl


########################################################
def get_doctype(val):
    if val == "Episode":
        val = "Video"
    elif val == "Minute":
        val = "Summary_Article"
    return val


#######################################################
def get_parentcategory(path):
    parentcategory = path.split("/")
    parentcategory = parentcategory[1]
    return parentcategory

######################################################
def get_byline_detail(onecms, byline_id, byline_name):
    """
    Returns the byline details - id, author name of a content. This is applicable
    for 8world (if english_name is not available), CNA, TODAY, 8 Days, Berita, Seithi, Corporate.

            Arguments:
                    onecms (obj | list of dictionaries): onecms response of a content
                    byline_id (list): empty list to contain byline IDs
                    byline_name (list): empty list to contain byline names

            Returns:
                    (tuple): Consists byline_id, byline_name
    """
    for byline in onecms[0]["byline_detail"]:
        # print('Adding ID:' + byline['id'])
        byline_id.append(byline["id"]) if byline["id"] not in byline_id else byline_id
        # print('Adding Name:' + byline['title'])
        byline_name.append(byline["title"]) if byline[
            "title"
        ] not in byline_name else byline_name
    return (byline_id, byline_name)

######################################################
def get_byline_ext(onecms, byline_id, byline_name):
    """
    Returns the byline extended details - id, author (english) name of a content. This is only applicable
    for 8world.

            Arguments:
                    onecms (obj | list of dictionaries): onecms response of a content
                    byline_id (list): empty list to contain byline IDs
                    byline_name (list): empty list to contain byline names

            Returns:
                    (tuple): Consists byline_id, byline_name
    """
    for byline in onecms[0]["byline_ext"]:
        if byline["english_name"]:
            # print('Adding ID:' + byline['id'])
            byline_id.append(byline["id"]) if byline[
                "id"
            ] not in byline_id else byline_id
            # print('Adding Name:' + byline['english_name'])
            byline_name.append(byline["english_name"]) if byline[
                "english_name"
            ] not in byline_name else byline_name
        else:
            # print('Calling byline_detail')
            byline_id, byline_name = get_byline_detail(onecms, byline_id, byline_name)
    return (byline_id, byline_name)

######################################################
def get_authorinfo(onecms, site):
    """
    Returns the authorinfo of a content

            Arguments:
                    onecms (obj | list of dictionaries): onecms response of a content
                    site (str): site name of the property
                        e.g. 8days, etc.

            Returns:
                    authorinfo {str} : author info of a content
                        e.g. 'AuthorFirstname AuthorLastname | <source> | <initials> |
                        BylineID1, BylineID2, BylineID3 |
                        Byline Firstname1 Lastname1, Firstname2 Lastname2, Firstname3 Lastname3 |
                        External_Author Firstname Lastname'
    """
    email_pattern = "[\w.-]+@[\w.-]+.\w+"

    try:
        # contentauthor = 'NA' if onecms[0]["author"] == 'null' or '' else onecms[0]["author"]
        if onecms[0]["author"] == "null" or "":
            author_name = "NA"
        # Check if author contains email, then truncate the domain and extract only the username
        elif re.search(email_pattern, onecms[0]["author"]):
            author_name = onecms[0]["author"].split("@")[0]
        else:
            author_name = onecms[0]["author"]
    except:
        author_name = "NA"

    try:
        source = onecms[0]["source"]["name"] if onecms[0]["source"]["name"] else "NA"
    except:
        source = "NA"

    try:
        initials = onecms[0]["initials"] if onecms[0]["initials"] else "NA"
    except:
        initials = "NA"

    try:
        external_author = (
            onecms[0]["external_author"] if onecms[0]["external_author"] else "NA"
        )
    except:
        external_author = "NA"

    byline_id = []
    byline_name = []
    try:
        if "8world" in site:
            if onecms[0]["byline_ext"]:
                byline_id, byline_name = get_byline_ext(onecms, byline_id, byline_name)
        else:
            byline_id, byline_name = get_byline_detail(onecms, byline_id, byline_name)
        byline_id = ",".join(byline_id) if byline_id else "NA"
        byline_name = ",".join(byline_name) if byline_name else "NA"
    except:
        byline_id = "NA"
        byline_name = "NA"

    try:
        authorinfo = "|".join(
            [author_name, source, initials, byline_id, byline_name, external_author]
        )
    except:
        authorinfo = "NA"

    return authorinfo

######################################################
def get_useragent(resource_name, platform):
    """
    Returns a custom user agent for lambda function

            Arguments:
                    resource_name (str): Lambda function name
                    platform (str): platform of the client

            Returns:
                    (str): custom user agent
    """
    python_ver = sys.version.split(" ")[0]
    user_agent = (
        "AWS Lambda("
        + resource_name
        + "/"
        + "Python "
        + python_ver
        + ") "
        + platform.capitalize()
        + " RT.MEDIACORP"
    )
    return user_agent


def add_prefixTo_payload(payload,playeros):
        if playeros=="Android" or playeros=="iOS":
            prefix="mcs.sdk4."
            newPayload={}
            for key in payload:
                if key.find("a.media")==-1:
                    newPayload[prefix+key]=payload[key]
                else:
                    newPayload[key]=payload[key]
            return newPayload
        else:
            return payload 
        if playeros=="Android" or playeros=="iOS":
            prefix="mcs.sdk4."
            newPayload={}
            for key in payload:
                newPayload[prefix+key]=payload[key]
            return newPayload
        else:
            return payload   