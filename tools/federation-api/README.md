<div align="center">

# Federation API

[![Coverage Status](https://coveralls.io/repos/github/neurobagel/federation-api/badge.svg?branch=main)](https://coveralls.io/github/neurobagel/federation-api?branch=main)

</div>

Please refer to our [**official documentation**](https://neurobagel.org/overview/) for more information on how to use the federation API.

## Launching the API
### 1. Set the Neurobagel nodes to federate over
Create a `fed.env` file with the variable `LOCAL_NB_NODES` containing the URLs and (arbitrary) names of the nodes to be federated over. 
Each node should be wrapped in brackets `()`, with the URL and name of the node (in that order) separated by a comma.
The variable must be an **unquoted** string.

This repo contains a [template `fed.env`](/fed.env) file that you can edit.

e.g.,
```bash
LOCAL_NB_NODES=(https://myfirstnode.org/,First Node)(https://mysecondnode.org/,Second Node)
```

### 2. Run the Docker container
```bash
docker pull neurobagel/federation_api

# Make sure to run the next command in the same directory where your .env file is
docker run -d --name=federation -p 8080:8000 --env-file=fed.env neurobagel/federation_api
```
NOTE: You can replace the port number `8080` for the `-p` flag with any port on the host you wish to use for the API.
