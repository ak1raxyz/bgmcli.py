
import os
import time
import json
import secrets
import logging
import webbrowser
import configparser
import functools
import urllib.parse

import requests

from utils import urldecode

# Prepare config
config = configparser.ConfigParser()
config.read("config.ini")

# Local credential file to store access_token and refresh_token
credentials_file = config["user"]["credentials_file"]

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

def oauth_authorize():
    params = {
        "client_id": config["app"]["id"],
        "response_type": "code",
        "redirect_uri": config["app"]["redirect_uri"],
        "state": secrets.token_hex(12)
    }
    logger.debug("OAuth 2.0 authorize params = %s" % params)
    authorize_uri = config["uri"]["authorize"]
    request_url = '?'.join([authorize_uri, urllib.parse.urlencode(params)])
    results = webbrowser.open(request_url)
    logger.debug("webbrowser.open(%s) -> %s" % (request_url, results))
    try:
        response_url = input("Please copy back the responsed url here: ")
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt triggered, skip.")
        exit()
    query = urldecode(urllib.parse.urlsplit(response_url).query)
    logger.debug("urldecode query = %s" % query)
    return query

def oauth_access_token(query):
    data = {
        "grant_type": "authorization_code",
        "client_id": config["app"]["id"],
        "client_secret": config["app"]["secret"],
        "code": query.get("code"),
        "redirect_uri": config["app"]["redirect_uri"],
        "state": query.get("state")
    }
    logger.debug("OAuth 2.0 access_token data = %s" % data)
    access_token_uri = config["uri"]["access_token"]
    credentials = requests.post(access_token_uri, data=data).json()
    logger.debug("credentials = %s" % credentials)
    current_time = int(time.time())
    expires_at = current_time + int(credentials.get("expires_in"))
    credentials.update({"expires": expires_at})
    logger.info("access_token created, expires at %s" % expires_at)
    with open(credentials_file, 'w') as f:
        f.write(json.dumps(credentials, indent=2))
        logger.info("%s saved" % credentials_file)

def oauth_refresh_token(force=False):
    with open(credentials_file) as f:
        credentials = json.loads(f.read())
    data = {
        "grant_type": "refresh_token",
        "client_id": config["app"]["id"],
        "client_secret": config["app"]["secret"],
        "refresh_token": credentials.get("refresh_token"),
        "redirect_uri": config["app"]["redirect"]
    }
    access_token_uri = config["uri"]["access_token_uri"]
    expires_at = int(credentials.get("expires"))
    current_time = int(time.time())
    if current_time < expires_at:
        if not force:
            logger.info("access_token is not expire, skip refresh_token.")
            return
        else:
            logger.info("access_token is not expire, force refresh_token.")
    else:
        logger.info("access_token expires, continue refresh_token.")
    response = requests.post(access_token_uri, data=data).json()
    current_time = int(time.time())
    expires_at_refreshed = current_time + int(response.get("expires_in"))
    credentials.update(
        {
            "access_token": response.get("access_token"),
            "refresh_token": response.get("refresh_token"),
            "expires": expires_at_refreshed
        }
    )
    with open(credentials_file, 'w') as f:
        f.write(json.dumps(credentials, indent=2))
        logger.info("success refresh_token, %s saved." % credentials_file)

def oauth_token_status():
    with open(credentials_file) as f:
        credentials = json.loads(f.read())
    data = {
        "access_token": credentials.get("access_token")
    }
    token_status_uri = config["uri"]["token_status"]
    token_status = requests.post(token_status_uri, data=data).json()
    logger.info("token_status = %s" % token_status)
    return token_status

def authenticate_required(api_request):
    @functools.wraps
    def authenticate_flow(*args, **kwargs):
        if not os.path.exists(credentials_file):
            query = oauth_authorize()
            oauth_access_token(query)
        else:
            with open(credentials_file) as f:
                credentials = json.loads(f.read())
            expires_at = int(credentials.get("expires"))
            current_time = int(time.time())
            if current_time >= expires_at:
                oauth_refresh_token()
        return api_request(*args, **kwargs)
    return authenticate_flow

if __name__ == "__main__":
    # query = oauth_authorize()
    # oauth_access_token(query)
    # oauth_refresh_token()
    # oauth_token_status()
    pass
