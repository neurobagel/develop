# The following script sets up two test nodes,
# Test node 1: 2 OpenNeuro datasets, in the aggregate results mode
# Test node 2: the (default) BIDS Synthetic dataset, in the unaggregated results mode
#
# A full_stack deployment recipe will be used for Test node 1 to provide local federation.

mkdir test_node1 test_node2 api-responses

# SETUP FOR TEST NODE 1
git clone https://github.com/neurobagel/recipes.git test_node1/recipes

# Get the data
git clone https://github.com/neurobagel/openneuro-annotations.git test_node1/openneuro-annotations
mkdir test_node1/openneuro_mini_data
cp test_node1/openneuro-annotations/ds000001.jsonld test_node1/recipes/ds000002.jsonld test_node1/openneuro_mini_data

cd test_node1/recipes
cp template.env .env

sed -i 's/^LOCAL_GRAPH_DATA=.*/LOCAL_GRAPH_DATA=../openneuro_mini_data/' .env
sed -i 's/^NB_FEDERATE_REMOTE_PUBLIC_NODES=.*/NB_FEDERATE_REMOTE_PUBLIC_NODES=False/' .env
sed -i 's/^NB_API_QUERY_URL=.*/NB_API_QUERY_URL=http://localhost:8080/' .env
sed -i 's/^COMPOSE_PROFILES=.*/COMPOSE_PROFILES=full_stack/' .env

# Use full container names to avoid conflicts
echo '[{"NodeName": "2 OpenNeuro Datasets", "ApiURL": "http://neurobagel_node-api-1:8000"},{"NodeName": "BIDS Synthetic", "ApiURL": "http://neurobagel_node2-api-1:8000"}]' > local_nb_nodes.json

# Generate a partial success result (since Test node 2 isn't up yet)
docker compose up -d

# WAIT FOR GRAPH TO FINISH BEING SET UP (?)
while ! curl --silent "localhost:7200/rest/repositories" -u "DBUSER:DBPASSWORD" | grep '\['; do
    :
done

# Query for female sex in f-API
curl -s http://localhost:8080/query?sex=snomed:248152002 | jq .  > api-responses/fapi_query_partial_success_207.json

# Generate a fail result (both nodes are not accessible)
docker stop neurobagel_node-api-1
curl -s http://localhost:8080/query?sex=snomed:248152002 | jq .  > api-responses/fapi_query_fail_207.json

cd ../..

# SETUP FOR TEST NODE 2
git clone https://github.com/neurobagel/recipes.git test_node2/recipes
cd test_node2/recipes
cp template.env .env

sed -i 's/^COMPOSE_PROJECT_NAME=.*/COMPOSE_PROJECT_NAME=neurobagel_node2/' .env
sed -i 's/^NB_GRAPH_PORT_HOST=.*/NB_GRAPH_PORT_HOST=7201/' .env
sed -i 's/^NB_NAPI_PORT_HOST=.*/NB_NAPI_PORT_HOST=8001/' .env

# Generate a full success result (both nodes are running and accessible)
# First, restart n-API for test node 1
docker start neurobagel_node-api-1
docker compose up -d
# Add second n-API to the network of the first node, so that the f-API can access the second n-API by container name
docker network add neurobagel_node_default neurobagel_node2-api-1
curl -s http://localhost:8080/query?sex=snomed:248152002 | jq .  > api-responses/fapi_query_success_207.json


# Generate query response where results are protected (test node 1)
curl -s http://localhost:8000/query?sex=snomed:248152002 | jq . > api-responses/napi_query_aggregated_results.json
# Generate query response where results are open (test node 2)
curl -s http://localhost:8001/query?sex=snomed:248152002 | jq . > api-responses/napi_query_unaggregated_results.json
