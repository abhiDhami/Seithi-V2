"""
OneCMS Seithi Media Analytics Prod 
Start time : 
Finish Time :
Last Update :
Version : 1.0
Update :
Last Update by :  Abhishek Dhami
Contributors: Mrunmayi Saoji, Anubhav Sarangi, Yusuf Tan, Abhishek Dhami
"""
import requests
import sys
import traceback
import json
from datetime import date

# import calendar
from datetime import datetime, timezone, timedelta
import logging
import os
import html

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    print("Media ID: %s\n" % event["id"])
    try:
        resource_name = context.function_name
        ##### Sitelang is harcoded because API was returning other language values according to the passed query string parameters
        sitelang = "ta"
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


def build_payload_seithi(event, resource_name):
    try:
        id = event["id"]
        platform = event["platform"]
        site = event["site"]
        path = event["path"]
        ##### Sitelang is harcoded because API was returning other language values according to the passed query string parameters
        RADIO_STATIONS = {"171626":"Oli 968"}
        user_agent = get_useragent(resource_name, platform)
        headers = {
            "Content-Type": "application/json",
            "cache-control": "no-cache",
            "User-Agent": user_agent,
        }
        endpoint = (
            os.environ["CMS_DATA_API_END_POINT"]
            + "/api/v1/media/"
            + id
            + "?_format=json"
        )
        request_parameters = {}
        try:
            playeros = get_os(platform)
        except:
            playeros = "NA"

        if id in RADIO_STATIONS.keys():
            return get_radioobject(id, site, platform, playeros,RADIO_STATIONS)
        else:
            r = requests.get(
                endpoint, data=request_parameters, headers=headers, timeout=2
            )
            r.encoding = "utf-8"
            one_cms = json.loads(r.text)
            return build_payload(one_cms, id, platform, playeros, site, path)

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


################################################################
def build_payload(onecms, id, platform, playeros, site, path):

    try:
        if onecms[0]["bundle"][0]["target_id"] == "video":
            return get_videoobject(onecms, playeros, site, path, platform)
        elif onecms[0]["bundle"][0]["target_id"] == "audio":
            return get_podcastobject(onecms, playeros, site, platform)
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
        return {"message": "Invalid ID"}


################################################################
def get_videoobject(onecms, playeros, site, path, platform):
    try:
        mediaid = onecms[0]["mid"][0]["value"]
    except:
        raise Exception("Invalid ID")
    try:
        mediaduration = str(round(float(onecms[0]["field_duration"][0]["value"])))
    except:
        mediaduration = "0"
    try:
        mediapublishdate = str(onecms[0]["created"][0]["value"])[:10]
    except:
        mediapublishdate = "NA"
    try:
        mediatype = "Video"
    except:
        mediatype = "NA"

    mediaseriesname = "NA"
    try:
        mediatitle = site + "_" + html.unescape(onecms[0]["name"][0]["value"])
    except:
        mediatitle = "NA"
    try:
        masrefid = (
            "NA"
            if onecms[0]["field_master_reference_key"][0]["value"] == None
            else onecms[0]["field_master_reference_key"][0]["value"]
        )
    except:
        masrefid = "NA"
    try:
        mediareferenceid = (
            "NA"
            if onecms[0]["field_video_house_id"][0]["value"] == None
            else onecms[0]["field_video_house_id"][0]["value"]
        )
    except:
        mediareferenceid = "NA"
    try:
        videotype, mediacategory = get_videotype(mediaduration)
    except:
        videotype = "NA"
        mediacategory = "NA"
    try:
        mediacontenttype = site + "_Free_" + mediacategory + "_Video"
    except:
        mediacontenttype = "NA"
    try:
        mediaplayer = site + "_" + platform + "_brightcoveplayer"
    except:
        mediaplayer = "NA"
    try:
        mediainfo = (
            site
            + ":"
            + str(mediaid)
            + ":"
            + str(mediaduration)
            + ":"
            + "F:"
            + videotype
            + ":NA:NA:NA:NA:NA:NA:NA:NA:NA"
        )
    except:
        mediainfo = "NA"
    try:
        mediaurl = onecms[0]["field_video_url_mp4"][0]["value"]
    except:
        mediaurl = "NA"
    try:
        mediaclassification = (
            "NA"
            if mediaduration == None or ""
            else get_mediaclassification(mediaduration)
        )
    except:
        mediaclassification = "NA"
    mediachannel = "vasantham"
    seriesid = "NA"
    payload={
        "mediaid": str(mediaid),
        "mediaduration": mediaduration,
        "mediapublishdate": mediapublishdate,
        "mediatype": mediatype,
        "mediacontenttype": mediacontenttype,
        "mediacategory": mediacategory,
        "mediaseriesname": mediaseriesname,
        "mediatitle": mediatitle,
        "a.media.name":mediatitle,
        "a.media.view": "true",
        "masrefid": masrefid,
        "houseid": mediareferenceid, #mediareferenceid
        "videotype": videotype,
        "mediaplayer": mediaplayer,
        "a.media.playername":mediaplayer,
        "mediainfo": mediainfo,
        "videourl": mediaurl,
        "mediaasseturl": mediaurl, #mediaurl
        "mediaclassification": mediaclassification,
        "mediachannel": mediachannel,
        "seriesid": seriesid,   
    }
    gfk = build_gfkobject(onecms, payload, path, site, platform)
    payload=add_prefixTo_payload(payload,playeros)
    
    video_payload = {
        "omniture": payload,
        "gfk":gfk
        
    }
    return video_payload


