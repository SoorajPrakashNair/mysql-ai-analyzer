import mysql.connector
import subprocess
import psutil
import os
from textblob import TextBlob
from rich import print
from rich.table import Table
from rich.console import Console
from rich.panel import Panel

console = Console()

# 🔍 Detect if input is general knowledge

def is_general_knowledge(prompt):
    db_keywords = ["select", "employee", "salary", "table", "database", "record", "from", "where", "hire_date", "department"]
    return not any(word in prompt.lower() for word in db_keywords)

# 🧠 Ask LLaMA to generate SQL or answer

def ask_llama(prompt):
    result = subprocess.run(
        ["ollama", "run", "llama3", prompt],
        capture_output=True, text=True
    )
    return result.stdout.strip()

# 🧩 Extract SQL code from LLaMA output

def extract_sql(output):
    if "```sql" in output:
        try:
            return output.split("```sql")[1].split("```")[0].strip()
        except:
            pass
    if "SELECT" in output.upper():
        start = output.upper().index("SELECT")
        end = output.find(";", start)
        if end != -1:
            return output[start:end+1].strip()
        else:
            return output[start:].strip()
    return output.strip()

# 🔧 Run SQL query on MySQL

def run_mysql_query(query):
    conn = mysql.connector.connect(
        host="localhost", user="root", password="sooraj2004", database="company_db"
    )
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    return column_names, rows

# 🧪 EXPLAIN query performance

def explain_query(query):
    try:
        explain_sql = f"EXPLAIN {query.strip().rstrip(';')};"
        col_names, rows = run_mysql_query(explain_sql)

        table = Table(title="🧪 EXPLAIN Analysis")
        for col in col_names:
            table.add_column(col, style="green", overflow="fold")

        for row in rows:
            table.add_row(*[str(cell) for cell in row])

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]❌ Failed to run EXPLAIN:[/] {e}")

# 🐢 Analyse Slow Queries

def analyse_slow_queries(log_path="/var/log/mysql/mysql-slow.log"):
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            print(Panel(f.read(), title="📄 SLOW QUERY LOG", border_style="red"))
    else:
        console.print(f"⚠️ [yellow]Slow query log not found at: {log_path}[/]")

# 🔍 Check Indexes on all tables

def check_table_indexes():
    query = """
    SELECT TABLE_NAME, INDEX_NAME, COLUMN_NAME
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = 'company_db';
    """
    try:
        col_names, results = run_mysql_query(query)
        table = Table(title="🔍 Indexes Found", expand=True)

        for col in col_names:
            table.add_column(col, style="green", no_wrap=True, overflow="ignore")

        for row in results:
            table.add_row(*[str(cell) for cell in row])

        console.print(table)
    except Exception as e:
        console.print(f"[bold red]❌ Error checking indexes:[/] {e}")

# 📊 System & MySQL stats

def get_performance_metrics():
    console.print(Panel("📊 SYSTEM PERFORMANCE", style="bold green"))
    print(f"🖥️  CPU Usage: {psutil.cpu_percent()}%")
    print(f"🧠 Memory Usage: {psutil.virtual_memory().percent}%")

    try:
        conn = mysql.connector.connect(
            host="localhost", user="root", password="sooraj2004"
        )
        cursor = conn.cursor()
        cursor.execute("SHOW GLOBAL STATUS LIKE 'Questions';")
        result = cursor.fetchone()
        print(f"📈 MySQL Questions Count: {result[1]}")
        cursor.close()
        conn.close()
    except Exception as e:
        print("[bold red]❌ Error getting performance metrics:[/]", e)

# 📄 Display Query Result

def display_query_result(col_names, results):
    table = Table(title="📄 Query Result")
    for col in col_names:
        table.add_column(col, style="green")
    for row in results:
        table.add_row(*[str(cell) for cell in row])
    console.print(table)

# 🔄 Main Interactive Loop
while True:
    user_input = input("\nAsk 🤖: ").strip().lower()

    if user_input in ["exit", "quit"]:
        break

    elif "slow" in user_input and "query" in user_input:
        analyse_slow_queries()
    elif "index" in user_input:
        check_table_indexes()
    elif "performance" in user_input or "system" in user_input:
        get_performance_metrics()
    elif is_general_knowledge(user_input):
        print("[bold magenta]💬 General Knowledge Answer:[/bold magenta]")
        output = ask_llama(user_input)
        print(f"[green]{output}[/green]")
    else:
        corrected_input = str(TextBlob(user_input).correct())
        print(f"[bold green]📝 Did you mean:[/] {corrected_input}")

        sql_prompt = f"""
        You are querying a MySQL database with an 'employees' table.
        The columns are: emp_id, first_name, last_name, email, hire_date, job_title, phone, salary, department_id.
        Write a MySQL query for this request: {corrected_input}
        Return only the query.
        """
        mysql_query = extract_sql(ask_llama(sql_prompt))
        print("[bold green]🧠 Generated SQL:[/]")
        print(mysql_query)

        try:
            col_names, results = run_mysql_query(mysql_query.strip())
            if results:
                display_query_result(col_names, results)
                print("[bold green]📘 Result Insight:[/]")
                if "order by salary asc" in mysql_query.lower():
                    print("This shows employee(s) with the lowest salary.")
                elif "order by salary desc" in mysql_query.lower():
                    print("This shows employee(s) with the highest salary.")
                elif "hire_date" in mysql_query.lower() and "desc" in mysql_query.lower():
                    print("This shows most recently hired employees.")
                elif "limit" in mysql_query.lower():
                    print("Query is limited to specific number of rows.")
                elif "where" in mysql_query.lower():
                    print("Filtered result based on specified condition.")
                else:
                    print("General data retrieved from the employees table.")

                print("[bold magenta]🤖 AI Suggestion:[/]")
                if "salary" in mysql_query.lower() and "order by" in mysql_query.lower():
                    print("Consider indexing the salary column for better ORDER BY performance.")
                    print("ALTER TABLE employees ADD INDEX idx_salary (salary);")
                elif "hire_date" in mysql_query.lower():
                    print("Consider indexing the hire_date column to improve sort speed.")
                    print("ALTER TABLE employees ADD INDEX idx_hire_date (hire_date);")
                elif "department_id" in mysql_query.lower():
                    print("Indexing department_id can help with filtering.")
                    print("ALTER TABLE employees ADD INDEX idx_department (department_id);")
                else:
                    print("Use EXPLAIN to analyze performance and add indexes where needed.")

                print("\n[bold green]🧪 Query Performance Plan (EXPLAIN):[/]")
                explain_query(mysql_query)
            else:
                print("[yellow]📭 No results found.[/]")
        except Exception as e:
            print("[bold red]❌ Error running query:[/]", e)
