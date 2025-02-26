from dataclasses import dataclass
import typing

from dataclasses_json import dataclass_json
import requests


class SemaphoreUIClient:

    def __init__(self, host, path="/api"):
        self.http = requests.Session()
        self.api_endpoint = f"{host}{path}"

    def login(self, user, password):
        response = self.http.post(
            f"{self.api_endpoint}/auth/login", json={"auth": user, "password": password}
        )
        if response.status_code != 204:
            raise ValueError(
                f"Username and/or password incorrect. Response from POST /auth/login was {response.status_code}"
            )

    def whoami(self):
        response = self.http.get(f"{self.api_endpoint}/auth/login")
        assert (
            response.status_code == 200
        ), f"GET /auth/login return response {response.status_code}"

    def logout(self):
        response = self.http.post(f"{self.api_endpoint}/auth/logout")
        assert response.status_code == 204

    def tokens(self) -> typing.List["Token"]:
        response = self.http.get(f"{self.api_endpoint}/user/tokens")
        assert response.status_code == 200
        return [Token(**token_data, client=self) for token_data in response.json()]

    def create_token(self) -> "Token":
        response = self.http.post(f"{self.api_endpoint}/user/tokens")
        assert response.status_code == 201
        return Token(**response.json(), client=self)

    def delete_token(self, id):
        response = self.http.post(f"{self.api_endpoint}/user/tokens/{id}")
        assert response.status_code in (204, 404)  # 404 if token was already expired

    def projects(self) -> typing.List["Project"]:
        response = self.http.get(f"{self.api_endpoint}/projects")
        assert response.status_code == 200
        return [Project(**data, client=self) for data in response.json()]

    def get_project(self, id: int) -> "Project":
        response = self.http.get(f"{self.api_endpoint}/project/{id}")
        assert response.status_code == 200
        return Project(**response.json(), client=self)

    def create_project(
        self,
        name: str,
        alert: bool,
        alert_chat: str,
        max_parallel_tasks: int,
        type: typing.Optional[str] = None,
        demo: typing.Optional[bool] = False,
    ) -> "Project":
        response = self.http.post(
            f"{self.api_endpoint}/projects",
            json={
                "name": name,
                "alert": alert,
                "alert_chat": alert_chat,
                "max_parallel_tasks": max_parallel_tasks,
                "type": type,
                "demo": demo,
            },
        )
        assert response.status_code == 201
        return Project(**response.json(), client=self)

    def delete_project(self, id: int):
        response = self.http.delete(f"{self.api_endpoint}/project/{id}")
        assert response.status_code == 204

    def update_project(
        self,
        id: int,
        name: str,
        alert: bool,
        alert_chat: str,
        max_parallel_tasks: int,
        type: str,
    ):
        response = self.http.put(
            f"{self.api_endpoint}/project/{id}",
            json={
                "name": name,
                "alert": alert,
            },
        )
        assert response.status_code == 204

    def backup_project(self, id: int) -> "ProjectBackup":
        response = self.http.get(f"{self.api_endpoint}/project/{id}/backup")
        assert response.status_code == 200
        return ProjectBackup(**response.json())

    def get_project_role(self, id: int) -> "Permissions":
        response = self.http.get(f"{self.api_endpoint}/project/{id}/role")
        assert response.status_code == 200
        return Permissions(**response.json())

    def get_project_events(self, id: int) -> typing.List["Event"]:
        response = self.http.get(f"{self.api_endpoint}/project/{id}/events")
        assert response.status_code == 200
        return [Event(**data) for data in response.json()]

    def get_project_users(self, id: int, sort: str, order: str) -> typing.List["User"]:
        response = self.http.get(f"{self.api_endpoint}/project/{id}/")
        assert response.status_code == 200
        return [User(**data) for data in response.json()]

    def add_project_user(self, id: int, user: "User"):
        response = self.http.post(
            f"{self.api_endpoint}/project/{id}/users", json=user.to_json()  # type: ignore
        )
        assert response.status_code == 204

    def update_project_user(self, id: int, user: "User"):
        response = self.http.put(
            f"{self.api_endpoint}/project/{id}/users/{user.id}", json=user.to_json()  # type: ignore
        )
        assert response.status_code == 204

    def remove_project_user(self, id: int, user_id: int):
        response = self.http.delete(f"{self.api_endpoint}/project/{id}/users/{user_id}")
        assert response.status_code == 204

    def get_project_integrations(self, id: int) -> typing.List["Integration"]:
        response = self.http.get(f"{self.api_endpoint}/project/{id}/integrations")
        assert response.status_code == 200
        return [Integration(**data, client=self) for data in response.json()]

    def create_project_integrations(
        self, project_id: int, name: str, template_id: int
    ) -> "Integration":
        response = self.http.post(
            f"{self.api_endpoint}/project/{id}integrations",
            json={"project_id": project_id, "name": name, "template_id": template_id},
        )
        assert response.status_code == 200
        return Integration(**response.json(), client=self)

    def update_project_integration(
        self, project_id: int, id: int, name: str, template_id: int
    ):
        response = self.http.put(
            f"{self.api_endpoint}/project/{project_id}/integrations/{id}",
            json={"project_id": project_id, "name": name, "template_id": template_id},
        )
        assert response.status_code == 204

    def delete_project_integration(self, project_id: int, id: int):
        response = self.http.delete(
            f"{self.api_endpoint}/project/{project_id}/integrations/{id}"
        )
        assert response.status_code == 204

    def get_project_keys(
        self,
        project_id: int,
        key_type: typing.Optional[str] = None,
        sort: typing.Optional[str] = None,
        order: typing.Optional[str] = None,
    ) -> typing.List["Key"]:
        response = self.http.get(f"{self.api_endpoint}/project/{project_id}/keys")
        assert response.status_code == 200
        return [Key(**data, client=self) for data in response.json()]

    def create_project_key(
        self,
        project_id: int,
        name: str,
        key_type: str,
        override_secret: bool,
        login_password: typing.Optional[typing.Tuple[str, str]],
        ssh: typing.Optional[typing.Tuple[str, str, str]],
    ) -> "Key":
        if key_type not in ("ssh", "login_password"):
            raise ValueError(f"Invalid key_type: {key_type}. Acceptable values are: ssh, login_password")
        if key_type == "ssh" and ssh is None:
            raise ValueError("ssh parameter must be set on key_type: ssh")
        elif key_type == "login_password" and login_password is None:
            raise ValueError("login_password parameter must be set on key_type: login_password")
        response = self.http.post(
            f"{self.api_endpoint}/project/{project_id}/keys",
            json={
                "id": 0,
                "project_id": project_id,
                "name": name,
                "type": key_type,
                "override_secret": override_secret,
                "login_password": {
                    "login": login_password[0],
                    "password": login_password[1],
                },
                "ssh": {
                    "login": ssh[0],
                    "passphrase": ssh[1],
                    "private_key": ssh[2],
                },
            },
        )
        assert response.status_code == 204

        try:
            return Key(**response.json(), client=self)
        except ValueError:
            # Sporadically, the response is an empty string. Get the actual key from the API
            return [
                key for key in self.get_project_keys(project_id) if key.name == name
            ][0]

    def delete_project_key(self, project_id: int, id: int):
        response = self.http.delete(
            f"{self.api_endpoint}/project/{project_id}/keys/{id}"
        )
        assert response.status_code == 204

    def get_project_repositories(self, project_id: int) -> typing.List["Repository"]:
        response = self.http.get(
            f"{self.api_endpoint}/project/{project_id}/repositories"
        )
        assert response.status_code == 200
        return [Repository(**data, client=self) for data in response.json()]

    def create_project_repository(
        self, project_id: int, name: str, git_url: str, git_branch: str, ssh_key_id: int
    ) -> "Repository":
        response = self.http.post(
            f"{self.api_endpoint}/project/{project_id}/repositories",
            json={
                "name": name,
                "project_id": project_id,
                "git_url": git_url,
                "git_branch": git_branch,
                "ssh_key_id": ssh_key_id,
            },
        )
        assert response.status_code == 204
        try:
            return Repository(**response.json(), client=self)
        except ValueError:
            return [
                repo
                for repo in self.get_project_repositories(project_id)
                if repo.name == name
            ][0]

    def delete_project_repository(self, project_id: int, id: int):
        response = self.http.delete(
            f"{self.api_endpoint}/project/{project_id}/repositories/{id}"
        )
        assert response.status_code == 204

    def get_project_environments(self, project_id: int) -> typing.List["Environment"]:
        response = self.http.get(
            f"{self.api_endpoint}/project/{project_id}/environment"
        )
        assert response.status_code == 200
        return [Environment(**data, client=self) for data in response.json()]

    def create_project_environment(
        self,
        project_id: int,
        name: str,
        password: str,
        json: str,
        env: str,
        secrets: typing.List[typing.Dict[typing.Any, typing.Any]],
    ) -> "Environment":
        response = self.http.post(
            f"{self.api_endpoint}/project/{project_id}/environment",
            json={
                "name": name,
                "project_id": project_id,
                "password": None,
                "json": json,
                "env": env,
                "secrets": secrets,
            },
        )
        assert response.status_code == 204
        try:
            return Environment(**response.json(), client=self)
        except ValueError:
            return [
                env
                for env in self.get_project_environments(project_id)
                if env.name == name
            ][0]

    def delete_project_environment(self, project_id: int, id: int):
        response = self.http.delete(
            f"{self.api_endpoint}/project/{project_id}/environment/{id}"
        )
        assert response.status_code == 204

    def get_project_views(self, project_id: int) -> typing.List["View"]:
        response = self.http.get(f"{self.api_endpoint}/project/{project_id}/views")
        assert response.status_code == 200
        return [View(**data, client=self) for data in response.json()]

    def create_project_view(self, project_id: int, title: str, position: int) -> "View":
        response = self.http.post(
            f"{self.api_endpoint}/project/{project_id}/views",
            json={"position": position, "title": title, "project_id": project_id},
        )
        assert response.status_code == 201
        return View(**response.json(), client=self)

    def delete_project_view(self, project_id: int, id: int):
        response = self.http.delete(
            f"{self.api_endpoint}/project/{project_id}/views/{id}"
        )
        assert response.status_code == 204

    def get_project_inventories(self, project_id: int) -> typing.List["Inventory"]:
        response = self.http.get(f"{self.api_endpoint}/project/{project_id}/inventory")
        assert response.status_code == 200
        return [Inventory(**data, client=self) for data in response.json()]

    def create_project_inventory(
        self,
        project_id: int,
        name: str,
        inventory: str,
        ssh_key_id: int,
        become_key_id: int,
        type: str,
        repostory_id: int,
    ) -> "Inventory":
        response = self.http.post(
            f"{self.api_endpoint}/project/{project_id}/inventory",
            json={
                "id": 0,
                "name": name,
                "project_id": project_id,
                "inventory": inventory,
                "ssh_key_id": ssh_key_id,
                "become_key_id": become_key_id,
                "type": type,
                "repository_id": repostory_id,
            },
        )
        assert response.status_code == 201
        return Inventory(**response.json(), client=self)

    def delete_project_inventory(self, project_id: int, id: int):
        response = self.http.delete(
            f"{self.api_endpoint}/project/{project_id}/inventory/{id}"
        )
        assert response.status_code == 204

    def get_project_templates(self, project_id: int) -> typing.List["Template"]:
        response = self.http.get(f"{self.api_endpoint}/project/{project_id}/templates")
        assert response.status_code == 200
        return [Template(**data, client=self) for data in response.json()]

    def create_project_template(
        self,
        project_id: int,
        name: str,
        repository_id: int,
        inventory_id: int,
        environment_id: int,
        view_id: int,
        vaults: typing.List[typing.Dict[str, typing.Any]],
        playbook: str,
        arguments: str,
        description: str,
        allow_override_args_in_task: bool,
        limit: int,
        suppress_success_alerts: bool,
        app: str,
        git_branch: str,
        survey_vars: typing.List[typing.Dict[str, typing.Any]],
        type: str,
        start_version: str,
        autorun: bool,
        build_template_id: typing.Optional[int]=None,
    ) -> "Template":
        response = self.http.post(
            f"{self.api_endpoint}/project/{project_id}/templates",
            json={
                "id": 1,
                "project_id": project_id,
                "inventory_id": inventory_id,
                "repository_id": repository_id,
                "environment_id": environment_id,
                "view_id": view_id,
                "vaults": vaults,
                "name": name,
                "playbook": playbook,
                "arguments": arguments,
                "description": description,
                "allow_override_args_in_task": allow_override_args_in_task,
                "limit": limit,
                "suppress_success_alerts": suppress_success_alerts,
                "app": app,
                "git_branch": git_branch,
                "survey_vars": survey_vars,
                "type": type,
                "start_version": start_version,
                "build_template_id": build_template_id,
                "autorun": autorun,
            },
        )
        assert (
            response.status_code == 201
        ), f"Expected response code 201, got {response.status_code}"
        return Template(**response.json(), client=self)
    
    def delete_project_template(self, project_id: int, id: int):
        response = self.http.delete(
            f"{self.api_endpoint}/project/{project_id}/templates/{id}"
        )
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
        self.client.update_project_integration(
            self.project_id, self.id, self.name, self.template_id
        )

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
        self.client.update_project(
            self.id,
            self.name,
            self.alert,
            self.alert_chat,
            self.max_parallel_tasks,
            self.type,
        )

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

    def keys(self) -> typing.List["Key"]:
        return self.client.get_project_keys(self.id)

    def create_key(
        self,
        name: str,
        key_type: str,
        override_secret: bool,
        string: str,
        login_password: typing.Optional[typing.Tuple[str, str]],
        ssh: typing.Optional[typing.Tuple[str, str, str]],
    ):
        return self.client.create_project_key(
            self.id, name, key_type, override_secret, login_password, ssh
        )

    def repositories(self) -> typing.List["Repository"]:
        return self.client.get_project_repositories(self.id)

    def create_repository(
        self, name: str, git_url: str, git_branch: str, ssh_key_id: int
    ) -> "Repository":
        return self.client.create_project_repository(
            self.id, name, git_url, git_branch, ssh_key_id
        )

    def environments(self) -> typing.List["Environment"]:
        return self.client.get_project_environments(self.id)

    def create_environment(
        self,
        name: str,
        password: str,
        json: str,
        env: str,
        secrets: typing.List[typing.Dict[typing.Any, typing.Any]],
    ) -> "Environment":
        return self.client.create_project_environment(
            self.id, name, password, json, env, secrets
        )

    def views(self) -> typing.List["View"]:
        return self.client.get_project_views(self.id)

    def create_view(self, title: str, position: int) -> "View":
        return self.client.create_project_view(self.id, title, position)

    def inventories(self) -> typing.List["Inventory"]:
        return self.client.get_project_inventories(self.id)

    def create_inventory(
        self,
        name: str,
        inventory: str,
        ssh_key_id: int,
        become_key_id: int,
        type: str,
        repository_id: int,
    ) -> "Inventory":
        return self.client.create_project_inventory(
            self.id, name, inventory, ssh_key_id, become_key_id, type, repository_id
        )

    def templates(self) -> typing.List["Template"]:
        return self.client.get_project_templates(self.id)

    def create_template(
        self,
        name: str,
        repository_id: int,
        inventory_id: int,
        environment_id: int,
        view_id: int,
        vaults: typing.List[typing.Dict[str, typing.Any]],
        playbook: str,
        arguments: str,
        description: str,
        allow_override_args_in_task: bool,
        limit: int,
        suppress_success_alerts: bool,
        app: str,
        git_branch: str,
        survey_vars: typing.List[typing.Dict[str, typing.Any]],
        type: str,
        start_version: str,
        autorun: bool,
        build_template_id: typing.Optional[int]=None,
    ) -> "Template":
        return self.client.create_project_template(
            self.id,
            name,
            repository_id,
            inventory_id,
            environment_id,
            view_id,
            vaults,
            playbook,
            arguments,
            description,
            allow_override_args_in_task,
            limit,
            suppress_success_alerts,
            app,
            git_branch,
            survey_vars,
            type,
            start_version,
            autorun,
            build_template_id,
        )