##############################################################
def get_podcastobject(onecms, playeros, site, platform):
    try:
        mediaid = onecms[0]["mid"][0]["value"]
    except:
        mediaid = "NA"
    try:
        mediaurl = onecms[0]["field_audio_url"][0]["value"]
    except:
        mediaurl = "NA"
    try:
        mediatitle = site + "_" + html.unescape(onecms[0]["name"][0]["value"])
    except:
        mediatitle = "NA"

    mediatype = "Podcast"
    try:
        mediacontenttype = site + "_Free_Podcast_Podcast"
    except:
        mediacontenttype = "NA"
    try:
        mediaplayer = site + "_" + platform + "podcastplayer"
    except:
        mediaplayer = "NA"
    try:
        mediaduration = str(
            round(float(onecms[0]["field_durationseconds"][0]["value"]))
        )
    except:
        mediaduration = "NA"
    try:
        mediapublishdate = str(onecms[0]["created"][0]["value"][:10])
    except:
        mediapublishdate = "NA"
    mediaseriesname = "NA"
    mediatype = "Podcast"
    mediareferenceid = "NA"
    masrefid = "NA"
    try:
        audiotype = get_audiotype(mediaduration)
    except:
        audiotype = "NA"
    mediatype = "Podcast"
    try:
        mediainfo = (
            site
            + ":"
            + str(mediaid)
            + ":"
            + str(mediaduration)
            + ":F:"
            + audiotype
            + ":NA:NA:NA:NA:NA:NA:NA:NA:NA"
        )
    except:
        mediainfo = "NA"
    try:
        mediaplayer = site + "_" + platform + "_podcastplayer"
    except:
        mediaplayer = "NA"
    mediacategory = "Podcast"
    try:
        mediaclassification = (
            "NA"
            if mediaduration == None or ""
            else get_mediaclassification(mediaduration)
        )
    except:
        mediaclassification = "NA"
    mediachannel = "vasantham_podcast"
    payload={
        "mediaid": str(mediaid),
        "mediaduration": mediaduration,
        "mediapublishdate": mediapublishdate,
        "mediatype": mediatype,
        "mediacontenttype": mediacontenttype,
        "mediacategory": mediacategory,
        "mediaseriesname": mediaseriesname,
        "mediatitle": mediatitle,
        "a.media.name":mediatitle,
        "a.media.view": "true",   #Need to update Processing Rule for attributing event56
        "masrefid": masrefid,
        "houseid": mediareferenceid, #mediareferenceid
        "audiotype": audiotype,  #Need to add in the processing Rule
        "mediaplayer": mediaplayer,
        "a.media.playername":mediaplayer,
        "mediainfo": mediainfo,
        "videourl": mediaurl,
        "mediaasseturl": mediaurl, #mediaurl
        "mediaclassification": mediaclassification,
        "mediachannel": mediachannel,
    }
    payload=add_prefixTo_payload(payload,playeros) 
    podcast_payload = {
        "omniture": payload,
    }
    return podcast_payload


