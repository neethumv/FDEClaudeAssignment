**Claude Code Assignment - HR Analytics Platform**
Overview

This assignment demonstrates the use of Claude Code capabilities including:

Slash Commands
Subagents
Skills
Custom Instructions
Agentic Workflow
MCP Integration

The implementation is based on an HR Analytics Proof of Concept (POC) built on Databricks using Unity Catalog, Delta Tables, Volumes, and HR operational datasets.

**Scenario 1: Repeatable Workflow**
Objective

Automate a recurring code review process using a Claude Code slash command.

Implementation

Created a reusable slash command:
/code_review

Location:
.claude/commands/code_review.md
``

The command performs a structured review covering:

Code quality
Naming conventions
Error handling
Logging
Security concerns
Test coverage

**Scenario 2: Context Management with Subagents**
Objective

Delegate repository investigation to a subagent before making changes.

Implementation

Task:
Find every usage of SCHEMA_OPS

Claude created a subagent to:

Investigate the repository
Search files
Analyze references

**Scenario 3: Packaging a Skill**
Objective

Convert a frequently repeated onboarding process into a reusable Claude Skill.

Skill Created
HR Data Onboarding

Location:
.claude/skills/hr-data-onboarding/SKILL.md

Defined Process
Validate source files
Validate schema
Create Delta table
Load data
Validate counts
Confirm readiness
Validation

Natural language request:
I received a new employee csv export.
what steps should I follow to load it into our HR analytics platform and verify everything was created correctly?

Claude automatically invoked the skill without the skill name being mentioned.

Outcome
Skill created
Trigger conditions defined
Auto-discovery confirmed

**Scenario 4: Enforcing Standards Automatically**
Objective

Apply team coding conventions through a repository-level instruction file.

Instructions File
CLAUDE.md

Standards Implemented
Naming Convention:
snake_case for functions and variables
UPPER_CASE for constants

Error Handling:
Mandatory try/except for external operations

Logging:
Use logger.info()
Use logger.error()
No print() statements

**Scenario 5: Agentic Loop Discipline**
Objective

Ensure Claude follows a structured engineering workflow.

Bug Report
The HR ticket validation process crashes when ticket_id is missing.

Required Workflow
Reproduce
Diagnose
Propose Fix
Apply Fix
Verify

**Scenario 6: Live Data Grounding via MCP**
Objective

Verify Claude retrieves live data from an MCP server rather than relying on model knowledge.

Validation Performed
List available MCP servers.

Result:
No MCP servers are configured.

Findings
The environment did not contain a configured MCP server.

Created MCP server for Github account
Once configured, questions such as:
Show latest commits in this repository.

Outcome:
MCP capability evaluated
Environment limitation documented
Configuration requirement identified

**Key Learnings:**
Slash commands improve repeatability and consistency.
Subagents help isolate large investigations from the main context.
Skills are effective for documenting reusable operational processes.
CLAUDE.md enables organization-wide coding standards enforcement.
Agentic workflows improve debugging quality and traceability.
MCP provides live data access and reduces dependency on model knowledge.

**Conclusion:**
This project successfully demonstrated core Claude Code capabilities across workflow automation, skill packaging, standards enforcement, agentic debugging, and MCP evaluation using a Databricks-based HR Analytics platform.