@dataclass
class Permissions:
    role: str
    permissions: int


@dataclass
class ProjectBackup: ...


@dataclass
class Event:
    project_id: int
    user_id: int
    object_id: str
    object_type: str
    description: str


@dataclass_json
@dataclass
class User:
    user_id: int
    role: str

    @property
    def id(self) -> int:
        return self.user_id


@dataclass
class KeySsh:
    login: str
    passphrase: str
    private_key: str


@dataclass
class KeyLoginPassword:
    login: str
    password: str


@dataclass
class Key:
    id: int
    name: str
    type: str
    project_id: int

    string: str
    override_secret: bool
    login_password: KeyLoginPassword
    ssh: KeySsh

    client: SemaphoreUIClient

    @classmethod
    def from_dict(cls, **keys) -> "Key":
        ssh = KeySsh(
            login=keys["ssh"]["login"],
            passphrase=keys["ssh"]["passphrase"],
            private_key=keys["ssh"]["private_key"],
        )
        login_password = KeyLoginPassword(
            login=keys["login_password"]["login"],
            password=keys["login_password"]["password"],
        )
        del keys["ssh"]
        del keys["login_password"]
        return cls(**keys, ssh=ssh, login_password=login_password)

    def delete(self):
        self.client.delete_project_key(self.project_id, self.id)


