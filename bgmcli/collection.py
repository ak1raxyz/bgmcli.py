
import json
import logging
import urllib.parse

import requests

from .oauth import login_required

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Collection(object):
    def __init__(self, config):
        self.config = config
        self.base = config["uri"]["base"]

    @login_required
    def get_subject(self, subject_id, credentials=None):
        '''
        GET /collection/:subject_id

        :params subject_id: required, subject_id from subject url.
        :params credentials: optional, automatically passed by login_required decorator.

        :return: return in raw JSON serialized data.
        '''
        uri = urllib.parse.urljoin(self.base, "/collection/%s" % subject_id)
        response = requests.get(uri, headers=credentials)
        return response.json()

    @login_required
    def update_subject(self, subject_id, status, comment=None, tags=list(), rating=None, privacy=0, credentials=None):
        '''
        POST /collection/:subject_id/:action

        :params subject_id: required, subject_id from subject url.
        :params status: required, can be one of "wish", "collect", "do", "on_hold" or "dropped".
        :params comment: optional, short comment for specific subject.
        :params tags: optional, tag list for specific subject.
        :params rating: optional, rating for specific subject.
        :params privacy: optional, collection privacy, 0 for public where 1 for private.
        :params credentials: optional, automatically passed by login_required decorator.

        :return: return in raw JSON serialized data.
        '''
        uri = urllib.parse.urljoin(self.base, "/collection/%s/update" % subject_id)
        data = {
            "subject_id": subject_id,
            "status": status,
            "comment": comment,
            "tags": " ".join(tags),
            "rating": rating,
            "privacy": privacy
        }
        response = requests.post(uri, data=data, headers=credentials)
        return response.json()
