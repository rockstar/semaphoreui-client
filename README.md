A python client for SemaphoreUI
==

This library provides an api client for the SemaphoreUI api. Its purpose is to provide an ergonomic and python interface, both in api and behavior.

To install,

```shell
$ pip install semaphoreui-client
```

To use,

```python
from semaphoreui_client import Client

client = Client("https://path.to/your/semaphore")
client.login("username", "myPassW0rd")

for project in client.projects():
    print(project.name)
```

This library is being used in production environments, but is still early in its development. As such, caution should be exercised when using this library--its api is still heavily in flux.