
import json
import logging
import urllib.parse

import requests

from oauth import login_required

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Collection(object):
    def __init__(self, config):
        self.config = config
        self.base_uri = config["uri"]["base"]
        with open(config["user"]["credentials_file"]) as f:
            self.credentials = json.loads(f.read())
        self.session = requests.Session()
        self.session.headers = {
            "Authorization": "%s %s" % (self.credentials.get("token_type"), self.credentials.get("access_token"))
        }

    @login_required
    def get_subject(self, subject_id):
        '''
        GET /collection/:subject_id

        :params subject_id: required, subject_id from subject url.

        :return: return in raw JSON serialized data.
        '''
        uri = urllib.parse.urljoin(self.base_uri, "/collection/%s" % subject_id)
        response = self.session.get(uri)
        return response

    @login_required
    def update_subject(self, subject_id, status, comment=None, tags=list(), rating=None, privacy=0):
        '''
        POST /collection/:subject_id/:action

        :params subject_id: required, subject_id from subject url.
        :params status: required, can be one of "wish", "collect", "do", "on_hold" or "dropped".
        :params comment: optional, short comment for specific subject.
        :params tags: optional, tag list for specific subject.
        :params rating: optional, rating for specific subject.
        :params privacy: optional, collection privacy, 0 for public where 1 for private.

        :return: return in raw JSON serialized data.
        '''
        uri = urllib.parse.urljoin(self.base_uri, "/collection/%s/update" % subject_id)
        data = {
            "subject_id": subject_id,
            "status": status,
            "comment": comment,
            "tags": " ".join(tags),
            "rating": rating,
            "privacy": privacy
        }
        response = self.session.post(uri, data=data)
        return response
