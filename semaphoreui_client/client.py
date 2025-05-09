from dataclasses import dataclass, field
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


@dataclass
class Integration:
    """A project integration"""

    id: int
    name: str
    project_id: int
    template_id: int

    client: SemaphoreUIClient

    def save(self) -> None:
        response = self.client.http.put(
            f"{self.client.api_endpoint}/project/{self.project_id}/integrations/{self.id}",
            json={
                "project_id": self.project_id,
                "name": self.name,
                "template_id": self.template_id,
            },
        )
        assert response.status_code == 204

    def delete(self) -> None:
        response = self.client.http.delete(
            f"{self.client.api_endpoint}/project/{self.project_id}/integrations/{self.id}"
        )
        assert response.status_code == 204


@dataclass
class Token:
    """An authorization token."""

    id: str
    created: str
    expired: bool
    user_id: int

    client: SemaphoreUIClient

    def delete(self) -> None:
        response = self.client.http.delete(
            f"{self.client.api_endpoint}/user/tokens/{self.id}"
        )
        assert response.status_code in (204, 404)  # 404 if token was already expired


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

    @property
    def url(self) -> str:
        return f"{self.client.api_endpoint}/project/{self.id}"

    def delete(self) -> None:
        response = self.client.http.delete(
            f"{self.client.api_endpoint}/project/{self.id}"
        )
        assert response.status_code == 204

    def save(self) -> None:
        response = self.client.http.put(
            f"{self.client.api_endpoint}/project/{self.id}",
            json={
                "name": self.name,
                "alert": self.alert,
                "alert_chat": self.alert_chat,
                "max_parallel_tasks": self.max_parallel_tasks,
                "type": self.type,
            },
        )
        assert response.status_code == 204

    def backup(self) -> "ProjectBackup":
        response = self.client.http.get(
            f"{self.client.api_endpoint}/project/{self.id}/backup"
        )
        assert response.status_code == 200
        return ProjectBackup(**response.json())

    def role(self) -> "Permissions":
        response = self.client.http.get(
            f"{self.client.api_endpoint}/project/{self.id}/role"
        )
        assert response.status_code == 200
        return Permissions(**response.json())

    def events(self) -> typing.List["Event"]:
        response = self.client.http.get(
            f"{self.client.api_endpoint}/project/{self.id}/events"
        )
        assert response.status_code == 200
        return [Event(**data) for data in response.json()]

    def users(
        self, sort: typing.Optional[str] = None, order: typing.Optional[str] = None
    ) -> typing.List["ProjectUser"]:
        params = {}
        if sort is not None:
            params["sort"] = sort
        if order is not None:
            params["order"] = order
        response = self.client.http.get(
            f"{self.client.api_endpoint}/project/{self.id}/users", params=params
        )
        assert response.status_code == 200
        return [
            ProjectUser(**data, client=self.client, project_id=self.id)
            for data in response.json()
        ]

    def add_user(self, user: "ProjectUser") -> None:
        response = self.client.http.post(
            f"{self.client.api_endpoint}/project/{self.id}/users",
            json=user.to_json(),  # type: ignore
        )
        assert response.status_code == 204

    def remove_user(self, user_id: int) -> None:
        response = self.client.http.delete(
            f"{self.client.api_endpoint}/project/{self.id}/users/{user_id}"
        )
        assert response.status_code == 204

    def update_user(self, user: "ProjectUser") -> None:
        response = self.client.http.put(
            f"{self.client.api_endpoint}/project/{self.id}/users/{user.id}",
            json=user.to_json(),  # type: ignore
        )
        assert response.status_code == 204

    def keys(
        self,
        key_type: typing.Optional[str] = None,
        sort: typing.Optional[str] = None,
        order: typing.Optional[str] = None,
    ) -> typing.List["Key"]:
        params = {}
        if key_type is not None:
            params["key_type"] = key_type
        if sort is not None:
            params["sort"] = sort
        if order is not None:
            params["order"] = order
        response = self.client.http.get(
            f"{self.client.api_endpoint}/project/{self.id}/keys", params=params
        )
        assert response.status_code == 200
        return [Key(**data, client=self.client) for data in response.json()]

    def create_key(
        self,
        name: str,
        key_type: str,
        override_secret: bool = False,
        login_password: typing.Optional[typing.Tuple[str, str]] = None,
        ssh: typing.Optional[typing.Tuple[str, str, str]] = None,
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
                "project_id": self.id,
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
                "project_id": self.id,
                "name": name,
                "type": key_type,
                "override_secret": override_secret,
                "login_password": {
                    "login": login_password[0],
                    "password": login_password[1],
                },
                "ssh": {"login": "", "passphrase": "", "private_key": ""},
            }
        response = self.client.http.post(
            f"{self.client.api_endpoint}/project/{self.id}/keys", json=json_data
        )
        assert response.status_code == 204

        try:
            return Key(**response.json(), client=self.client)
        except ValueError:
            # Sporadically, the response is an empty string. Get the actual key from the API
            return [key for key in self.keys() if key.name == name][0]

    def repositories(self) -> typing.List["Repository"]:
        response = self.client.http.get(
            f"{self.client.api_endpoint}/project/{self.id}/repositories"
        )
        assert response.status_code == 200
        return [Repository(**data, client=self.client) for data in response.json()]

    def create_repository(
        self, name: str, git_url: str, git_branch: str, ssh_key_id: int
    ) -> "Repository":
        response = self.client.http.post(
            f"{self.client.api_endpoint}/project/{self.id}/repositories",
            json={
                "name": name,
                "project_id": self.id,
                "git_url": git_url,
                "git_branch": git_branch,
                "ssh_key_id": ssh_key_id,
            },
        )
        assert response.status_code == 204
        try:
            return Repository(**response.json(), client=self.client)
        except ValueError:
            return [repo for repo in self.repositories() if repo.name == name][0]

    def environments(self) -> typing.List["Environment"]:
        response = self.client.http.get(
            f"{self.client.api_endpoint}/project/{self.id}/environment"
        )
        assert response.status_code == 200
        return [Environment(**data, client=self.client) for data in response.json()]

    def create_environment(
        self,
        name: str,
        password: str,
        json: str,
        env: str,
        secrets: typing.List[typing.Dict[typing.Any, typing.Any]],
    ) -> "Environment":
        response = self.client.http.post(
            f"{self.url}/environment",
            json={
                "name": name,
                "project_id": self.id,
                "password": None,
                "json": json,
                "env": env,
                "secrets": secrets,
            },
        )
        assert response.status_code == 204
        try:
            return Environment(**response.json(), client=self.client)
        except ValueError:
            return [env for env in self.environments() if env.name == name][0]

    def views(self) -> typing.List["View"]:
        response = self.client.http.get(f"{self.url}/views")
        assert response.status_code == 200
        return [View(**data, client=self.client) for data in response.json()]

    def create_view(self, title: str, position: int) -> "View":
        response = self.client.http.post(
            f"{self.url}/views",
            json={"position": position, "title": title, "project_id": self.id},
        )
        assert response.status_code == 201
        return View(**response.json(), client=self.client)

    def inventories(self) -> typing.List["Inventory"]:
        response = self.client.http.get(f"{self.url}/inventory")
        assert response.status_code == 200
        return [Inventory(**data, client=self.client) for data in response.json()]

    def create_inventory(
        self,
        name: str,
        inventory: str,
        ssh_key_id: int,
        become_key_id: int,
        type: str,
        repository_id: int,
    ) -> "Inventory":
        response = self.client.http.post(
            f"{self.url}/inventory",
            json={
                "id": 0,
                "name": name,
                "project_id": self.id,
                "inventory": inventory,
                "ssh_key_id": ssh_key_id,
                "become_key_id": become_key_id,
                "type": type,
                "repository_id": repository_id,
            },
        )
        assert response.status_code == 201
        return Inventory(**response.json(), client=self.client)

    def templates(self) -> typing.List["Template"]:
        response = self.client.http.get(f"{self.url}/templates")
        assert response.status_code == 200
        templates: typing.List["Template"] = []
        for template in response.json():
            if template["last_task"] is not None:
                template["last_task"] = Task(
                    **template["last_task"], client=self.client
                )
            templates.append(Template(**template, client=self.client))
        return templates

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
        response = self.client.http.post(
            f"{self.url}/templates",
            json={
                "id": 0,
                "project_id": self.id,
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
        return Template(**response.json(), client=self.client)

    def schedules(self) -> typing.List["Schedule"]:
        response = self.client.http.get(f"{self.url}/schedules")
        assert response.status_code == 200
        return [
            Schedule(**schedule, client=self.client) for schedule in response.json()
        ]

    def create_schedule(
        self, template_id: int, name: str, cron_format: str, active: bool = True
    ) -> "Schedule":
        response = self.client.http.post(
            f"{self.url}/schedules",
            json={
                "id": 0,
                "project_id": self.id,
                "template_id": template_id,
                "name": name,
                "cron_format": cron_format,
                "active": active,
            },
        )
        assert response.status_code == 201
        return Schedule(**response.json(), client=self.client)

    def tasks(self) -> typing.List["Task"]:
        response = self.client.http.get(f"{self.url}/tasks")
        assert response.status_code == 200
        return [Task(**task, client=self.client) for task in response.json()]

    def get_task(self, task_id: int) -> "Task":
        response = self.client.http.get(
            f"{self.client.api_endpoint}/project/{self.id}/tasks/{task_id}"
        )
        assert response.status_code == 200
        return Task(**response.json(), client=self.client)

    def integrations(self) -> typing.List["Integration"]:
        response = self.client.http.get(
            f"{self.client.api_endpoint}/project/{self.id}/integrations"
        )
        assert response.status_code == 200
        return [Integration(**data, client=self.client) for data in response.json()]

    def create_integration(self, name: str, template_id: int) -> "Integration":
        response = self.client.http.post(
            f"{self.client.api_endpoint}/project/{self.id}integrations",
            json={"project_id": self.id, "name": name, "template_id": template_id},
        )
        assert response.status_code == 200
        return Integration(**response.json(), client=self.client)


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
class ProjectUser:
    id: int
    name: str
    username: str
    role: str

    project_id: int

    client: SemaphoreUIClient

    @property
    def url(self) -> str:
        return f"{self.client.api_endpoint}/project/{self.project_id}/users/{self.id}"


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

    @property
    def url(self) -> str:
        return f"{self.client.api_endpoint}/project/{self.project_id}/keys/{self.id}"

    def delete(self) -> None:
        response = self.client.http.delete(self.url)
        assert response.status_code == 204


@dataclass
class Repository:
    id: int
    name: str
    project_id: int
    git_url: str
    git_branch: str
    ssh_key_id: int

    client: SemaphoreUIClient

    @property
    def url(self) -> str:
        return f"{self.client.api_endpoint}/project/{self.project_id}/repositories/{self.id}"

    def delete(self) -> None:
        response = self.client.http.delete(self.url)
        assert response.status_code == 204


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

    @property
    def url(self) -> str:
        return f"{self.client.api_endpoint}/project/{self.project_id}/environment/{self.id}"

    def delete(self) -> None:
        response = self.client.http.delete(self.url)
        assert response.status_code == 204


@dataclass
class View:
    id: int
    title: str
    position: int
    project_id: int

    client: SemaphoreUIClient

    @property
    def url(self) -> str:
        return f"{self.client.api_endpoint}/project/{self.project_id}/views/{self.id}"

    def delete(self) -> None:
        response = self.client.http.delete(self.url)
        assert response.status_code == 204


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

    def url(self) -> str:
        return (
            f"{self.client.api_endpoint}/project/{self.project_id}/inventory/{self.id}"
        )

    def delete(self) -> None:
        response = self.client.http.delete(
            f"{self.client.api_endpoint}/project/{self.project_id}/inventory/{self.id}"
        )
        assert response.status_code == 204


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

    @property
    def url(self) -> str:
        return (
            f"{self.client.api_endpoint}/project/{self.project_id}/templates/{self.id}"
        )

    def run(
        self,
        debug: bool = False,
        dry_run: bool = False,
        diff: bool = False,
        message: str = "",
        limit: str = "",
        environment: str = "",
    ) -> "Task":
        project = self.client.get_project(self.project_id)
        repo = [
            repo for repo in project.repositories() if repo.id == self.repository_id
        ][0]
        git_branch = repo.git_branch
        response = self.client.http.post(
            f"{self.client.api_endpoint}/project/{self.project_id}/tasks",
            json={
                "template_id": self.id,
                "debug": debug,
                "dry_run": dry_run,
                "diff": diff,
                "playbook": self.playbook,
                "environment": environment,
                "limit": limit,
                "git_branch": git_branch,
                "message": message,
            },
        )
        assert response.status_code == 201
        # The response is not quite a full task, so re-fetch it.
        project = self.client.get_project(self.project_id)
        return project.get_task(response.json()["id"])

    def delete(self) -> None:
        response = self.client.http.delete(self.url)
        assert response.status_code == 204

    def last_tasks(self, limit: typing.Optional[int] = None) -> typing.List["Task"]:
        """Get the last tasks.

        This function is _technically_ undocumented in the SemaphoreUI
        swagger doc. It was sleuthed out in the UI, so it may be
        an unstable function.
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        response = self.client.http.get(
            f"{self.url}/project/{self.project_id}/templates/{self.id}/tasks/last",
            params=params,
        )
        assert response.status_code == 200
        return [Task(**task, client=self.client) for task in response.json()]


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

    @property
    def url(self) -> str:
        return (
            f"{self.client.api_endpoint}/project/{self.project_id}/schedules/{self.id}"
        )

    def save(self) -> None:
        response = self.client.http.post(
            self.url,
            json={
                "id": self.id,
                "project_id": self.project_id,
                "template_id": self.template_id,
                "name": self.name,
                "cron_format": self.cron_format,
                "active": self.active,
            },
        )
        assert response.status_code == 201

    def delete(self) -> None:
        response = self.client.http.delete(self.url)
        assert response.status_code == 204


@dataclass
class Task:
    arguments: typing.Optional[str]
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

    client: SemaphoreUIClient

    # XXX: rockstar (7 Apr 2025) - These attributes are not always provided,
    # seemingly based on execution state? Because we aren't using `kw_only`
    # in our dataclass, the order of these attributes is important.
    build_task: typing.Optional["Task"] = field(default=None)
    tpl_alias: typing.Optional[str] = field(default=None)
    tpl_app: typing.Optional[str] = field(default=None)
    tpl_playbook: typing.Optional[str] = field(default=None)
    tpl_type: typing.Optional[str] = field(default=None)
    user_id: typing.Optional[int] = field(default=None)
    user_name: typing.Optional[str] = field(default=None)
    version: typing.Optional[str] = field(default=None)

    @property
    def url(self) -> str:
        return f"{self.client.api_endpoint}/project/{self.project_id}/tasks/{self.id}"

    def stop(self) -> None:
        response = self.client.http.post(f"{self.url}/stop")
        assert response.status_code == 204

    def delete(self) -> None:
        response = self.client.http.delete(self.url)
        assert response.status_code == 204

    def output(self) -> typing.List[str]:
        response = self.client.http.get(f"{self.url}/output")
        assert response.status_code == 200
        return [data["output"] for data in response.json()]
