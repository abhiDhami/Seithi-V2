"""
Details :  Seithi OneCMS PageAnalytics Prod- V2
Start time :
Finish Time : 
Last Update :
Version : 1.0
Update :
Last Update by :  Abhishek Dhami
Contributors: Mrunmayi Saoji, Anubhav Sarangi, Yusuf Tan, Abhishek Dhami
"""

import sys
import traceback
import json
from datetime import date
import calendar
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    # TODO implement
    try:
        event_uuid = event.get("uuid", "NA")
        uuid = event_uuid if event_uuid != "" or None else "NA"
        ##### Sitelang is harcoded because API was returning other language values according to the passed query string parameters
        sitelang = "ta"
        return build_payload(
            event["site"], event["platform"], event["path"], sitelang, uuid
        )
    except Exception as exp:
        # raise Exception
        exception_type, exception_value, exception_traceback = sys.exc_info()
        traceback_string = traceback.format_exception(
            exception_type, exception_value, exception_traceback
        )
        err_msg = json.dumps(
            {
                "errorType": exception_type.__name__,
                "errorMessage": str(exception_value),
                "stackTrace": traceback_string,
            }
        )
        logger.error(err_msg)
        return {"message": "Invalid Input"}


def build_payload(propertyvalue, platform, path, sitelanguage, uuid):
    try:
        division = "sg"

        timezone_offset = 8.0  # Singapore Standard Time (UTC 08:00)
        timezone_info = timezone(timedelta(hours=timezone_offset))
        date_now = datetime.now(timezone_info).date()

        try:
            sitelang = "en" if sitelanguage == "" else sitelanguage
        except:
            sitelang = "en"

        try:
            site = propertyvalue
        except:
            return {"message": "Invalid Property"}

        try:
            channel = division + ":" + site + ":" + platform
        except:
            return {"message": "Invalid Site"}

        try:
            if path == "/":
                pagename = channel + ":home"
            else:
                pagename = channel + path.replace("/", ":")
        except:
            return {"message": "Invalid Path"}

        print("Pagename: %s\n" % pagename)

        try:
            pageSection=get_parentcategory(path)
        except:
            pageSection="NA"
        
        try:
            if len(pagename.split(":")) > 3:
                subsection = channel + ":" + pagename.split(":")[3]
            else:
                subsection = "NA"
        except:
            subsection = "NA"

        try:
            if len(pagename.split(":")) > 4:
                subsection2 = subsection + ":" + pagename.split(":")[4]
            else:
                subsection2 = "NA"
        except:
            subsection2 = "NA"
        try:
            if len(pagename.split(":")) > 5:
                subsection3 = subsection2 + ":" + pagename.split(":")[5]
            else:
                subsection3 = "NA"
        except:
            subsection3 = "NA"
        split_path = path.split("/")

        try:
            if path == "/":
                contenttype = "Home Page"
            elif split_path[1] != "NA":
                if split_path[1] == "search":
                    contenttype = "Search Page"
                elif split_path[1] == "404":
                    contenttype = "Error Page"
                else:
                    contenttype = "Section Page"
            else:
                contenttype = "Home Page"

        except:
            contenttype = "NA"
        try:
            hier1 = pagename.replace(":", "%temp%").replace("|", ":").replace("%temp%", "|")
        except:
            hier1 = "NA"
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
            pageurl = get_domain(propertyvalue) + path
        except:
            pageurl = "NA"

        try:
            playeros = get_os(platform)
        except:
            playeros = "NA"

        pagepaylaod={
            "custompagename":pagename,
            "channel": channel,
            "hier1": hier1,
            "server": "seithi " + playeros,
            "division": "sg",
            "site": site,
            "subsection": subsection,
            "subsection2": subsection2,
            "subsection3": subsection3,
            "pagesection": pageSection,
            "sitesection": channel,
            "contenttype": contenttype,
            "hourofday": uuid,
            "uuid": uuid,
            "dayofweek": dayofweek,
            "daytype": daytype,
            "pageurl": pageurl,
            "sitelanguage": sitelang,
            "cpv": "true",
        }
        pagepaylaod=add_prefixTo_payload(pagepaylaod,playeros)       
        comscore = {"c1": "2", "c2": "6154803"}
        lotame = {
            "ClientID": get_lotame_clientid(propertyvalue),
            "seg": [
                "PageName:" + pagename,
                "DeviceType:" + propertyvalue + ":" + platform,
                "Section:" + propertyvalue + ":Section:" + subsection,
                "ContentType:" + propertyvalue + ":" + contenttype,
                "ContentLanguage:" + propertyvalue + ":" + sitelang,
                "DomainName:" + propertyvalue + ":" + get_domain(propertyvalue),
                "DeviceType:" + propertyvalue + ":" + platform,
                "DeviceOS:" + propertyvalue + ":" + playeros,
            ],
        }
        cxense = {"id": get_cxense_siteid(propertyvalue), "pageurl": {"location": pageurl}}
        payload = {
            "omniture": pagepaylaod,
            "comscore": comscore,
            "lotame": lotame,
            "cxense": cxense,
        }
        return payload
    except:
        raise Exception("Error while building payload")



def get_domain(propertyval):
    if propertyval == "berita":
        return "https://www.berita.mediacorp.sg"
    elif propertyval == "seithi":
        return "https://seithi.mediacorp.sg"
    else:
        return "NA"


def get_lotame_clientid(propertyval):
    if propertyval == "berita":
        return "7480"
    elif propertyval == "seithi":
        return "7479"
    else:
        return "NA"


def get_cxense_siteid(propertyval):
    if propertyval == "berita":
        return "1146312927903700934"
    elif propertyval == "seithi":
        return "1146312927903700933"
    else:
        return "NA"


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

def get_parentcategory(path):
    parentcategory = path.split("/")
    parentcategory = parentcategory[1]
    if parentcategory=="":
        parentcategory="Home"
    return parentcategory

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