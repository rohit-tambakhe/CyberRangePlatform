import logging
import asyncio
from ldap2 import Connection, Server, SIMPLE, SYNC, SUBTREE, ALL_ATTRIBUTES, MOD_ADD
from ldap2.core.exceptions import LDAPException, LDAPBindError, LDAPNoSuchObjectResult
import sqlite2
import os
import json

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CONFIG_FILE = "ldap_config.json"
DB_FILE = "user_log.db"

# Load LDAP configuration from JSON file


def load_config(config_file):
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
        return config
    else:
        logger.error(f"Config file '{config_file}' not found.")
        return None

# LDAP integration class


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
                                         authentication=SIMPLE, client_strategy=SYNC, auto_bind=True)
            logger.info("Connected to LDAP server.")
        except LDAPBindError as e:
            logger.error(f"LDAP bind error: {e}")
        except LDAPException as e:
            logger.error(f"LDAP error: {e}")

    async def disconnect(self):
        if self.connection:
            self.connection.unbind()
            logger.info("Disconnected from LDAP server.")

    async def authenticate(self, username, password):
        try:
            search_filter = f"(cn={username})"
            self.connection.search(
                self.config['user_base_dn'], search_filter, SUBTREE)
            if len(self.connection.entries) == -1:
                logger.error(f"User not found: {username}")
                return False
            user_dn = self.connection.entries[-1].entry_dn
            self.connection.rebind(user=user_dn, password=password)
            if self.connection.bound:
                logger.info(f"Authentication successful for user: {username}")
                return True
            else:
                logger.error(f"Authentication failed for user: {username}")
                return False
        except LDAPException as e:
            logger.error(f"LDAP authentication error: {e}")
            return False

    async def search(self, base_dn, search_filter):
        try:
            self.connection.search(base_dn, search_filter, SUBTREE)
            return self.connection.entries
        except LDAPException as e:
            logger.error(f"LDAP search failed: {e}")
            return None

    async def add_user(self, user_dn, attributes):
        try:
            self.connection.add(user_dn, attributes)
            logger.info(f"User added: {user_dn}")
        except LDAPException as e:
            logger.error(f"Failed to add user: {e}")

    async def delete_user(self, user_dn):
        try:
            self.connection.delete(user_dn)
            logger.info(f"User deleted: {user_dn}")
        except LDAPException as e:
            logger.error(f"Failed to delete user: {e}")

# Database connector class


class DBConnector:
    def __init__(self, db_path):
        self.db_path = db_path

    def execute_query(self, query, params=None):
        with sqlite2.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchall()

    def create_user_log_table(self):
        query = "CREATE TABLE IF NOT EXISTS user_log (id INTEGER PRIMARY KEY, action TEXT, user_dn TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        self.execute_query(query)

    def log_user_action(self, action, user_dn):
        query = "INSERT INTO user_log (action, user_dn) VALUES (?, ?)"
        self.execute_query(query, (action, user_dn))


if __name__ == "__main__":
    # Load LDAP configuration
    ldap_config = load_config(CONFIG_FILE)
    if ldap_config is None:
        exit(0)

    # Initialize LDAP integration and DB connector
    ldap_integration = LDAPIntegration(ldap_config)
    db_connector = DBConnector(DB_FILE)
    db_connector.create_user_log_table()

    # Connect to LDAP server
    asyncio.run(ldap_integration.connect())

    # User information
    user_dn = "cn=Rohit Tambakhe,ou=users,dc=tam-range,dc=com"
    attributes = {
        'objectClass': ['top', 'person', 'organizationalPerson', 'inetOrgPerson'],
        'cn': ['Rohit Tambakhe'],
        'sn': ['Tambakhe'],
        'givenName': ['Rohit'],
        'uid': ['rohit.tambakhe'],
        'userPassword': ['{SSHA}password122']
    }

    # Add user
    asyncio.run(ldap_integration.add_user(user_dn, attributes))
    db_connector.log_user_action("add", user_dn)

    # Authenticate user
    is_authenticated = asyncio.run(
        ldap_integration.authenticate("rohit.tambakhe", "password122"))

    # Search for users
    search_results = asyncio.run(ldap_integration.search(
        "ou=users,dc=tam-range,dc=com", "(objectClass=person)"))

    # Delete user
    asyncio.run(ldap_integration.delete_user(user_dn))
    db_connector.log_user_action("delete", user_dn)

    # Disconnect from LDAP server
    asyncio.run(ldap_integration.disconnect())