##############################################################
def get_radioobject(mediaid, site, platform, playeros,RADIO_STATIONS):
    """
    Returns the Live Radio metadata.
    """
    mediaduration = 0
    mediatype = "Radio"
    audiotype = "RD"
    radioname=RADIO_STATIONS[mediaid]
    try:
        mediaseriesname = site + "_"+radioname
    except:
        mediaseriesname = "NA"

    try:
        mediatitle = site + "_"+radioname
    except:
        mediatitle = "NA"

    try:
        mediaplayer = site + "_" + platform + "_radioplayer"
    except:
        mediaplayer = "NA"

    try:
        mediainfo = (
            site
            + ":"
            + str(mediaid)
            + ":"
            + str(mediaduration)
            + ":F:"
            + audiotype
            + ":NA:NA:NA:NA:NA:NA:NA:NA:NA"
        )
    except:
        mediainfo = "NA"
    payload={
        "mediaid": mediaid,
        "mediaduration": mediaduration,
        "mediapublishdate": "NA",
        "mediatype": mediatype,
        "mediacontenttype": site + "_Free_Live_" + mediatype,
        "mediaseriesname": mediaseriesname,
        "mediatitle": mediatitle,
        "a.media.name":mediatitle,
        "a.media.view": "true",
        "masrefid": "NA",
        "houseid": "NA",  #mediareferenceid
        "audiotype": audiotype,
        "mediaplayer": mediaplayer,
        "a.media.playername":mediaplayer,
        "mediainfo": mediainfo,
        "videourl": "NA", #Remove once mediaasseturl available in processing rules
        "mediaasseturl": "NA",  #mediaurl
    }
    payload=add_prefixTo_payload(payload,playeros)
  
    payload = {
        "omniture": payload,
    }
    return payload

##############################################################
def get_videotype(duration):
    if duration == "0":
        type = "LN"
        category = "Live"
    else:
        type = "CP"
        category = "Video"
    return type, category


###############################################################
def get_audiotype(duration):
    if duration == "0":
        type = "Live"
    else:
        type = "Podcast"
    return type


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


#####################################################
def get_mediaclassification(mediaduration):
    try:
        if int(mediaduration) == 0:
            mediaclassification = "Live"
        elif int(mediaduration) >= 900:
            mediaclassification = "Long"
        elif int(mediaduration) > 200 and int(mediaduration) < 900:
            mediaclassification = "Medium"
        else:
            mediaclassification = "Short"
    except:
        mediaclassification = "NA"
    return mediaclassification


################################################################
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


#########################################################
def get_mediatype(type):
    """
    Returns the name, language of mediacorp properties

            Parameters:
                    site (str): site name
                                e.g. 8days, today, etc.

            Returns:
                    sitedetail (obj | nested dict): Site details object containing site name and language
    """

    mediatype = {
        "Movie": "339",
        "Episode": "340",
        "Linear": "341",
        "Sports": "342",
        "News": "385",
        "Extra": "386",
        "Education": "387",
        "Clip": "388",
    }
    try:
        return mediatype[type]
    except:
        return "null"


#########################################################
def get_sitedetail(site):
    """
    Returns the name, language of mediacorp properties

            Parameters:
                    site (str): site name
                                e.g. 8days, today, etc.

            Returns:
                    sitedetail (obj | nested dict): Site details object containing site name and language
    """

    sitedetail = {
        "cna": {"name": "CNA", "lang": "en", "tv_channel": "CNA"},
        "cnalifestyle": {"name": "CNA Lifestyle", "lang": "en", "tv_channel": "CNA"},
        "cnaluxury": {"name": "CNA Luxury", "lang": "en", "tv_channel": "CNA"},
        "8world": {"name": "8world", "lang": "zh", "tv_channel": "Channel 8"},
        "8worldentlife": {
            "name": "8world Entlife",
            "lang": "zh",
            "tv_channel": "Channel 8",
        },
        "today": {"name": "TODAY", "lang": "en", "tv_channel": "null"},
        "8days": {"name": "8 DAYS", "lang": "en", "tv_channel": "null"},
        "seithi": {"name": "SEITHI", "lang": "ta", "tv_channel": "Vasantham"},
        "berita": {"name": "BERITA", "lang": "ms", "tv_channel": "Suria"},
        "corporate": {
            "name": "Mediacorp Corporate",
            "lang": "en",
            "tv_channel": "null",
        },
    }
    try:
        return sitedetail[site]
    except:
        return "null"


#########################################################
def get_gfkmediaid(site, platform):
    """
    Returns the Gfk relevant platform for various support platforms on mediacorp sites/properties

            Arguments:
                    platform (str): platform of the client
            Returns:
                    (str): Gfk platform
    """
    gfkplatform = {
        "online": get_sitedetail(site)["name"] + " Web",
        "appletv": get_sitedetail(site)["name"] + " iOS",
        "mobileandroidphone": get_sitedetail(site)["name"] + " Android",
        "androidtv": get_sitedetail(site)["name"] + " AndroidTV",
        "mobileandroidtablet": get_sitedetail(site)["name"] + " Android",
        "mobileiphone": get_sitedetail(site)["name"] + " iOS",
        "mobileipad": get_sitedetail(site)["name"] + " iOS",
        "onlinechromecast": get_sitedetail(site)["name"] + " Web",
        "mobileandroidphonechromecast": get_sitedetail(site)["name"] + " Android",
        "mobileandroidtabletchromecast": get_sitedetail(site)["name"] + " Android",
        "mobileiphonechromecast": get_sitedetail(site)["name"] + " iOS",
        "mobileipadchromecast": get_sitedetail(site)["name"] + " iOS",
        "mobileiphoneairplay": get_sitedetail(site)["name"] + " iOS",
        "mobileipadairplay": get_sitedetail(site)["name"] + " iOS",
    }
    try:
        return gfkplatform[platform]
    except:
        return "null"


