<div align="center">

# Federation API

[![Coverage Status](https://coveralls.io/repos/github/neurobagel/federation-api/badge.svg?branch=main)](https://coveralls.io/github/neurobagel/federation-api?branch=main)

</div>

Please refer to our [**official documentation**](https://neurobagel.org/overview/) for more information on how to use the federation API.

## Launching the API
### 1. Set the Neurobagel nodes to federate over
Create an `.env` file with the variable `NB_NODES` set to the URLs of the nodes to be federated over. 
The URLs should be stored as a **space-separated, unquoted** string.

e.g.,
```bash
NB_NODES=https://myfirstnode.org/ https://mysecondnode.org/
```

### 2. Run the Docker container
```bash
docker pull neurobagel/federation_api

# Make sure to run the next command in the same directory where your .env file is
docker run -d --name=federation -p 8080:8000 --env-file=.env neurobagel/federation_api
```
NOTE: You can replace the port number `8080` for the `-p` flag with any port on the host you wish to use for the API.
