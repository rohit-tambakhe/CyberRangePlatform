import os
import ldap
from keystoneauth1 import identity
from keystoneauth1 import session
from keystoneclient.v3 import client as keystone_client
from openstack import connection
from pyguacamole import GuacamoleClient, GuacamoleSocket
import logging
from configparser import ConfigParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration from config.ini
config = ConfigParser()
config.read('config.ini')

ldap_url = config.get('LDAP', 'url')
ldap_bind_dn = config.get('LDAP', 'bind_dn')
ldap_base_dn = config.get('LDAP', 'base_dn')

keystone_auth_url = config.get('Keystone', 'auth_url')
keystone_username = config.get('Keystone', 'username')
keystone_project_name = config.get('Keystone', 'project_name')

guacamole_host = config.get('Guacamole', 'host')
guacamole_port = int(config.get('Guacamole', 'port'))
guacamole_protocol = config.get('Guacamole', 'protocol')

new_user = {
    'username': config.get('User', 'username'),
    'password': '',  # Will be retrieved from Barbican
    'email': config.get('User', 'email'),
}

error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)

# Retrieve secrets from environment variables
barbican_secret_id = os.environ.get('BARBICAN_SECRET_ID')
keystone_access_id = os.environ.get('KEYSTONE_ACCESS_ID')


def initialize_ldap_connection():
    try:
        ldap_connection = ldap.initialize(ldap_url)
        ldap_connection.simple_bind_s(ldap_bind_dn, ldap_bind_password)
        return ldap_connection
    except ldap.LDAPError as e:
        error_logger.error("LDAP Error: %s", e)
        raise


def create_guacamole_connection():
    try:
        guacamole_client = GuacamoleClient(
            GuacamoleSocket(guacamole_host, guacamole_port))
        connection = guacamole_client.create_connection(
            protocol=guacamole_protocol)
        return guacamole_client, connection
    except Exception as e:
        error_logger.error("Guacamole Error: %s", e)
        raise


def retrieve_ldap_secret_from_barbican():
    try:
        auth = identity.v3.Password(
            auth_url=keystone_auth_url,
            username=keystone_username,
            password=keystone_password,
            project_name=keystone_project_name,
            user_domain_id='default',
        )

        sess = session.Session(auth=auth)
        conn = connection.Connection(auth_url=keystone_auth_url,
                                     session=sess)

        secret = conn.key_manager.get_secret(barbican_secret_id)
        return secret.payload
    except Exception as e:
        error_logger.error("Error retrieving LDAP secret from Barbican: %s", e)
        raise


def main():
    try:
        ldap_bind_password = retrieve_ldap_secret_from_barbican()
        ldap_connection = initialize_ldap_connection()

        ldif = (
            "dn: uid={},{}".format(new_user['username'], ldap_base_dn),
            "objectClass: top",
            "objectClass: person",
            "objectClass: organizationalPerson",
            "objectClass: inetOrgPerson",
            "cn: {}".format(new_user['username']),
            "sn: {}".format(new_user['username']),
            "uid: {}".format(new_user['username']),
            "userPassword: {}".format(new_user['password']),
            "mail: {}".format(new_user['email']),
        )

        ldap_connection.add_s("uid={},{}".format(
            new_user['username'], ldap_base_dn), ldif)
        logger.info("User %s added to LDAP.", new_user['username'])

        auth = identity.v3.Password(
            auth_url=keystone_auth_url,
            username=keystone_username,
            password=keystone_password,
            project_name=keystone_project_name,
            user_domain_id='default',
        )

        sess = session.Session(auth=auth)
        keystone = keystone_client.Client(session=sess)

        keystone_user = keystone.users.create(
            name=new_user['username'],
            domain='default',
            password=new_user['password'],
            email=new_user['email'],
        )

        keystone_project = keystone.projects.create(
            name=new_user['username'] + '_project',
            domain='default',
        )

        keystone.roles.grant(
            role='Member',
            user=keystone_user,
            project=keystone_project,
        )

        logger.info(
            "User %s created in Keystone and assigned to project.", new_user['username'])

        guacamole_client, guacamole_connection = create_guacamole_connection()
        guacamole_client.connect(guacamole_connection)
        logger.info("Connected to Guacamole. Connection ID: %s",
                    guacamole_connection.connection_id)

    except Exception as e:
        error_logger.error("Application Error: %s", e)


if __name__ == "__main__":
    main()
