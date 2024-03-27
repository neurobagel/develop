#!/bin/bash

# TODO: Set up a user and so on

 # Launch graphdb in the background
/opt/graphdb/dist/bin/graphdb -Dgraphdb.home=/opt/graphdb/home &
GRAPHDB_PID=$!

while ! curl --silent "localhost:7200/rest/repositories" | grep '\[\]'; do
    :
done

# Make templates for the two databases
sed 's/my_db/db1/g' /opt/data-config_template.ttl > ./db1.ttl
sed 's/my_db/db2/g' /opt/data-config_template.ttl > ./db2.ttl

echo "Setting up the databases now"
curl -X PUT --silent localhost:7200/repositories/db1 --data-binary "@db1.ttl" -H "Content-Type: application/x-turtle"
curl -X PUT --silent localhost:7200/repositories/db2 --data-binary "@db2.ttl" -H "Content-Type: application/x-turtle"


while ! curl --silent "localhost:7200/rest/repositories" | grep -e "db1" -e "db2"; do
    :
done

# Upload the data
for file in /data/*.jsonld;
do
    echo "Uploading $file"
    curl --silent -X POST -H "Content-Type: application/ld+json" --data-binary "@$file"  localhost:7200/repositories/db1/statements
    curl --silent -X POST -H "Content-Type: application/ld+json" --data-binary "@$file"  localhost:7200/repositories/db2/statements
done

# We don't have jobcontrol here, so can't bring graphdb back to foreground
# instead we'll wait
wait $GRAPHDB_PID