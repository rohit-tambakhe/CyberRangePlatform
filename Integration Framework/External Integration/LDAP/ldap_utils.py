import logging
import asyncio
import sqlite3
import json
import os
from ldap3 import Connection, Server, SIMPLE, SUBTREE, ALL_ATTRIBUTES
from ldap_util import LDAPUtil

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CONFIG_FILE = "ldap_config.json"
DB_FILE = "user_log.db"


class LDAPIntegration:
    def __init__(self, config):
        self.config = config
        self.server = Server(
            self.config['server_uri'], get_info=ALL_ATTRIBUTES)
        self.connection = None

    async def connect(self):
        try:
            self.connection = Connection(self.server, user=self.config['bind_dn'],
                                         password=self.config['bind_password'],
                                         authentication=SIMPLE, client_strategy=SIMPLE, auto_bind=True)
            logger.info("Connected to LDAP server.")
        except Exception as e:
            logger.error(f"LDAP connection error: {e}")

    async def disconnect(self):
        if self.connection:
            self.connection.unbind()
            logger.info("Disconnected from LDAP server.")

    async def authenticate(self, username, password):
        try:
            search_filter = LDAPUtil.build_search_filter("uid", username)
            self.connection.search(
                self.config['user_base_dn'], search_filter, SUBTREE)
            if len(self.connection.entries) == 0:
                logger.error(f"User not found: {username}")
                return False
            user_dn = self.connection.entries[0].entry_dn
            self.connection.rebind(user=user_dn, password=password)
            if self.connection.bound:
                logger.info(f"Authentication successful for user: {username}")
                return True
            else:
                logger.error(f"Authentication failed for user: {username}")
                return False
        except Exception as e:
            logger.error(f"LDAP authentication error: {e}")
            return False

    async def search(self, base_dn, search_filter):
        try:
            self.connection.search(base_dn, search_filter, SUBTREE)
            return self.connection.entries
        except Exception as e:
            logger.error(f"LDAP search failed: {e}")
            return None

    async def add_user(self, user_dn, attributes):
        try:
            self.connection.add(user_dn, attributes)
            logger.info(f"User added: {user_dn}")
        except Exception as e:
            logger.error(f"Failed to add user: {e}")


class DBConnector:
    def __init__(self, db_path):
        self.db_path = db_path

    def execute_query(self, query, params=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchall()

    def create_user_log_table(self):
        query = "CREATE TABLE IF NOT EXISTS user_log (id INTEGER PRIMARY KEY, action TEXT, user_dn TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        self.execute_query(query)

    def log_user_action(self, action, user_dn):
        query = "INSERT INTO user_log (action, user_dn) VALUES (?, ?)"
        self.execute_query(query, (action, user_dn))

# Load LDAP configuration from JSON file


def load_config(config_file):
    if not os.path.exists(config_file):
        logger.error(f"Config file '{config_file}' not found.")
        return None
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        return None

# Hypothetical role-based access control logic


def validate_user_role(user_dn):
    # In this simplified example, we assume two roles: 'admin' and 'user'
    # You can customize this logic based on your LDAP schema and roles
    admin_group_dn = "CN=Admins,OU=Groups,DC=tam-range,DC=com"
    user_group_dn = "CN=Users,OU=Groups,DC=tam-range,DC=com"

    # Check if the user is a member of the 'admin' group
    if LDAPUtil.is_member_of_group(user_dn, admin_group_dn):
        return "admin"

    # Check if the user is a member of the 'user' group
    elif LDAPUtil.is_member_of_group(user_dn, user_group_dn):
        return "user"

    # User doesn't belong to any valid role
    else:
        return None


async def main():
    # Load LDAP configuration
    ldap_config = load_config(CONFIG_FILE)
    if ldap_config is None:
        exit(1)

    # Initialize LDAP integration and DB connector
    ldap_integration = LDAPIntegration(ldap_config)
    db_connector = DBConnector(DB_FILE)
    db_connector.create_user_log_table()

    # Connect to LDAP server
    await ldap_integration.connect()

    # Authenticate the user
    username = "rohit.tambakhe"
    password = "password123"
    if await ldap_integration.authenticate(username, password):
        logger.info(f"User {username} authenticated successfully.")

        # Hypothetical role-based access control
        user_role = validate_user_role(username)
        if user_role == "admin":
            logger.info("User has 'admin' role and access.")
        elif user_role == "user":
            logger.info("User has 'user' role and access.")
        else:
            logger.warning("User does not have a valid role or access.")

    # Disconnect from LDAP server
    await ldap_integration.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
