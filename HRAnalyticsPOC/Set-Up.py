# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# DBTITLE 1,HR Configuration
# HR Analytics Configuration
# This cell contains all catalog, schema, table, and volume configurations

# Unity Catalog Configuration
CATALOG_NAME = "hr_catalog"

# Schema Configuration
SCHEMA_CORE = "hr_core"
SCHEMA_OPS = "hr_ops"

# Volume Configuration
VOLUME_NAME = "hr_volume"

# Fully Qualified Names
FQN_VOLUME = f"{CATALOG_NAME}.{SCHEMA_CORE}.{VOLUME_NAME}"
VOLUME_PATH = f"/Volumes/{CATALOG_NAME}/{SCHEMA_CORE}/{VOLUME_NAME}"

# Core Tables (in hr_core schema)
TABLE_EMPLOYEES = f"{CATALOG_NAME}.{SCHEMA_CORE}.employees"
TABLE_LEAVE_BALANCES = f"{CATALOG_NAME}.{SCHEMA_CORE}.leave_balances"
TABLE_TRAINING_COMPLETIONS = f"{CATALOG_NAME}.{SCHEMA_CORE}.training_completions"

# Operational Tables (in hr_ops schema)
TABLE_LEAVE_REQUESTS = f"{CATALOG_NAME}.{SCHEMA_OPS}.leave_requests"
TABLE_HR_TICKETS = f"{CATALOG_NAME}.{SCHEMA_OPS}.hr_tickets"

# Source CSV Files
CSV_EMPLOYEES = f"{VOLUME_PATH}/employees_export_2025-01.csv"
CSV_LEAVE_BALANCES = f"{VOLUME_PATH}/leave_balances_2025-01.csv"
CSV_TRAINING_COMPLETIONS = f"{VOLUME_PATH}/training_completions_2025-01.csv"
CSV_HR_TICKETS = f"{VOLUME_PATH}/hr_helpdesk_tickets_2025-01.csv"

# Table Comments
COMMENTS = {
    "catalog": "HR Analytics catalog for employee data and operations",
    "schema_core": "Core HR data including employee records and organizational structure",
    "schema_ops": "Operational HR data including metrics and analytics",
    "volume": "Volume for storing HR files, documents, and data assets"
}

print("✓ HR Configuration loaded")
print(f"  Catalog: {CATALOG_NAME}")
print(f"  Schemas: {SCHEMA_CORE}, {SCHEMA_OPS}")
print(f"  Volume: {VOLUME_PATH}")

# COMMAND ----------

# DBTITLE 1,Create HR Catalog and Schemas
# Create the HR catalog and schemas using config values
spark.sql(f"""
CREATE CATALOG IF NOT EXISTS {CATALOG_NAME}
COMMENT '{COMMENTS['catalog']}'
""")

spark.sql(f"""
CREATE SCHEMA IF NOT EXISTS {CATALOG_NAME}.{SCHEMA_CORE}
COMMENT '{COMMENTS['schema_core']}'
""")

spark.sql(f"""
CREATE SCHEMA IF NOT EXISTS {CATALOG_NAME}.{SCHEMA_OPS}
COMMENT '{COMMENTS['schema_ops']}'
""")

print(f"Created catalog: {CATALOG_NAME}")
print(f"Created schemas: {SCHEMA_CORE}, {SCHEMA_OPS}")

# COMMAND ----------

# DBTITLE 1,Create HR Volume
# Create the hr_volume using config values
spark.sql(f"""
CREATE VOLUME IF NOT EXISTS {FQN_VOLUME}
COMMENT '{COMMENTS['volume']}'
""")

print(f"Created volume: {FQN_VOLUME}")
print(f"Volume path: {VOLUME_PATH}")

# COMMAND ----------

# DBTITLE 1,Check Volume Contents
# List files in the hr_volume using config
import os

volume_path = VOLUME_PATH

try:
    files = dbutils.fs.ls(volume_path)
    if files:
        print(f"Found {len(files)} items in the volume:")
        for file in files:
            print(f"  - {file.name} ({file.size} bytes)")
    else:
        print("Volume is empty. No files found.")