################################################################
def build_gfkobject(one_cms, video, path, site, platform):
    """
    Returns Gfk payload for a video landing page content

            Arguments:
                    onecms (obj | list of dictionaries): onecms response of a content
                    videos (obj | list of dictionaries): videos metadata of a content
                    site (str): site name of the property
                    platform (str): platform of the client

            Returns:
                    (obj) | llist of dictionaries: gfk payload
    """
    gfkmedia = {}

    try:
        mediaduration = video["mediaduration"]
    except:
        mediaduration = "NA"

    # Media Type ID
    try:
        if mediaduration == "NA":
            # Linear
            mediatype = "Linear"
        elif one_cms[0]["field_programme"]:
            # Episode
            mediatype = "Episode"
        else:
            mediatype = "News"
        contentid = get_mediatype(mediatype)
    except:
        mediatype = "NA"
        contentid = "null"

    # Media ID
    try:
        mediaid = get_gfkmediaid(site, platform)
    except:
        mediaid = "null"

    try:
        islive = "true" if str(contentid) == "341" else "false"
    except:
        islive = "false"

    # Video Type
    try:
        if islive == "true":
            cp1 = "3"
        else:
            cp1 = "1"
    except:
        cp1 = "1"

    # Video ID
    try:
        cp2 = str(video["mediaid"])
    except:
        cp2 = "null"

    # Video Title
    try:
        cp3 = video["mediatitle"]
    except:
        cp3 = "null"

    # Video Duration
    try:
        cp4 = "null" if mediaduration == "NA" else mediaduration
    except:
        cp4 = "null"

    # Advertisement-ID
    cp5 = "null"

    # Episode ID
    try:
        cp6 = cp2 if contentid == "340" else "null"
    except:
        cp6 = "null"

    # Episode Title
    try:
        cp7 = cp3 if contentid == "340" else "null"
    except:
        cp7 = "null"

    # Episode Duration
    try:
        cp8 = mediaduration if contentid == "340" else "null"
    except:
        cp8 = "null"

    # Airtime
    cp9 = "null"

    # Web Status
    try:
        cp10 = (
            "1"
            if contentid == "388" or contentid == "386" or contentid == "339"
            else "null"
        )
    except:
        cp10 = "null"

    # Pay Status
    cp11 = "0"

    # Video URL
    try:
        cp12 = get_domain(site) + path
    except:
        cp12 = "null"

    # Language
    try:
        cp13 = get_sitedetail(site)["lang"]
    except:
        cp13 = "null"

    # Program Name
    try:
        if one_cms[0]["field_programme"]:
            cp14 = one_cms[0]["field_programme"]["name"]
        else:
            cp14 = "null"
    except:
        cp14 = "null"

    # TV Channel
    try:
        cp15 = get_sitedetail(site)["tv_channel"]
    except:
        cp15 = "null"

    # Program ID
    try:
        if one_cms[0]["field_programme"]:
            cp16 = one_cms[0]["field_programme"]["id"]
        else:
            cp16 = "null"
    except:
        cp16 = "null"

    # Master Reference Key ID
    try:
        cp18 = "null" if video["masrefid"] in ["", "NA"] else video["masrefid"]
    except:
        cp18 = "null"

    try:
        gfkmedia = {
            "contentId": mediatype,
            "mediaId": mediaid,
            "cp": {
                "cp1": cp1,
                "cp2": cp2,
                "cp3": cp3,
                "cp4": cp4,
                "cp5": cp5,
                "cp6": cp6,
                "cp7": cp7,
                "cp8": cp8,
                "cp9": cp9,
                "cp10": cp10,
                "cp11": cp11,
                "cp12": cp12,
                "cp13": cp13,
                "cp14": cp14,
                "cp15": cp15,
                "cp16": cp16,
                "cp18": cp18,
            },
        }
    except:
        gfkmedia = {}
    return gfkmedia

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