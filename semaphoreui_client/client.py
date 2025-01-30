from dataclasses import dataclass
import json
import typing

import requests


class SemaphoreUIClient:

    def __init__(self, host, path="/api"):
        self.http = requests.Session()
        self.api_endpoint = f"{host}{path}"
        
    def login(self, user, password):
        response = self.http.post(f"{self.api_endpoint}/auth/login", json={"auth": user, "password": password})
        if response.status_code != 204:
            raise ValueError(f"Username and/or password incorrect. Response from POST /auth/login was {response.status_code}")
        import pdb; pdb.set_trace()
        
    def whoami(self):
        response = self.http.get(f"{self.api_endpoint}/auth/login")
        assert response.status_code == 200, f"GET /auth/login return response {response.status_code}"

    def logout(self):
        response = self.http.post(f"{self.api_endpoint}/auth/logout")
        assert response.status_code == 204

    def tokens(self) -> typing.List["Token"]:
        response = self.http.get(f"{self.api_endpoint}/user/tokens")
        assert response.status_code == 200
        return [Token(*token_data) for token_data in response.json()]
    
    def create_token(self) -> "Token":
        response = self.http.post(f"{self.api_endpoint}/user/tokens")
        assert response.status_code == 201
        return Token(*response.json())
    
    def delete_token(self, id):
        response = self.http.post(f"{self.api_endpoint}/user/tokens/{id}")
        assert response.status_code == 204
    
    def projects(self) -> typing.List["Project"]:
        response = self.http.get(f"{self.api_endpoint}/projects")
        assert response.status_code == 200
        return [Project(*data) for data in response.json()]
    
    def get_project(self, id: int) -> "Project":
        response = self.http.get(f"{self.api_endpoint}/project/{id}")
        assert response.status_code == 200
        return Project(*response.json())
    
    def create_project(self, name: str, alert: bool, alert_chat: str, max_parallel_tasks: int, type: str, demo: bool) -> "Project":
        response = self.http.get(f"{self.api_endpoint}/projects")
        assert response.status_code == 201
        return Project(*response.json())

    def delete_project(self, id: int):
        response = self.http.delete(f"{self.api_endpoint}/project")
        assert response.status_code == 204

    def update_project(self, id: int, name: str, alert: bool, alert_chat: str, max_parallel_tasks: int, type: str):
        response = self.http.put(f"{self.api_endpoint}/project/{id}", json={"name": name, "alert": alert, })
        assert response.status_code == 204

    def backup_project(self, id: int) -> "ProjectBackup":
        response = self.http.get(f"{self.api_endpoint}/project/{id}/backup")
        assert response.status_code == 200
        return ProjectBackup(*response.json())

    def get_project_role(self, id: int) -> "Permissions":
        response = self.http.get(f"{self.api_endpoint}/project/{id}/role")
        assert response.status_code == 200
    
    def get_project_events(self, id: int) -> typing.List["Events"]:
        response = self.http.get(f"{self.api_endpoint}/project/{id}/events")
        assert response.status_code == 200

    def get_project_users(self, id: int, sort: str, order: str) -> typing.List["User"]:
        response = self.http.get(f"{self.api_endpoint}/project/{id}/")
        assert response.status_code == 200
        return [User(*data) for data in response.json()]

    def add_project_user(self, id: int, user: "User"):
        response = self.http.post(f"{self.api_endpoint}/project/{id}/users", json=user.to_json())
        assert response.status_code == 204

    def update_project_user(self, id: int, user: "User"):
        response = self.http.put(f"{self.api_endpoint}/project/{id}/users/{user.id}", json=user.to_json())
        assert response.status_code == 204

    def remove_project_user(self, id: int, user_id: int):
        response = self.http.delete(f"{self.api_endpoint}/project/{id}/users/{user_id}")
        assert response.status_code == 204

    def get_project_integrations(self, id: int) -> typing.List["Integration"]:
        response = self.http.get(f"{self.api_endpoint}/projects/{id}/integrations")
        assert response.status_code == 200
        return [Integration(*data) for data in response.json()]

    def create_project_integrations(self, project_id: int, name: str, template_id: int) -> "Integration":
        response = self.http.post(f"{self.api_endpoint}/projects/{id}integrations", json={"project_id": project_id, "name": name, "template_id": template_id})
        assert response.status_code == 200
        return Integration(*response.json())
    
    def update_project_integration(self, project_id: int, id: int, name: str, template_id: int):
        response = self.http.put(f"{self.api_endpoint}/projects/{project_id}/integrations/{id}", json={"project_id": project_id, "name": name, "template_id": template_id})
        assert response.status_code == 204
    
    def delete_project_integration(self, project_id, id: int):
        response = self.http.delete(f"{self.api_endpoint}/projects/{project_id}/integrations/{id}")
        assert response.status_code == 204


@dataclass
class Integration:
    """A project integration"""
    id: int
    name: str
    project_id: int
    template_id: int

    client: SemaphoreUIClient

    def save(self):
        self.client.update_project_integration(self.project_id, self.id, self.name, self.template_id)

    def delete(self):
        self.client.delete_project_integration(self.project_id, self.id)


@dataclass
class Token:
    """An authorization token."""
    id: str
    created: str
    expired: bool
    user_id: int

    client: SemaphoreUIClient

    def delete(self):
        self.client.delete_token(self.id)


@dataclass
class Project:
    """A Semaphore UI project."""
    id: int
    name: str
    created: str
    alert: bool
    alert_chat: str
    max_parallel_tasks: int
    type: str  # This might be an enum?

    client: SemaphoreUIClient

    def delete(self):
        self.client.delete_project(self.id)

    def save(self):
        self.client.update_project(self.id, self.name, self.alert, self.alert_chat, self.max_parallel_tasks, self.type)

    def backup(self):
        return self.client.backup_project(self.id)

    def role(self):
        return self.client.get_project_role(self.id)

    def events(self):
        return self.client.get_project_events(self.id)

    def users(self, sort: str, order: str):
        return self.client.get_project_users(self.id, sort, order)

    def add_user(self, user: "User"):
        return self.client.add_project_user(self.id, user)

    def remove_user(self, user_id: int):
        return self.client.remove_project_user(self.id, user_id)
    
    def update_user(self, user: "User"):
        return self.client.update_project_user(self.id, user)
    

@dataclass
class ProjectBackup:
    ...
    

@dataclass
class User:
    user_id: int
    role: str

    @property
    def id(self) -> int:
        return self.user_id