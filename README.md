# postgres-log-bind-params-filler
Matches parameterized SQL queries from the PostgreSQL server log with real bind values for direct query execution

# Limitations

Currently only tested with logfiles having `log_line_prefix = '%m-%c-'`