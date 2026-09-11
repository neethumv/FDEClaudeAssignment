# Claude Code Assignment - HR Analytics Platform

## Overview
This project demonstrates key Claude Code capabilities using a Databricks-based HR Analytics Platform built with Unity Catalog, Delta Tables, Volumes, and HR datasets.

## Scenarios Implemented

### 1. Repeatable Workflow
Created a reusable `/code_review` slash command to perform structured code reviews covering:
- Code quality
- Naming conventions
- Error handling
- Logging
- Security
- Test coverage

### 2. Context Management with Subagents
Used subagents to investigate repository-wide references of `SCHEMA_OPS`, enabling efficient analysis without overloading the main context.

### 3. Packaging a Skill
Developed a reusable **HR Data Onboarding** skill that automates:
- File validation
- Schema validation
- Delta table creation
- Data loading
- Data quality checks

### 4. Standards Enforcement
Implemented repository-level coding standards through `CLAUDE.md`, including:
- Consistent naming conventions
- Mandatory error handling
- Standardized logging practices

### 5. Agentic Workflow
Applied a structured debugging workflow:
1. Reproduce
2. Diagnose
3. Fix
4. Verify

### 6. MCP Integration
Evaluated MCP capabilities for live data access. Configured a GitHub MCP server and validated repository-based queries.

## Key Learnings
- Slash commands improve workflow consistency.
- Subagents simplify large-scale investigations.
- Skills enable reusable operational processes.
- `CLAUDE.md` enforces coding standards.
- Agentic workflows improve debugging quality.
- MCP provides real-time data grounding.

## Conclusion
This assignment successfully demonstrates workflow automation, skill creation, standards enforcement, agentic debugging, and MCP integration using Claude Code within an HR Analytics platform.
