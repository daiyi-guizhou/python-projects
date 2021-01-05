
```es_jar.md
#kafka
bootstrap.servers=hostname:port
group.id=test-group-id
enable.auto.commit=false
auto.offset.reset=earliest
#For multiple topics, separate with ,
topics=test-3

#ES
index=test_index_01
hostname=localhost
port=9200
#support json and single line text
type=json

```


`java -jar kafkaToEs-1.0-SNAPSHOT.jar es_jar.md`

143 149 150`