---
name: database-schema-text2sql
description: Use when designing schemas for LLM Text-to-SQL queries.
tags:
  - database
  - llm
  - sql
  - schema
  - text-to-sql
---

# Database Schema Design for Text-to-SQL (LLM)

Use when: You are asked to design, initialize, or optimize a relational database schema that an LLM (like Hermes Agent) will query using Text-to-SQL capabilities.

LLMs are excellent at writing SQL, but they struggle with performance if they generate heavy dynamic aggregation queries over hundreds of millions of rows. Their context also relies heavily on schema metadata, not just table/column names.

## Core Rules & Pitfalls

### 1. Mandatory Metadata (Comments)
- **Rule**: You MUST add `COMMENT ON TABLE` and `COMMENT ON COLUMN` for every object.
- **Why**: LLMs inject the DB catalog (schema definition) into their prompt context. Without comments, ambiguous columns (e.g., `is_rework`) confuse the AI. Explicit comments (e.g., `TRUE means re-tested after repair`) ensure accurate query generation.

### 2. Pre-Aggregated Wide Tables (Crucial for Performance)
- **Rule**: Never rely on the LLM to dynamically run `COUNT() / SUM() / GROUP BY` on raw fact tables with millions of rows (like manufacturing MES logs or access swipe logs) for routine metrics like "Daily Yield" or "Daily Attendance".
- **Action**: Always design an Aggregation/Wide Table (e.g., `agg_daily_attendance` or `agg_daily_yield`). Have the backend ETL hydrate this table, and instruct the LLM to query *this* table for business questions. This guarantees millisecond responses instead of query timeouts.

### 3. Declarative Partitioning
- **Rule**: For raw data ingestion tables (Fact Tables), use native database declarative partitioning (e.g., PostgreSQL `PARTITION BY RANGE (created_at)`).
- **Why**: Ensures that when the LLM generates a filter for "today's data", the database engine prunes partitions and scans instantly, avoiding full-table scans that hang the connection.

### Example Architecture
```sql
-- 1. Dimension Tables
CREATE TABLE dim_employee (emp_id VARCHAR PRIMARY KEY, name VARCHAR);
COMMENT ON COLUMN dim_employee.emp_id IS 'Unique employee identifier';

-- 2. Fact Tables (Partitioned)
CREATE TABLE fact_log (id BIGSERIAL, emp_id VARCHAR, created_at TIMESTAMP) PARTITION BY RANGE (created_at);
COMMENT ON TABLE fact_log IS 'Massive raw logs';

-- 3. Pre-Aggregated Tables for AI
CREATE TABLE agg_daily_status (emp_id VARCHAR, work_date DATE, status VARCHAR);
COMMENT ON TABLE agg_daily_status IS 'Query this table for daily status instead of fact_log';
```