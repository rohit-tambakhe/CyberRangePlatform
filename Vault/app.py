import pulumi
from pulumi_openstack import compute, network, identity
from pulumi_vault import AppRole, Backend, Mount, RoleSecretId

# Create a new Virtual Network
network_config = network.VirtualNetwork(
    "myNetwork",
    cidr_block="10.0.0.0/16",
)

# Create a new Subnet
subnet = network.Subnet(
    "mySubnet",
    virtual_network=network_config.id,
    cidr_block="10.0.1.0/24",
)

# Create a new Security Group
security_group = network.SecurityGroup(
    "mySecurityGroup",
    description="Allow HTTP and SSH traffic",
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "protocol": "tcp",
            "from_port": 80,
            "to_port": 80,
            "cidr_blocks": ["0.0.0.0/0"],
        },
    ],
)

# Create a new Router
router = network.Router(
    "myRouter",
    external_network_id="public",
)

# Associate Subnet with Router
subnet_router_interface = network.RouterInterface(
    "subnetRouterInterface",
    router_id=router.id,
    subnet_id=subnet.id,
)

# Create a new Floating IP
floating_ip = network.FloatingIp(
    "myFloatingIp",
    pool="public",
)

# Associate Floating IP with Instance
floating_ip_association = network.RouterFloatingIpAssociation(
    "floatingIpAssociation",
    floating_ip_id=floating_ip.id,
    router_id=router.id,
)

# Create a Vault AppRole
app_role = AppRole(
    "myAppRole",
    backend=app_role_backend.path,
    token_ttl=3600,
    token_max_ttl=7200,
)

# Use the AppRole authentication method to get the AppRole Secret ID
app_role_secret_id = RoleSecretId(
    "appRoleSecretId",
    role_name=app_role.name,
)

# Create a new VM instance for Vault, using the dynamically generated AppRole Secret ID
vault_instance = compute.Instance(
    "vault-instance",
    flavor_name="m1.small",
    image_name="Ubuntu 20.04",
    security_groups=[security_group.name],
    network_interfaces=[
        {
            "network_id": network_config.id,
            "subnet_id": subnet.id,
            "access_network_security_groups": [security_group.id],
            "floating_ip": floating_ip.address,
        }
    ],
    # Pass the AppRole Secret ID as user data
    user_data=app_role_secret_id.secret_id,
)

# Create an Identity Service (Keystone) for user management
identity_service = identity.Service(
    "keystone",
    type="identity",
    description="OpenStack Identity Service",
)

# Create a new Project (Tenant) for Cyber Range
cyber_range_project = identity.Project(
    "cyberRangeProject",
    description="Cyber Range Project",
    domain="default",
)

# Create a User for the Cyber Range Project
cyber_range_user = identity.User(
    "cyberRangeUser",
    name="cyberrangeuser",
    password="CyberRangePassword",
    default_project=cyber_range_project.id,
)

# Assign the User a Role in the Cyber Range Project
cyber_range_role = identity.Role(
    "cyberRangeRole",
    name="CyberRangeRole",
    project_id=cyber_range_project.id,
)

identity.RoleAssignment(
    "cyberRangeRoleAssignment",
    role_id=cyber_range_role.id,
    user_id=cyber_range_user.id,
    project_id=cyber_range_project.id,
)

