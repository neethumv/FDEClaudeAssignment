# HR Analytics - HR Ticket Record Validator
# Validates a DataFrame of HR ticket records against data-quality rules before
# they are loaded into the hr_tickets Delta table.
# Follows the hr-data-onboarding "Validate" steps: schema, null values, duplicate keys,
# plus domain checks on priority, status, and resolution timestamps.

import logging

from pyspark.sql import functions as F

import hr_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Module Constants
TARGET_TABLE = hr_config.TABLE_HR_TICKETS
KEY_COLUMN = hr_config.HR_TICKETS_KEY_COLUMN
REQUIRED_COLUMNS = hr_config.HR_TICKETS_REQUIRED_COLUMNS
NOT_NULL_COLUMNS = hr_config.HR_TICKETS_NOT_NULL_COLUMNS
ALLOWED_PRIORITIES = hr_config.HR_TICKETS_ALLOWED_PRIORITIES
ALLOWED_STATUSES = hr_config.HR_TICKETS_ALLOWED_STATUSES
CLOSED_STATUSES = hr_config.HR_TICKETS_CLOSED_STATUSES


def _check_required_columns(tickets_df, issues):
    """Confirm every required column is present in the DataFrame."""
    missing_columns = [name for name in REQUIRED_COLUMNS if name not in tickets_df.columns]
    if missing_columns:
        message = f"Missing required columns: {missing_columns}"
        logger.error(message)
        issues.append(message)
    return missing_columns


def _check_not_null(tickets_df, issues):
    """Flag any not-null column that contains null or empty values."""
    for column_name in NOT_NULL_COLUMNS:
        if column_name not in tickets_df.columns:
            continue
        try:
            null_count = tickets_df.filter(
                F.col(column_name).isNull() | (F.trim(F.col(column_name).cast("string")) == "")
            ).count()
        except Exception as null_check_error:
            logger.error("Failed null check on column %s: %s", column_name, null_check_error)
            raise
        if null_count > 0:
            message = f"Column '{column_name}' has {null_count} null or empty values"
            logger.error(message)
            issues.append(message)


def _check_duplicate_keys(tickets_df, issues):
    """Flag duplicate ticket_id values.

    Null keys are excluded here so that missing 'ticket_id' values are reported only
    by the not-null check; Spark collapses all nulls into a single distinct value,
    which would otherwise be miscounted as duplicates.
    """
    if KEY_COLUMN not in tickets_df.columns:
        return
    try:
        keyed_df = tickets_df.filter(F.col(KEY_COLUMN).isNotNull())
        non_null_count = keyed_df.count()
        distinct_count = keyed_df.select(KEY_COLUMN).distinct().count()
    except Exception as duplicate_check_error:
        logger.error("Failed duplicate-key check on %s: %s", KEY_COLUMN, duplicate_check_error)
        raise
    duplicate_count = non_null_count - distinct_count
    if duplicate_count > 0:
        message = f"Found {duplicate_count} duplicate '{KEY_COLUMN}' values"
        logger.error(message)
        issues.append(message)


def _check_allowed_values(tickets_df, column_name, allowed_values, issues):
    """Flag rows whose column value is outside the allowed set (case-insensitive)."""
    if column_name not in tickets_df.columns:
        return
    lowered_allowed = [value.lower() for value in allowed_values]
    try:
        invalid_count = tickets_df.filter(
            F.col(column_name).isNotNull()
            & ~F.lower(F.trim(F.col(column_name))).isin(lowered_allowed)
        ).count()
    except Exception as allowed_check_error:
        logger.error(
            "Failed allowed-value check on column %s: %s", column_name, allowed_check_error
        )
        raise
    if invalid_count > 0:
        message = (
            f"Column '{column_name}' has {invalid_count} values outside allowed set {allowed_values}"
        )
        logger.error(message)
        issues.append(message)


def _check_resolution_timestamps(tickets_df, issues):
    """Closed/resolved tickets must have a resolved_timestamp not earlier than created."""
    columns = tickets_df.columns
    if "status" not in columns or "resolved_timestamp" not in columns:
        return
    lowered_closed = [value.lower() for value in CLOSED_STATUSES]
    try:
        missing_resolution_count = tickets_df.filter(
            F.lower(F.trim(F.col("status"))).isin(lowered_closed)
            & F.col("resolved_timestamp").isNull()
        ).count()

        negative_duration_count = 0
        if "created_timestamp" in columns:
            negative_duration_count = tickets_df.filter(
                F.col("resolved_timestamp").isNotNull()
                & F.col("created_timestamp").isNotNull()
                & (F.col("resolved_timestamp") < F.col("created_timestamp"))
            ).count()
    except Exception as timestamp_check_error:
        logger.error("Failed resolution-timestamp check: %s", timestamp_check_error)
        raise

    if missing_resolution_count > 0:
        message = (
            f"{missing_resolution_count} tickets in a closed status are missing 'resolved_timestamp'"
        )
        logger.error(message)
        issues.append(message)
    if negative_duration_count > 0:
        message = (
            f"{negative_duration_count} tickets have 'resolved_timestamp' earlier than "
            "'created_timestamp'"
        )
        logger.error(message)
        issues.append(message)


def validate_hr_tickets(tickets_df, raise_on_error=True):
    """Validate HR ticket records against data-quality rules before loading.

    Args:
        tickets_df: Spark DataFrame of HR ticket records mapped to the hr_tickets schema.
        raise_on_error: When True, raise ValueError if any validation issue is found.

    Returns:
        dict with keys 'is_valid', 'record_count', 'missing_columns' (list of
        absent required columns), and 'issues' (list of messages).

    Raises:
        ValueError: When raise_on_error is True and one or more issues are found.
    """
    logger.info("Validating HR ticket records for load into %s", TARGET_TABLE)

    try:
        record_count = tickets_df.count()
    except Exception as count_error:
        logger.error("Failed to count HR ticket records: %s", count_error)
        raise

    issues = []
    if record_count == 0:
        message = "HR ticket DataFrame contains no records"
        logger.error(message)
        issues.append(message)

    missing_columns = _check_required_columns(tickets_df, issues)
    if not missing_columns:
        _check_not_null(tickets_df, issues)
        _check_duplicate_keys(tickets_df, issues)
        _check_allowed_values(tickets_df, "priority", ALLOWED_PRIORITIES, issues)
        _check_allowed_values(tickets_df, "status", ALLOWED_STATUSES, issues)
        _check_resolution_timestamps(tickets_df, issues)

    is_valid = len(issues) == 0
    result = {
        "is_valid": is_valid,
        "record_count": record_count,
        "missing_columns": missing_columns,
        "issues": issues,
    }

    if is_valid:
        logger.info("HR ticket validation passed: %s records", record_count)
    else:
        logger.error("HR ticket validation failed with %s issue(s): %s", len(issues), issues)
        if raise_on_error:
            raise ValueError(f"HR ticket validation failed: {issues}")

    return result
