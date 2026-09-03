# HR Analytics Configuration
# This file contains all catalog, schema, table, and volume configurations

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

# Employees Table Load Configuration
EMPLOYEES_KEY_COLUMN = "employee_id"
EMPLOYEES_TABLE_COMMENT = "Core employee master records onboarded from HR CSV exports"
EMPLOYEES_LOAD_MODE = "append"

# HR Tickets Validation Configuration
HR_TICKETS_KEY_COLUMN = "ticket_id"
HR_TICKETS_REQUIRED_COLUMNS = [
    "ticket_id",
    "employee_id",
    "category",
    "priority",
    "status",
    "created_timestamp",
]
HR_TICKETS_NOT_NULL_COLUMNS = [
    "ticket_id",
    "employee_id",
    "category",
    "priority",
    "status",
    "created_timestamp",
]
HR_TICKETS_ALLOWED_PRIORITIES = ["low", "medium", "high", "critical"]
HR_TICKETS_ALLOWED_STATUSES = ["open", "in_progress", "on_hold", "resolved", "closed"]
HR_TICKETS_CLOSED_STATUSES = ["resolved", "closed"]
