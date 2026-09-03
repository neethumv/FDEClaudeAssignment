# HR Analytics Development Standards

These standards apply to all generated Python and Databricks code.

## Naming Convention

- Functions must use snake_case
- Variables must use snake_case
- Constants must use UPPER_CASE

## Error Handling

- External operations must be wrapped in try/except
- Exceptions must be logged before raising
- Never silently ignore exceptions

## Logging Standards

- Do not use print()
- Use logger.info() for informational events
- Use logger.error() for failures

## Databricks Standards

- Use configuration constants instead of hardcoded table names
- Use fully qualified Unity Catalog table names