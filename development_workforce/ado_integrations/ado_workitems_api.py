import base64
from enum import Enum
import os
import requests
from dotenv import load_dotenv

from development_workforce.ado_integrations.ado_connection import ADOConnection
from development_workforce.ado_integrations.base_ado_workitems_api import BaseAdoWorkitemsApi

class WorkItemType(Enum):
    Bug = "Bug"
    Task = "Task"
    Feature = "Feature"
    Epic = "Epic"
    UserStory = "User Story"


load_dotenv()

class ADOWorkitemsApi(ADOConnection, BaseAdoWorkitemsApi):
    def get_headers(self, method_type="GET"):
        encoded_bytes = base64.b64encode(f':{self.personal_access_token}'.encode('ascii'))
        encoded_pat = str(encoded_bytes, 'ascii')
        return {
            'Authorization': f'Basic {encoded_pat}',
            'Content-Type': 'application/json-patch+json' if method_type == "PATCH" else 'application/json',
        }
    
    def make_request(self, method, url, **kwargs):
        headers = self.get_headers(method)
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

    def fetch_all_objects(self):
        url = f"{self.organization_url}/{self.project_name}/_apis/wit/wiql?api-version=6.0"
        query = {"query": "SELECT [Id], [Title], [State] FROM WorkItems WHERE [System.TeamProject] = @project"}
        response_data = self.make_request('POST', url, json=query)
        work_items = response_data["workItems"]
        return [self.fetch_object_details(work_item['id']) for work_item in work_items]

    def fetch_object_details(self, work_item_id: int):
        url = f"{self.organization_url}/{self.project_name}/_apis/wit/workitems/{work_item_id}?api-version=6.0"
        work_item_details = self.make_request('GET', url)
        return {
            'id': work_item_details['id'],
            'title': work_item_details['fields']['System.Title'],
            'state': work_item_details['fields']['System.State'],
            'description': work_item_details['fields']['System.Description']
        }
    
    def update_object_state(self, work_item_id, new_state):
        url = f"{self.organization_url}/{self.project_name}/_apis/wit/workitems/{work_item_id}?api-version=7.0"
        document = [
            {
                "op": "replace",
                "path": "/fields/System.State",
                "value": new_state
            }
        ]
        self.make_request('PATCH', url, json=document)


    def create_object(self, title, description, work_item_type):
        url = f"{self.organization_url}/{self.project_name}/_apis/wit/workitems/${work_item_type}?api-version=6.0"
        document = [
            {
                "op": "add",
                "path": "/fields/System.Title",
                "value": title
            },
            {
                "op": "add",
                "path": "/fields/System.Description",
                "value": description
            }
        ]
        self.make_request('POST', url, json=document)

    def update_object_details(self, work_item_id, title, description):
        url = f"{self.organization_url}/{self.project_name}/_apis/wit/workitems/{work_item_id}?api-version=6.0"
        document = [
            {
                "op": "test",
                "path": "/rev",
                "value": work_item_id
            },
            {
                "op": "replace",
                "path": "/fields/System.Title",
                "value": title
            },
            {
                "op": "replace",
                "path": "/fields/System.Description",
                "value": description
            }
        ]
        self.make_request('PATCH', url, json=document)

    def delete_object(self, work_item_id):
        url = f"{self.organization_url}/{self.project_name}/_apis/wit/workitems/{work_item_id}?api-version=6.0"
        self.make_request('DELETE', url)

    def set_relationship(self, source_id, target_id, relationship):
        url = f"{self.organization_url}/{self.project_name}/_apis/wit/workitems/{source_id}?api-version=6.0"
        document = [
            {
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": relationship,
                    "url": f"{self.organization_url}/{self.project_name}/_apis/wit/workitems/{target_id}"
                }
            }
        ]
        self.make_request('PATCH', url, json=document)


if __name__ == "__main__":
    interface = ADOWorkitemsApi()
    objects = interface.fetch_all_objects()
    print(objects)
    if objects:
        # Choose the first object in the list
        first_object = objects[0]
        # Update the details of the first object
        # interface.update_object_details(first_object['id'], "Updated Title", "Updated Description")
        interface.update_object_state(first_object['id'], "Closed")

    


