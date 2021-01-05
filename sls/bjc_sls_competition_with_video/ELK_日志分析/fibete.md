filebeat.prospectors:
- input_type: log
  paths:
    - /var/log/*.log
output.kafka:
  hosts: ["localhost:9092"]
  topic: test-filetokafka
  keep_alive: 10s