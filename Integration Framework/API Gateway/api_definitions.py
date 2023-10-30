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
    def __init__(self, tyk_url, keystone_url, keystone_credentials, org_id="1"):
        self.tyk_url = tyk_url
        self.keystone_url = keystone_url
        self.keystone_credentials = keystone_credentials
        self.org_id = org_id
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

    def create_api_definition(self, api_name, target_url):
        api_definition = self.build_api_definition(api_name, target_url)

        try:
            response = requests.post(
                f"{self.tyk_url}/apis", headers=self.headers, json=api_definition)
            response.raise_for_status()
            logger.info(f"API definition created for {api_name}")
            return response.json()
        except HTTPError as e:
            logger.error(
                f"Failed to create API definition for {api_name}: {e}")
            raise

    def build_api_definition(self, api_name, target_url):
        api_definition = {
            "name": api_name,
            "api_id": api_name,
            "org_id": self.org_id,
            "definition": {
                "location": "header",
                "key": "x-api-version"
            },
            "use_keyless": False,
            "auth": {
                "auth_header_name": "Authorization"
            },
            "version_data": {
                "not_versioned": True,
                "versions": {
                    "Default": {
                        "name": "Default",
                        "expires": "3000-01-02 15:04",
                        "use_extended_paths": True,
                        "extended_paths": {
                            "ignored": [],
                            "white_list": [],
                            "black_list": []
                        }
                    }
                }
            },
            "proxy": {
                "listen_path": f"/{api_name}/",
                "target_url": target_url,
                "strip_listen_path": True
            }
        }
        return api_definition


if __name__ == "__main__":
    tyk_url = "https://api.tam-range.com/api"
    keystone_url = "https://keystone.tam-range.com:5000/v3"
    keystone_credentials = {
        "username": "tambakhe",
        "password": "****************",
        "user_domain_name": "keystone.tam-range.com",
        "project_domain_name": "tam-range.com",
        "project_name": "tam-tenant-1"
    }

    tyk_manager = TykAPIManager(tyk_url, keystone_url, keystone_credentials)


    try:
        tyk_manager.create_api_definition(
            "keystone", "https://keystone.tam-range.com")
        tyk_manager.create_api_definition(
            "guacamole", "https://guacamole.tam-range.com")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
