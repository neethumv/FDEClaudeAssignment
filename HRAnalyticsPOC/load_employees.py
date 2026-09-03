# HR Analytics - Employee CSV Loader
# Loads a new employee CSV export from the HR volume into the employees Delta table.
# Follows the hr-data-onboarding process: validate source, ensure target, load, validate load.

import logging

import hr_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Module Constants
DEFAULT_CSV_PATH = hr_config.CSV_EMPLOYEES
TARGET_TABLE = hr_config.TABLE_EMPLOYEES
KEY_COLUMN = hr_config.EMPLOYEES_KEY_COLUMN
TABLE_COMMENT = hr_config.EMPLOYEES_TABLE_COMMENT
LOAD_MODE = hr_config.EMPLOYEES_LOAD_MODE


def _read_employee_csv(spark, csv_path):
    """Read the employee CSV file from the volume with an inferred schema."""
    try:
        employees_df = spark.read.csv(csv_path, header=True, inferSchema=True)
    except Exception as read_error:
        logger.error("Failed to read employee CSV at %s: %s", csv_path, read_error)
        raise

    if len(employees_df.columns) == 0:
        message = f"No columns inferred from CSV at {csv_path}; header row may be missing"
        logger.error(message)
        raise ValueError(message)

    if KEY_COLUMN not in employees_df.columns:
        message = f"Required key column '{KEY_COLUMN}' not found in CSV at {csv_path}"
        logger.error(message)
        raise ValueError(message)

    return employees_df


def _validate_source_data(employees_df, csv_path):
    """Validate record count, null keys, and duplicate keys before loading."""
    try:
        record_count = employees_df.count()
        null_key_count = employees_df.filter(employees_df[KEY_COLUMN].isNull()).count()
        distinct_key_count = employees_df.select(KEY_COLUMN).distinct().count()
    except Exception as validation_error:
        logger.error("Failed to validate source data from %s: %s", csv_path, validation_error)
        raise

    if record_count == 0:
        message = f"Employee CSV at {csv_path} contains no data rows"
        logger.error(message)
        raise ValueError(message)

    if null_key_count > 0:
        message = f"Employee CSV at {csv_path} has {null_key_count} rows with a null '{KEY_COLUMN}'"
        logger.error(message)
        raise ValueError(message)

    duplicate_key_count = record_count - distinct_key_count
    if duplicate_key_count > 0:
        message = f"Employee CSV at {csv_path} has {duplicate_key_count} duplicate '{KEY_COLUMN}' values"
        logger.error(message)
        raise ValueError(message)

    logger.info("Source validation passed for %s: %s records", csv_path, record_count)
    return record_count


def _ensure_target_table(spark, employees_df):
    """Create the employees Delta table from the source schema if it does not exist."""
    try:
        table_exists = spark.catalog.tableExists(TARGET_TABLE)
        if not table_exists:
            logger.info("Target table %s not found; creating it", TARGET_TABLE)
            empty_df = spark.createDataFrame([], employees_df.schema)
            empty_df.write.format("delta").saveAsTable(TARGET_TABLE)
            spark.sql(f"COMMENT ON TABLE {TARGET_TABLE} IS '{TABLE_COMMENT}'")
            logger.info("Created target table %s", TARGET_TABLE)
        else:
            logger.info("Target table %s already exists", TARGET_TABLE)
    except Exception as create_error:
        logger.error("Failed to ensure target table %s: %s", TARGET_TABLE, create_error)
        raise


def _write_to_table(employees_df):
    """Write the validated employee DataFrame to the target Delta table."""
    try:
        employees_df.write.format("delta").mode(LOAD_MODE).option(
            "mergeSchema", "true"
        ).saveAsTable(TARGET_TABLE)
    except Exception as write_error:
        logger.error("Failed to write employee data to %s: %s", TARGET_TABLE, write_error)
        raise


def _validate_load(spark, expected_new_records):
    """Confirm the load by checking the resulting row count in the target table."""
    try:
        total_row_count = spark.table(TARGET_TABLE).count()
    except Exception as post_load_error:
        logger.error("Failed to validate load for %s: %s", TARGET_TABLE, post_load_error)
        raise

    logger.info(
        "Load validation for %s: %s new records written, %s total rows in table",
        TARGET_TABLE,
        expected_new_records,
        total_row_count,
    )
    return total_row_count


def load_employee_csv(spark, csv_path=DEFAULT_CSV_PATH):
    """Load a new employee CSV file from the HR volume into the employees Delta table.

    Args:
        spark: Active SparkSession.
        csv_path: Fully qualified volume path to the employee CSV export.
            Defaults to the configured employees export path.

    Returns:
        dict with the source record count and the resulting table row count.
    """
    logger.info("Starting employee CSV load from %s into %s", csv_path, TARGET_TABLE)

    employees_df = _read_employee_csv(spark, csv_path)
    source_record_count = _validate_source_data(employees_df, csv_path)
    _ensure_target_table(spark, employees_df)
    _write_to_table(employees_df)
    total_row_count = _validate_load(spark, source_record_count)

    logger.info("Completed employee CSV load from %s", csv_path)
    return {
        "csv_path": csv_path,
        "target_table": TARGET_TABLE,
        "source_record_count": source_record_count,
        "table_row_count": total_row_count,
    }
