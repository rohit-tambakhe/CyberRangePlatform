import requests
from keystoneauth1 import session
from keystoneauth1.identity import v3


class TenantDataConnector:
    def __init__(self, tenant_id, keystone_url, keystone_credentials):
        self.tenant_id = tenant_id
        self.api_url = f'https://{tenant_id}.api.tam-range.com'
        self.keystone_url = keystone_url
        self.keystone_credentials = keystone_credentials
        self.keystone_session = self.get_keystone_session()

    def get_keystone_session(self):
        auth = v3.Password(
            auth_url=self.keystone_url,
            **self.keystone_credentials
        )
        return session.Session(auth=auth)

    def get_api_token(self):
        token_endpoint = f'/v3/projects/{self.tenant_id}/api_token'
        response = self.keystone_session.get(
            f'{self.keystone_url}{token_endpoint}')
        response.raise_for_status()
        return response.json().get('api_token')

    def get_data(self, endpoint):
        api_token = self.get_api_token()
        headers = {'Authorization': f'Bearer {api_token}'}
        response = requests.get(f'{self.api_url}/{endpoint}', headers=headers)
        response.raise_for_status()
        return response.json()

    def update_data(self, endpoint, data):
        api_token = self.get_api_token()
        headers = {'Authorization': f'Bearer {api_token}'}
        response = requests.put(
            f'{self.api_url}/{endpoint}', headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def delete_data(self, endpoint):
        api_token = self.get_api_token()
        headers = {'Authorization': f'Bearer {api_token}'}
        response = requests.delete(
            f'{self.api_url}/{endpoint}', headers=headers)
        response.raise_for_status()

    def list_tenants(self):
        tenants = []
        tenants_endpoint = '/v3/projects'
        response = self.keystone_session.get(
            f'{self.keystone_url}{tenants_endpoint}')
        response.raise_for_status()
        tenants_data = response.json().get('projects', [])

        for tenant in tenants_data:
            tenants.append({
                'id': tenant['id'],
                'name': tenant['name']
            })

        return tenants

    def get_tenant_users(self):
        users = []
        users_endpoint = f'/v3/projects/{self.tenant_id}/users'
        response = self.keystone_session.get(
            f'{self.keystone_url}{users_endpoint}')
        response.raise_for_status()
        users_data = response.json().get('users', [])

        for user in users_data:
            users.append({
                'id': user['id'],
                'name': user['name'],
                'email': user['email']
            })

        return users

    def create_resource(self, endpoint, data):
        resource_endpoint = f'/v1/{self.tenant_id}/{endpoint}'
        response = requests.post(
            f'{self.api_url}/{resource_endpoint}', json=data)
        response.raise_for_status()
        return response.json()

    def complex_operation(self):
        result = {}
        initial_data = self.get_data('initial-endpoint')
        processed_data = self.process_data(initial_data)
        created_resource = self.create_resource(
            'complex-resource', processed_data)
        additional_info = self.get_data(
            f'info-endpoint/{created_resource["id"]}')

        result['initial_data'] = initial_data
        result['processed_data'] = processed_data
        result['created_resource'] = created_resource
        result['additional_info'] = additional_info

        return result

    def process_data(self, data):
        processed_data = {}
        # Add your data processing logic here
        return processed_data


if __name__ == "__main__":
    keystone_url = "https://keystone.tam-range.com:5000/v3"
    keystone_credentials = {
        "username": "admin",
        "password": "password",
        "user_domain_name": "Default",
        "project_domain_name": "Default",
        "project_name": "admin"
    }

    for tenant_id in ['tenant1', 'tenantN1']:
        tenant_connector = TenantDataConnector(
            tenant_id, keystone_url, keystone_credentials)
        data = tenant_connector.get_data('data-endpoint')
        print(f'Data for {tenant_id}: {data}')

        tenant_connector.create_resource('new-resource', {'key': 'value'})
        tenant_connector.update_data(
            'data-endpoint', {'updated_key': 'updated_value'})
        tenant_connector.delete_data('delete-endpoint')

        tenant_list = tenant_connector.list_tenants()
        print(f'Tenants: {tenant_list}')

        tenant_users = tenant_connector.get_tenant_users()
        print(f'Tenant Users: {tenant_users}')

        complex_result = tenant_connector.complex_operation()
        print(f'Complex Operation Result for {tenant_id}: {complex_result}')
