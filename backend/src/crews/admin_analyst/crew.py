import json
from crewai import Crew, Task, Process
from .agents import make_sql_analyst_agent, make_report_manager_agent


def run_admin_analyst_crew(admin_query: str) -> dict:
    """
    Run the Admin Analyst Crew: NL → SQL → formatted results.
    Returns:
        {
          "generated_sql": str,
          "columns": list[str],
          "rows": list[list],
          "total_rows": int,
          "summary": str
        }
    """
    sql_agent = make_sql_analyst_agent()
    report_agent = make_report_manager_agent()

    t_sql = Task(
        description=(
            f"The admin asks: '{admin_query}'\n"
            "1. Generate a read-only SQL SELECT query.\n"
            "2. Execute it using the azure_sql_tool.\n"
            "3. Return JSON with keys: generated_sql (str), results (list of row dicts)."
        ),
        expected_output="JSON with generated_sql and results (list of dicts)",
        agent=sql_agent,
    )

    t_report = Task(
        description=(
            "Take the SQL results from the previous step and format them.\n"
            "Return JSON with keys:\n"
            "- generated_sql: the SQL that was run\n"
            "- columns: list of column names\n"
            "- rows: list of lists (values in column order)\n"
            "- total_rows: integer count\n"
            "- summary: a one-sentence Korean summary of what the data shows"
        ),
        expected_output="JSON with generated_sql, columns, rows, total_rows, summary",
        agent=report_agent,
        context=[t_sql],
    )

    crew = Crew(
        agents=[sql_agent, report_agent],
        tasks=[t_sql, t_report],
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff(inputs={"admin_query": admin_query})

    import re
    try:
        raw_output = result.raw
        if "```" in raw_output:
            json_match = re.search(r'```(?:json)?\n?(.*?)\n?```', raw_output, re.DOTALL)
            if json_match:
                raw_output = json_match.group(1).strip()
                
        parsed = json.loads(raw_output)
        return {
            "generated_sql": parsed.get("generated_sql", ""),
            "columns": parsed.get("columns", []),
            "rows": parsed.get("rows", []),
            "total_rows": parsed.get("total_rows", 0),
            "summary": parsed.get("summary", ""),
        }
    except (json.JSONDecodeError, AttributeError):
        return {
            "generated_sql": "",
            "columns": [],
            "rows": [],
            "total_rows": 0,
            "summary": "결과를 파싱할 수 없습니다.",
        }
