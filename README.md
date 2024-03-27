# Template repo for development stack

The main idea here is to have a single command that
spins up the complete development stack. 
This won't be useful directly because nothing
is set up to be locally edited. 
Instead this is meant as a template. 
So if for example you would like to develop the 
f-API repo, you would bind-mount the f-API code repo
into the f-API container and have it talk to the
two n-API services in this templates.

Additional constraints:
- ephemeral setup: every `docker compose up` is the same. No local data / all writes to the container FS. This is on purpose to keep the build clean.
- everything hardcoded in the docker-compose.yml. This is also on purpose so we don't have to manually edit a bunch of `.env` files before things can run.
- no permissions on the graph. This is laziness and should be changed.
- everything is in the repo. Also laziness, instead example data should be fetched from existing repos.
- all versions hardcoded. This is mainly laziness. It's pretty easy to change the versions - and so we could adapt this to compare different versions.
- no ability to check when all services are done building. Not yet sure how to do this well. E.g. the graphDB service takes a while to launch. Same for the query tool. So if we wanted to use this for integration tests, we first would have to check that everything is up and running.

