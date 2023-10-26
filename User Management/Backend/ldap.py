from flask_ldap3_login import LDAP3LoginManager

app.config['LDAP_HOST'] = 'your-ldap-server'
app.config['LDAP_BASE_DN'] = 'ou=users,dc=example,dc=com'
app.config['LDAP_USER_LOGIN_ATTR'] = 'uid'

ldap_manager = LDAP3LoginManager(app)
