import json
import logging
import urllib.parse

import requests

from oauth import login_required

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

class User(object):
    def __init__(self, config):
        self.config = config
        self.base = config["uri"]["base"]

    def get_user_info(self, username):
        '''
        :params username: required, can be username or user_id.

        :return: return in raw JSON serialized data.
        '''
        uri = urllib.parse.urljoin(self.base, '/user/%s' % username)
        response = requests.get(uri)
        return response.json()

    def get_user_collection(self, username, category="watching", subject_ids=None, response_group="medium"):
        '''
        GET /user/{username}/collection

        :params username: required, can be username or user_id.
        :params category: optional, can be "watching" or "all_watching",
            "watching" include anime and real while "all_watching" append "books".
        :params subject_ids: optional, list, subject_ids to search.
        :params response_group: optional, can be "medium" or "small".

        :return: return in raw JSON serialized data.
        '''
        uri = urllib.parse.urljoin(self.base, "/user/%s/collection")
        params = {
            "cat": category,
            "responseGroup": response_group
        }
        if subject_ids:
            params.update({"ids": ",".join(subject_ids)})
        response = requests.get(uri, params=params)
        return response.json()

    def get_user_collection_type(self, username, subject_type, max_results=10):
        '''
        GET /user/{username}/collections/{subject_type}

        :params username: required, can be username or user_id.
        :params subject_type: required, can be one of "book", "anime", "music", "game", "real".
        :params max_results: optional, max results to return, max is 25.

        :return: return in raw JSON serialized data.
        '''
        uri = urllib.parse.urljoin(self.base, "/user/%s/collections/%s" % (username, subject_type))
        params = {
            "app_id": self.config["app"]["id"],
            "max_results": max_results
        }
        response = requests.get(uri, params=params)
        return response.json()

    def get_user_collection_status(self, username):
        '''
        GET /user/{username}/collections/status

        :params username: required, can be username or user_id.

        :return: return in raw JSON serialized data.
        '''
        uri = urllib.parse.urljoin(self.base, "/user/%s/collections/status" % username)
        params = {
            "app_id": self.config["app"]["id"]
        }
        response = requests.get(uri, params=params)
        return response.json()

    @login_required
    def get_user_progress(self, username, subject_id=None, credentials=None):
        '''
        GET /user/{username}/progress

        :params username: required, can be username or user_id.
        :params subject_id: optional, specific subject_id to query.
        :params credentials: optional, automatically passed by login_required decorator.

        :return: return in raw JSON serialized data.
        '''
        uri = urllib.parse.urljoin(self.base, "/user/%s/progress" % username)
        params = None
        if subject_id:
            params = {
                "subject_id": subject_id
            }
        response = requests.get(uri, params=params, headers=credentials)
        return response.json()
