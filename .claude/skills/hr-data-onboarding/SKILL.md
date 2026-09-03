---
name: HR Data Onboarding
description: Standard process for onboarding new HR datasets into the HR Analytics  environment.
---

# Trigger Conditions

Use this skill when the user asks things like:

- Load a new HR dataset
- Onboard employee data
- Create HR tables from CSV files
- Add a new source file to the HR platform
- Prepare HR data for analytics
- Create tables from HR exports
- Validate HR ingestion process

# Process

## Step 1: Verify Configuration

Confirm:

- Catalog exists
- Schema exists
- Volume exists

Required assets:

- hr_catalog
- hr_core schema
- hr_ops schema
- hr_volume

## Step 2: Validate Source Files

Check:

- File exists in volume
- Header row present
- Schema can be inferred
- Required columns exist

## Step 3: Create Target Table

If table does not exist:

- Create Delta table
- Add comments
- Verify schema

## Step 4: Load Data

Read source CSV.

Validate:

- Record count
- Null values
- Duplicate keys

Write data to Delta table.

## Step 5: Validate Load

Check:

- Row counts
- Schema
- Sample records

## Step 6: Operational Readiness

Verify:

- Unity Catalog registration
- Table permissions
- Query accessibility

# Output Format

## Summary

## Validation Results

## Issues Found

## Recommended Next Steps