import pulumi
import pulumi_openstack as openstack
import pulumi_kubernetes as k8s
import pulumi_random as random
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts
from pulumi_kubernetes.core.v1 import Namespace
import yaml
import argparse  # Import argparse for command-line argument parsing

# Read OpenStack authentication information from environment variables
os_username = pulumi.get_env("OS_USERNAME")
os_password = pulumi.secret(pulumi.get_env("OS_PASSWORD"))
os_auth_url = pulumi.get_env("OS_AUTH_URL")
os_project_name = pulumi.get_env("OS_PROJECT_NAME")
os_user_domain_name = pulumi.get_env("OS_USER_DOMAIN_NAME")
os_project_domain_name = pulumi.get_env("OS_PROJECT_DOMAIN_NAME")

# Create an argument parser
parser = argparse.ArgumentParser(
    description="Deploy EFK Stack with custom configuration.")
parser.add_argument(
    "config_file",
    type=str,
    help="Path to the custom configuration file (e.g., efk-stack-config-1.yaml)",
)

# Parse the command-line arguments
args = parser.parse_args()

# Load the selected configuration from the custom file
selected_config_file = args.config_file
with open(selected_config_file, "r") as config_file:
    selected_config = yaml.safe_load(config_file)

# Create an OpenStack provider
provider = openstack.Provider(
    "openstack-provider",
    identity_endpoint=os_auth_url,
    user_name=os_username,
    password=os_password,
    tenant_name=os_project_name,
    domain_name=os_user_domain_name,
    project_domain_name=os_project_domain_name,
)

# Create a random password for Elasticsearch
elasticsearch_password = random.RandomPassword(
    "elasticsearch-password",
    length=16,
    special=True,
)

# Create a network, subnet, and security group for the EFK stack
network = openstack.networking.Network(
    "efk-network",
    provider=provider,
)

subnet = openstack.networking.Subnet(
    "efk-subnet",
    provider=provider,
    network_id=network.id,
    cidr="10.0.0.0/24",
)

security_group = openstack.networking.SecGroup(
    "efk-security-group",
    provider=provider,
    description="Allow EFK traffic",
    rule=[
        {
            "from_port": 9200,
            "to_port": 9200,
            "protocol": "tcp",
            "cidr": "0.0.0.0/0",
        },
        {
            "from_port": 24224,
            "to_port": 24224,
            "protocol": "tcp",
            "cidr": "0.0.0.0/0",
        },
        # Add more rules as needed
    ],
)

# Create Elasticsearch, Fluentd, and Kibana resources using Helm charts
namespace = Namespace("efk-namespace")

elasticsearch_chart = Chart(
    "elasticsearch",
    ChartOpts(
        namespace=namespace.metadata["name"],
        fetch_opts=k8s.HelmRepoOpts(
            repo="elastic",
            chart="elasticsearch",
        ),
        values={
            "elasticsearchPassword": elasticsearch_password.result,
            "service": {
                "annotations": {
                    "service.beta.kubernetes.io/openstack-internal-ip": subnet.allocation_pools[0]["start"],
                },
            },
            # Merge selected config
            **selected_config.get("elasticsearch", {}),
        },
    ),
)

fluentd_chart = Chart(
    "fluentd",
    ChartOpts(
        namespace=namespace.metadata["name"],
        fetch_opts=k8s.HelmRepoOpts(
            repo="fluent/fluentd-elasticsearch",
            chart="fluentd-elasticsearch",
        ),
        values={
            "elasticsearch.host": elasticsearch_chart.resources[0].metadata["name"],
            **selected_config.get("fluentd", {}),  # Merge selected config
        },
    ),
)

kibana_chart = Chart(
    "kibana",
    ChartOpts(
        namespace=namespace.metadata["name"],
        fetch_opts=k8s.HelmRepoOpts(
            repo="elastic",
            chart="kibana",
        ),
        values={
            "elasticsearchHosts": f"http://{elasticsearch_chart.resources[0].metadata['name']}:9200",
            **selected_config.get("kibana", {}),  # Merge selected config
        },
    ),
)

# Export necessary information
pulumi.export("elasticsearch_endpoint",
              elasticsearch_chart.resources[0].metadata["name"])
pulumi.export("kibana_endpoint", kibana_chart.resources[0].metadata["name"])
