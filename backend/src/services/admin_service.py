from sqlalchemy.orm import Session
from ..models.chat_log import ChatLog
from ..crews.admin_analyst.crew import run_admin_analyst_crew
from ..tools.excel_export_tool import generate_and_upload_excel


def process_chat_query(query: str, admin_user_id: int, db: Session) -> dict:
    """
    Run the Admin Analyst Crew on the NL query, save ChatLog, return results.
    """
    result = run_admin_analyst_crew(query)

    log = ChatLog(
        admin_user_id=admin_user_id,
        user_query=query,
        generated_sql=result.get("generated_sql"),
        result_summary=result.get("summary"),
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return {
        "log_id": log.log_id,
        "query": query,
        "generated_sql": result.get("generated_sql", ""),
        "columns": result.get("columns", []),
        "rows": result.get("rows", []),
        "total_rows": result.get("total_rows", 0),
        "summary": result.get("summary", ""),
    }


def export_chat_log(log_id: int, admin_user_id: int, db: Session) -> dict:
    """
    Generate an Excel file from the saved ChatLog and return SAS URL.
    Instead of re-running the AI, we use the saved generated_sql.
    """
    from ..tools.azure_sql_tool import execute_read_query

    log = db.query(ChatLog).filter(
        ChatLog.log_id == log_id,
        ChatLog.admin_user_id == admin_user_id,
    ).first()

    if not log or not log.generated_sql:
        return None

    # Execute the purely SQL query saved during the initial chat
    try:
        db_rows = execute_read_query(log.generated_sql)
        if db_rows:
            columns = list(db_rows[0].keys())
            rows = [list(r.values()) for r in db_rows]
        else:
            columns = ["Result"]
            rows = [["No data found"]]
    except Exception as e:
        columns = ["Error"]
        rows = [[str(e)]]

    export_result = generate_and_upload_excel(columns, rows, admin_user_id)

    # Update log with export URL
    log.export_file_url = export_result["download_url"]
    db.commit()

    return {
        "download_url": export_result["download_url"],
        "file_name": export_result["file_name"],
        "expires_in_minutes": 60,
    }