@dataclass
class Repository:
    id: int
    name: str
    project_id: int
    git_url: str
    git_branch: str
    ssh_key_id: int

    client: SemaphoreUIClient

    def delete(self):
        self.client.delete_project_repository(self.project_id, self.id)


@dataclass
class Secret:
    id: int
    name: str
    type: str


@dataclass
class Environment:
    id: int
    name: str
    project_id: int
    password: str
    json: str
    env: str
    secrets: typing.List["Secret"]

    client: SemaphoreUIClient

    def delete(self):
        self.client.delete_project_environment(self.project_id, self.id)


@dataclass
class View:
    id: int
    title: str
    position: int
    project_id: int

    client: SemaphoreUIClient

    def delete(self):
        self.client.delete_project_view(self.project_id, self.id)


@dataclass
class Inventory:
    id: int
    name: str
    project_id: int
    inventory: str
    ssh_key_id: int
    become_key_id: int
    type: str

    holder_id: int
    repository_id: int

    client: SemaphoreUIClient

    def delete(self):
        self.client.delete_project_inventory(self.project_id, self.id)


@dataclass
class Template:
    id: int
    project_id: int
    repository_id: int
    inventory_id: int
    environment_id: int
    view_id: int
    name: str
    playbook: str
    arguments: str
    description: str
    allow_override_args_in_task: bool
    suppress_success_alerts: bool
    app: str
    survey_vars: typing.List[typing.Dict[str, typing.Any]]
    type: str
    start_version: str
    build_template_id: int
    autorun: bool
    vault_key_id: int
    last_task: int
    tasks: int


    client: SemaphoreUIClient

    def delete(self):
        self.client.delete_project_template(self.project_id, self.id)
