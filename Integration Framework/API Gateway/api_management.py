import requests
import json
import logging
from requests.exceptions import HTTPError
from keystoneauth1 import session
from keystoneauth1.identity import v3

# Define a logging configuration
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TykAPIManager:
    def __init__(self, tyk_url, keystone_url, keystone_credentials):
        self.tyk_url = tyk_url
        self.keystone_url = keystone_url
        self.keystone_credentials = keystone_credentials
        self.headers = {
            "Authorization": f"Bearer {self.get_keystone_token()}",
            "Content-Type": "application/json"
        }

    def get_keystone_token(self):
        auth = v3.Password(**self.keystone_credentials)
        keystone_session = session.Session(auth=auth)
        token = keystone_session.get_token()
        logger.info("Obtained Keystone token")
        return token

    def list_apis(self):
        try:
            response = requests.get(
                f"{self.tyk_url}/apis", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            logger.error(f"Failed to list APIs: {e}")
            raise

    def get_api(self, api_id):
        try:
            response = requests.get(
                f"{self.tyk_url}/apis/{api_id}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            logger.error(f"Failed to get API '{api_id}': {e}")
            raise

    def delete_api(self, api_id):
        try:
            response = requests.delete(
                f"{self.tyk_url}/apis/{api_id}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            logger.error(f"Failed to delete API '{api_id}': {e}")
            raise


if __name__ == "__main__":
    tyk_url = "https://api.tam-range.com/api"
    keystone_url = "https://keystone.tam-range.com:5000/v3"
    keystone_credentials = {
        "username": "your_username",
        "password": "your_password",
        "user_domain_name": "your_user_domain",
        "project_domain_name": "your_project_domain",
        "project_name": "your_project_name"
    }

    tyk_manager = TykAPIManager(tyk_url, keystone_url, keystone_credentials)
