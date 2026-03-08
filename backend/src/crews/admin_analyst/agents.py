from crewai import Agent
from crewai.tools import tool

from ...tools.azure_sql_tool import execute_read_query
from ...config import get_settings

settings = get_settings()

# Full DB schema injected into NL2SQL agent's backstory
DB_SCHEMA = """
Database Schema (Azure SQL, read-only):
- Users (user_id, employee_no, email, name, dept_id FK, role: 'Employee'|'Admin', created_at)
- Departments (dept_id, dept_name, manager_id FK→Users)
- AssetCategories (category_id, category_name, audit_cycle_months)
- Assets (asset_id, asset_code(10-digit), asset_name, category_id FK, status: 'Active'|'Disposed'|'Transferred', current_holder_id FK→Users, registered_address, last_audit_date, last_condition, created_at)
- AuditLogs (audit_id, asset_id FK, user_id FK, photo_url, ocr_asset_code, detected_address, distance_meters, photo_taken_at, asset_condition, is_verified BIT, verification_msg, created_at)
- ChatLogs (log_id, admin_user_id FK, user_query, generated_sql, result_summary, export_file_url, created_at)

RULES: Generate SELECT queries ONLY. Use English literals for status values.
"""


@tool("admin_sql_execute")
def admin_sql_tool(sql: str) -> list:
    """Execute a read-only SELECT query against Azure SQL Database. Returns list of row dicts."""
    return execute_read_query(sql)


def make_sql_analyst_agent() -> Agent:
    return Agent(
        role="SQL Analyst",
        goal=(
            "Translate natural language questions about assets and employees into accurate "
            "read-only SQL SELECT queries and execute them."
        ),
        backstory=(
            f"You are an expert SQL analyst for an asset management system. "
            f"Always generate read-only SELECT queries.\n\n{DB_SCHEMA}"
        ),
        tools=[admin_sql_tool],
        verbose=False,
        allow_delegation=False,
        llm=f"azure/{settings.azure_openai_deployment}",
    )


def make_report_manager_agent() -> Agent:
    return Agent(
        role="Report Manager",
        goal="Format SQL query results as structured JSON with columns, rows, total_rows, and summary.",
        backstory="You are a report formatting expert. Present results clearly for asset managers.",
        tools=[],
        verbose=False,
        allow_delegation=False,
        llm=f"azure/{settings.azure_openai_deployment}",
    )
