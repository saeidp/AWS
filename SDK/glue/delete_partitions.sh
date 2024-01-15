# assuming 1000 partitions
aws glue get-partitions --database-name=<my-database> --table-name=<my-table> | jq -cr '[ { Values: .Partitions[].Values } ]' > partitions.json

seq 0 25 1000 | xargs -I _ bash -c "cat partitions.json | jq -c '.[_:_+25]'" | while read X; do aws glue batch-delete-partition --database-name=<my-database> --table-name=<my-table > --partitions-to-delete=$X; done