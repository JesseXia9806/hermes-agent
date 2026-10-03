---
name: postgresql-fdw-cross-db
description: Use when querying or moving data between Postgres databases.
tags:
  - postgresql
  - database
  - fdw
  - cross-database
---

# PostgreSQL FDW (Foreign Data Wrapper) Setup

Use when: You need to query, join, or aggregate data across two different PostgreSQL databases natively, without relying on slow external Python/script-based ETL loops.

Often used when one database hosts raw streaming data (ODS) and another hosts the structured data warehouse (DW), and you need to bulk-aggregate between them.

## Setup Recipe

```sql
-- 1. Enable the extension in the TARGET database
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- 2. Create the server link pointing to the SOURCE database
DROP SERVER IF EXISTS source_server CASCADE;
CREATE SERVER source_server 
  FOREIGN DATA WRAPPER postgres_fdw 
  OPTIONS (host '127.0.0.1', dbname 'source_db_name', port '5432');

-- 3. Map the local user to the remote user credentials
CREATE USER MAPPING FOR current_user_or_postgres 
  SERVER source_server 
  OPTIONS (user 'remote_username', password 'remote_password');

-- 4. Create Foreign Table matching the remote schema
CREATE FOREIGN TABLE ext_raw_data (
    id BIGINT,
    created_at TIMESTAMP,
    status VARCHAR
) SERVER source_server OPTIONS (schema_name 'public', table_name 'remote_table_name');
```

## Pitfalls
- Foreign tables do not carry over indexes locally, but PostgreSQL pushes down `WHERE` clauses to the remote server. Ensure filtering happens remotely.
- Using FDW combined with `INSERT INTO ... SELECT ... ON CONFLICT DO UPDATE` is dramatically faster and safer than moving millions of rows through Python arrays or `psycopg2.executemany()`.