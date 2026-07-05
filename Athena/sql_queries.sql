CREATE DATABASE karan_website_analytics;

CREATE EXTERNAL TABLE karan_website_logs (
 Ɵmestamp STRING,
 user_id STRING,
 page STRING,
 country STRING,
 device STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
LOCATION 's3://website-log-data-2026/raw-logs/';