except Exception as e:
    print(f"Volume is empty or error accessing: {e}")

# COMMAND ----------

# DBTITLE 1,Create Employees Table from CSV
# Read CSV and create employees table using config
employees_df = spark.read.csv(
    CSV_EMPLOYEES,
    header=True,
    inferSchema=True
)

# Write as Delta table
employees_df.write.mode('overwrite').saveAsTable(TABLE_EMPLOYEES)

print(f"Created table {TABLE_EMPLOYEES} with {employees_df.count()} rows")
display(employees_df.limit(5))

# COMMAND ----------

# DBTITLE 1,Create Leave Balances Table from CSV
# Read CSV and create leave balances table using config
leave_df = spark.read.csv(
    CSV_LEAVE_BALANCES,
    header=True,
    inferSchema=True
)

# Write as Delta table
leave_df.write.mode('overwrite').saveAsTable(TABLE_LEAVE_BALANCES)

print(f"Created table {TABLE_LEAVE_BALANCES} with {leave_df.count()} rows")
display(leave_df.limit(5))

# COMMAND ----------

# DBTITLE 1,Create Training Completions Table from CSV
# Read CSV and create training completions table using config
training_df = spark.read.csv(
    CSV_TRAINING_COMPLETIONS,
    header=True,
    inferSchema=True
)

# Write as Delta table
training_df.write.mode('overwrite').saveAsTable(TABLE_TRAINING_COMPLETIONS)

print(f"Created table {TABLE_TRAINING_COMPLETIONS} with {training_df.count()} rows")
display(training_df.limit(5))

# COMMAND ----------

# DBTITLE 1,Create Leave Requests Table
# Create leave_requests table using config
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {TABLE_LEAVE_REQUESTS}
(
    request_id STRING,
    employee_id STRING,
    start_date DATE,
    end_date DATE,
    days_requested DOUBLE,
    request_reason STRING,
    request_status STRING,
    submitted_timestamp TIMESTAMP,
    approved_by STRING,
    approval_timestamp TIMESTAMP
)
""")

print(f"Created table: {TABLE_LEAVE_REQUESTS}")

# COMMAND ----------

# DBTITLE 1,Create HR Tickets Table
# Create hr_tickets table using config
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {TABLE_HR_TICKETS}
(
    ticket_id STRING,
    employee_id STRING,
    category STRING,
    priority STRING,
    description STRING,
    status STRING,
    created_timestamp TIMESTAMP,
    assigned_to STRING,
    resolved_timestamp TIMESTAMP
)
""")

print(f"Created table: {TABLE_HR_TICKETS}")

# COMMAND ----------

# DBTITLE 1,Load HR Tickets Data from CSV
# Read CSV and check schema first using config
tickets_df = spark.read.csv(
    CSV_HR_TICKETS,
    header=True,
    inferSchema=True
)

print("CSV Schema:")
tickets_df.printSchema()
print(f"\nTotal rows: {tickets_df.count()}")
print("\nSample data:")
display(tickets_df.limit(5))

# COMMAND ----------

# DBTITLE 1,Insert Mapped Data into HR Tickets Table
# Map CSV columns to hr_tickets table schema
from pyspark.sql.functions import col

mapped_tickets_df = tickets_df.select(
    col('ticket_id'),
    col('requester_id').alias('employee_id'),
    col('category'),
    col('priority'),
    col('description'),
    col('status'),
    col('opened_at').alias('created_timestamp'),
    col('assignee_id').alias('assigned_to'),
    col('closed_at').alias('resolved_timestamp')
)

# Insert data into the hr_tickets table using config
mapped_tickets_df.write.mode('append').saveAsTable(TABLE_HR_TICKETS)

print(f"Successfully inserted {mapped_tickets_df.count()} rows into {TABLE_HR_TICKETS}")
print("\nSample inserted data:")
display(spark.table(TABLE_HR_TICKETS).limit(5))