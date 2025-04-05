from dataclasses import dataclass
import typing

from dataclasses_json import dataclass_json
import requests


class SemaphoreUIClient:
    def __init__(self, host: str, path: str = "/api"):
        self.http = requests.Session()
        if host.endswith("/"):
            host = host.strip("/")
        if not path.startswith("/"):
            path = f"/{path}"
        self.api_endpoint = f"{host}{path}"

    def login(self, user: str, password: str) -> None:
        response = self.http.post(
            f"{self.api_endpoint}/auth/login", json={"auth": user, "password": password}
        )
        if response.status_code != 204:
            raise ValueError(
                f"Username and/or password incorrect. Response from POST /auth/login was {response.status_code}"
            )

    def whoami(self) -> None:
        response = self.http.get(f"{self.api_endpoint}/auth/login")
        assert response.status_code == 200, (
            f"GET /auth/login return response {response.status_code}"
        )

    def logout(self) -> None:
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

    def delete_token(self, id: str) -> None:
        response = self.http.delete(f"{self.api_endpoint}/user/tokens/{id}")
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

    def delete_project(self, id: int) -> None:
        response = self.http.delete(f"{self.api_endpoint}/project/{id}")
        assert response.status_code == 204

    def update_project(
        self,
        id: int,
        name: str,
        alert: bool,
        alert_chat: str,
        max_parallel_tasks: int,
        type: typing.Optional[str] = None,
    ) -> None:
        response = self.http.put(
            f"{self.api_endpoint}/project/{id}",
            json={
                "name": name,
                "alert": alert,
                "alert_chat": alert_chat,
                "max_parallel_tasks": max_parallel_tasks,
                "type": type,
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

    def add_project_user(self, id: int, user: "User") -> None:
        response = self.http.post(
            f"{self.api_endpoint}/project/{id}/users",
            json=user.to_json(),  # type: ignore
        )
        assert response.status_code == 204

    def update_project_user(self, id: int, user: "User") -> None:
        response = self.http.put(
            f"{self.api_endpoint}/project/{id}/users/{user.id}",
            json=user.to_json(),  # type: ignore
        )
        assert response.status_code == 204

    def remove_project_user(self, id: int, user_id: int) -> None:
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
    ) -> None:
        response = self.http.put(
            f"{self.api_endpoint}/project/{project_id}/integrations/{id}",
            json={"project_id": project_id, "name": name, "template_id": template_id},
        )
        assert response.status_code == 204

    def delete_project_integration(self, project_id: int, id: int) -> None:
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
            raise ValueError(
                f"Invalid key_type: {key_type}. Acceptable values are: ssh, login_password"
            )
        if key_type == "ssh":
            if ssh is None:
                raise ValueError("ssh parameter must be set on key_type: ssh")
            json_data = {
                "id": 0,
                "project_id": project_id,
                "name": name,
                "type": key_type,
                "override_secret": override_secret,
                "login_password": {
                    "login": "",
                    "password": "",
                },
                "ssh": {
                    "login": ssh[0],
                    "passphrase": ssh[1],
                    "private_key": ssh[2],
                },
            }
        elif key_type == "login_password":
            if login_password is None:
                raise ValueError(
                    "login_password parameter must be set on key_type: login_password"
                )
            json_data = {
                "id": 0,
                "project_id": project_id,
                "name": name,
                "type": key_type,
                "override_secret": override_secret,
                "login_password": {
                    "login": login_password[0],
                    "password": login_password[1],
                },
                "ssh": {"login": "", "passphrase": "", "private_key": ""},
            }
        response = self.http.post(
            f"{self.api_endpoint}/project/{project_id}/keys", json=json_data
        )
        assert response.status_code == 204

        try:
            return Key(**response.json(), client=self)
        except ValueError:
            # Sporadically, the response is an empty string. Get the actual key from the API
            return [
                key for key in self.get_project_keys(project_id) if key.name == name
            ][0]

    def delete_project_key(self, project_id: int, id: int) -> None:
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

    def delete_project_repository(self, project_id: int, id: int) -> None:
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

    def delete_project_environment(self, project_id: int, id: int) -> None:
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

    def delete_project_view(self, project_id: int, id: int) -> None:
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

    def delete_project_inventory(self, project_id: int, id: int) -> None:
        response = self.http.delete(
            f"{self.api_endpoint}/project/{project_id}/inventory/{id}"
        )
        assert response.status_code == 204

    def get_project_templates(self, project_id: int) -> typing.List["Template"]:
        response = self.http.get(f"{self.api_endpoint}/project/{project_id}/templates")
        assert response.status_code == 200
        templates: typing.List["Template"] = []
        for template in response.json():
            if template["last_task"] is not None:
                template["last_task"] = Task(**template["last_task"], client=self)
            templates.append(Template(**template, client=self))
        return templates

    def create_project_template(
        self,
        project_id: int,
        name: str,
        repository_id: int,
        inventory_id: int,
        environment_id: int,
        view_id: int,
        vault_id: int,
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
        build_template_id: typing.Optional[int] = None,
    ) -> "Template":
        response = self.http.post(
            f"{self.api_endpoint}/project/{project_id}/templates",
            json={
                "id": 0,
                "project_id": project_id,
                "inventory_id": inventory_id,
                "repository_id": repository_id,
                "environment_id": environment_id,
                "view_id": view_id,
                "vault_key_id": vault_id,
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
        assert response.status_code == 201, (
            f"Expected response code 201, got {response.status_code}"
        )
        return Template(**response.json(), client=self)

    def delete_project_template(self, project_id: int, id: int) -> None:
        response = self.http.delete(
            f"{self.api_endpoint}/project/{project_id}/templates/{id}"
        )
        assert response.status_code == 204

    def get_project_schedules(self, project_id: int) -> typing.List["Schedule"]:
        response = self.http.get(f"{self.api_endpoint}/project/{project_id}/schedules")
        assert response.status_code == 200
        return [Schedule(**schedule, client=self) for schedule in response.json()]

    def create_project_schedule(
        self,
        project_id: int,
        template_id: int,
        name: str,
        cron_format: str,
        active: bool = True,
    ) -> "Schedule":
        response = self.http.post(
            f"{self.api_endpoint}/project/{project_id}/schedules",
            json={
                "id": 0,
                "project_id": project_id,
                "template_id": template_id,
                "name": name,
                "cron_format": cron_format,
                "active": active,
            },
        )
        assert response.status_code == 201
        return Schedule(**response.json(), client=self)

    def update_project_schedule(
        self,
        project_id: int,
        schedule_id: int,
        template_id: int,
        name: str,
        cron_format: str,
        active: bool,
    ) -> None:
        response = self.http.post(
            f"{self.api_endpoint}/project/{project_id}/schedules",
            json={
                "id": schedule_id,
                "project_id": project_id,
                "template_id": template_id,
                "name": name,
                "cron_format": cron_format,
                "active": active,
            },
        )
        assert response.status_code == 201

    def delete_project_schedule(self, project_id: int, schedule_id: int) -> None:
        response = self.http.delete(
            f"{self.api_endpoint}/project/{project_id}/schedules/{schedule_id}"
        )
        assert response.status_code == 204

    def get_project_tasks(self, project_id: int) -> typing.List["Task"]:
        response = self.http.get(f"{self.api_endpoint}/project/{project_id}/tasks")
        assert response.status_code == 200
        return [Task(**task, client=self) for task in response.json()]

    def stop_project_task(self, project_id: int, id: int) -> None:
        response = self.http.post(
            f"{self.api_endpoint}/project/{project_id}/tasks/{id}/stop"
        )
        assert response.status_code == 204

    def get_project_task(self, project_id: int, id: int) -> "Task":
        response = self.http.get(f"{self.api_endpoint}/project/{project_id}/tasks/{id}")
        assert response.status_code == 200
        return Task(**response.json(), project_id=project_id, client=self)

    def delete_project_task(self, project_id: int, id: int) -> None:
        response = self.http.delete(
            f"{self.api_endpoint}/project/{project_id}/tasks/{id}"
        )
        assert response.status_code == 204

    def get_project_task_output(self, project_id: int, id: int) -> str:
        response = self.http.get(
            f"{self.api_endpoint}/project/{project_id}/tasks/{id}/output"
        )
        assert response.status_code == 200
        return "\n".join(data["output"] for data in response.json())


@dataclass
class Integration:
    """A project integration"""

    id: int
    name: str
    project_id: int
    template_id: int

    client: SemaphoreUIClient

    def save(self) -> None:
        self.client.update_project_integration(
            self.project_id, self.id, self.name, self.template_id
        )

    def delete(self) -> None:
        self.client.delete_project_integration(self.project_id, self.id)


@dataclass
class Token:
    """An authorization token."""

    id: str
    created: str
    expired: bool
    user_id: int

    client: SemaphoreUIClient

    def delete(self) -> None:
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

    def delete(self) -> None:
        self.client.delete_project(self.id)

    def save(self) -> None:
        self.client.update_project(
            self.id,
            self.name,
            self.alert,
            self.alert_chat,
            self.max_parallel_tasks,
            self.type,
        )

    def backup(self) -> "ProjectBackup":
        return self.client.backup_project(self.id)

    def role(self) -> "Permissions":
        return self.client.get_project_role(self.id)

    def events(self) -> typing.List["Event"]:
        return self.client.get_project_events(self.id)

    def users(self, sort: str, order: str) -> typing.List["User"]:
        return self.client.get_project_users(self.id, sort, order)

    def add_user(self, user: "User") -> None:
        return self.client.add_project_user(self.id, user)

    def remove_user(self, user_id: int) -> None:
        return self.client.remove_project_user(self.id, user_id)

    def update_user(self, user: "User") -> None:
        return self.client.update_project_user(self.id, user)

    def keys(self) -> typing.List["Key"]:
        return self.client.get_project_keys(self.id)

    def create_key(
        self,
        name: str,
        key_type: str,
        override_secret: bool = False,
        login_password: typing.Optional[typing.Tuple[str, str]] = None,
        ssh: typing.Optional[typing.Tuple[str, str, str]] = None,
    ) -> "Key":
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
        vault_id: int,
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
        build_template_id: typing.Optional[int] = None,
    ) -> "Template":
        return self.client.create_project_template(
            self.id,
            name,
            repository_id,
            inventory_id,
            environment_id,
            view_id,
            vault_id,
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

    def schedules(self) -> typing.List["Schedule"]:
        return self.client.get_project_schedules(self.id)

    def create_schedule(
        self, template_id: int, name: str, cron_format: str, active: bool = True
    ) -> "Schedule":
        return self.client.create_project_schedule(
            self.id, template_id, name, cron_format, active
        )

    def tasks(self) -> typing.List["Task"]:
        return self.client.get_project_tasks(self.id)

    def get_task(self, task_id: int) -> "Task":
        return self.client.get_project_task(self.id, task_id)


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

    def delete(self) -> None:
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

    def delete(self) -> None:
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

    def delete(self) -> None:
        self.client.delete_project_environment(self.project_id, self.id)


@dataclass
class View:
    id: int
    title: str
    position: int
    project_id: int

    client: SemaphoreUIClient

    def delete(self) -> None:
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

    def delete(self) -> None:
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
    last_task: typing.Optional["Task"]
    tasks: int

    client: SemaphoreUIClient

    def delete(self) -> None:
        self.client.delete_project_template(self.project_id, self.id)


@dataclass
class Schedule:
    id: int
    cron_format: str
    project_id: int
    template_id: int
    repository_id: typing.Optional[int]
    name: str
    active: bool

    client: SemaphoreUIClient

    def save(self) -> None:
        self.client.update_project_schedule(
            self.project_id,
            self.id,
            self.template_id,
            self.name,
            self.cron_format,
            self.active,
        )

    def delete(self) -> None:
        self.client.delete_project_schedule(self.project_id, self.id)


@dataclass
class Task:
    arguments: typing.Optional[str]
    build_task: typing.Optional["Task"]
    build_task_id: typing.Optional[int]
    commit_hash: typing.Optional[str]
    commit_message: str
    created: str
    debug: bool
    diff: bool
    dry_run: bool
    end: bool
    environment: str
    id: int
    integration_id: typing.Optional[int]
    inventory_id: typing.Optional[int]
    limit: str
    message: str
    playbook: str
    project_id: int
    schedule_id: typing.Optional[int]
    secret: str
    start: str
    status: str
    template_id: int
    tpl_alias: str
    tpl_app: str
    tpl_playbook: str
    tpl_type: str
    user_id: typing.Optional[int]
    user_name: typing.Optional[str]
    version: typing.Optional[str]

    client: SemaphoreUIClient

    def stop(self) -> None:
        self.client.stop_project_task(self.project_id, self.id)

    def delete(self) -> None:
        self.client.delete_project_task(self.project_id, self.id)

    def output(self) -> str:
        return self.client.get_project_task_output(self.project_id, self.id)
