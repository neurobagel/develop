<div align="center">

# Federation API

[![Main branch check status](https://img.shields.io/github/check-runs/neurobagel/federation-api/main?style=flat-square)](https://github.com/neurobagel/federation-api/actions?query=branch:main)
[![Tests status](https://img.shields.io/github/actions/workflow/status/neurobagel/federation-api/test.yaml?branch=main&style=flat-square&label=tests&link=https%3A%2F%2Fgithub.com%2Fneurobagel%2Ffederation-api%2Factions%2Fworkflows%2Ftest.yaml)](https://github.com/neurobagel/federation-api/actions/workflows/test.yaml)
[![Codecov](https://img.shields.io/codecov/c/github/neurobagel/federation-api?token=B827PI9W1U&style=flat-square&logo=codecov&link=https%3A%2F%2Fcodecov.io%2Fgh%2Fneurobagel%2Ffederation-api)](https://app.codecov.io/gh/neurobagel/federation-api)
[![Python versions static](https://img.shields.io/badge/python-3.10-blue?style=flat-square&logo=python)](https://www.python.org)
[![License](https://img.shields.io/github/license/neurobagel/federation-api?style=flat-square&color=purple&link=LICENSE)](LICENSE)
[![Docker Image Version (tag)](https://img.shields.io/docker/v/neurobagel/federation_api/latest?style=flat-square&logo=docker&link=https%3A%2F%2Fhub.docker.com%2Fr%2Fneurobagel%2Ffederation_api%2Ftags)](https://hub.docker.com/r/neurobagel/federation_api/tags)
[![Docker Pulls](https://img.shields.io/docker/pulls/neurobagel/federation_api?style=flat-square&logo=docker&link=https%3A%2F%2Fhub.docker.com%2Fr%2Fneurobagel%2Ffederation_api%2Ftags)](https://hub.docker.com/r/neurobagel/federation_api/tags)

</div>

Please refer to our [**official documentation**](https://neurobagel.org/user_guide/api/) for more information on Neurobagel federation and how to [deploy your own federation API](https://neurobagel.org/user_guide/getting_started/).

## Launching the API
### 1. Set the local Neurobagel nodes to federate over
Create a configuration JSON file called `local_nb_nodes.json` containing the URLs and (arbitrary) names of the local nodes you wish to federate over.
Each node must be denoted by a dictionary `{}` with two key-value pairs: `"NodeName"` for the name of the node, and `"ApiURL"` for the url of the API exposed for that node. 
Multiple nodes must be wrapped in a list `[]`.

For a template `local_nb_nodes.json` file that you can clone and edit, 
see the [neurobagel/recipes](https://github.com/neurobagel/recipes/tree/main/local_federation) repo.

Examples:  

`local_nb_nodes.json` with one local node API running on `http://localhost:8000`
```json
{
    "NodeName": "Local graph",
    "ApiURL": "http://host.docker.internal:8000"
}
```
_**NOTE:** If the local node API(s) you are federating over is running on the same host machine as the federation API 
(e.g., the URL to access the node API is `http://localhost:XXXX`), 
in `local_nb_nodes.json` you **must** replace `localhost` with `host.docker.internal` in the corresponding `"ApiURL"`, 
as shown above (for more information, see the [Docker documentation](https://docs.docker.com/engine/reference/commandline/run/#add-host))._

`local_nb_nodes.json` with two local nodes
```json
[
    {
        "NodeName": "Local graph 1",
        "ApiURL": "http://host.docker.internal:8000"
    },
    {
        "NodeName": "Local graph 2",
        "ApiURL": "http://192.168.0.1"
    }
]
```

### 2. Run the Docker container
```bash
docker pull neurobagel/federation_api

# Run this next command in the same directory where your `local_nb_nodes.json` file is located
docker run -d -v ${PWD}/local_nb_nodes.json:/usr/src/local_nb_nodes.json:ro \
    --add-host=host.docker.internal:host-gateway \
    --name=federation -p 8080:8000 neurobagel/federation_api
```
NOTE: You can replace the port number `8080` for the `-p` flag with any port on the host you wish to use for the API.
