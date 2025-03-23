```
pip install snowflake-connector-python pyyaml argparse
```

```
cp snowflake_config-templ.yaml snowflake_config.yaml
vi  snowflake_config.yaml
```

```
./snowflake2sqlite.py SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER customer.ddl
./snowflake2csv.py SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER customer.csv
```

```
sqlite3 sample.db
.read customer.ddl
.separator ,
.import --skip 1 customer.csv customer
```
