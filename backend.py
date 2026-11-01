#!/usr/bin/env python3
"""
===============================================================================
PERSONAL FINANCE & EXPENSE ANALYZER - ENTERPRISE BACKEND SYSTEM (v6.0)
Architecture: Native Python http.server REST API + Multi-Tiered Data Layer
Storage Subsystems: SQLite3 DB, CSV Exports, TXT Security Logs, Pickle Binary State
Target Standard: CBSE Class XII Computer Science Practical Project
Author: Sagnik Guha
Support Email: sagnikguha2010@gmail.com
===============================================================================
"""

import os
import sys
import json
import sqlite3
import csv
import pickle
import time
import datetime
import urllib.parse
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- GLOBAL SYSTEM CONFIGURATION ---
HOST = "0.0.0.0"
PORT = 8081
# --- AUTHENTICATION CONFIG ---
USERNAME = "sagnik"
PASSWORD = "securepassword123"
DB_FILE = "finance_master.db"
CSV_FILE = "transactions.csv"
LOG_FILE = "audit_trail.txt"
PICKLE_FILE = "app_state.pkl"
DEV_EMAIL = "sagnikguha2010@gmail.com"

# --- STORAGE SUBSYSTEM CONTROLLERS ---

def init_databases():
    """Initialize SQLite3 relational database with full schema definition."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # User Credentials Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            auth_provider TEXT DEFAULT 'Local',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Financial Ledger Transactions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            trans_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            trans_type TEXT CHECK(trans_type IN ('income', 'expense')) NOT NULL,
            trans_date DATE NOT NULL,
            FOREIGN KEY (user_email) REFERENCES users (email)
        )
    ''')
    
    # Helpdesk Support Tickets Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS support_tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            recipient_email TEXT NOT NULL,
            inquiry_type TEXT NOT NULL,
            message TEXT NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Seed default user if database is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (name, email, auth_provider) VALUES (?, ?, ?)",
                       ("Demo User", DEV_EMAIL, "System"))
        
    conn.commit()
    conn.close()
    log_audit_event("DATABASE_INIT", "SQLite schemas verified and tables active.")

def init_csv_storage():
    """Initialize CSV raw ledger file."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Transaction_ID", "User_Email", "Title", "Amount", "Category", "Type", "Date"])
        log_audit_event("CSV_INIT", "Transaction CSV ledger created.")

def init_pickle_storage():
    """Initialize binary state store using Python pickle module."""
    if not os.path.exists(PICKLE_FILE):
        default_state = {
            "system_version": "6.0.0",
            "last_backup": str(datetime.datetime.now()),
            "support_recipient": DEV_EMAIL,
            "currency_symbol": "₹",
            "features_enabled": ["GoogleOAuth", "VisualGraphs", "AISuggestions", "FAQSection", "TopNavbar"]
        }
        with open(PICKLE_FILE, "wb") as f:
            pickle.dump(default_state, f)
        log_audit_event("PICKLE_INIT", "Application binary state serialized.")

def log_audit_event(event_type, description):
    """Append audit trail logs into standard text log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{event_type}] {description}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(log_entry)

def sync_db_to_csv():
    """Sync all SQLite records into CSV file format."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT trans_id, user_email, title, amount, category, trans_type, trans_date FROM transactions")
    rows = cursor.fetchall()
    conn.close()

    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Transaction_ID", "User_Email", "Title", "Amount", "Category", "Type", "Date"])
        writer.writerows(rows)
    log_audit_event("CSV_SYNC", f"Exported {len(rows)} database records to CSV.")

# --- FINANCIAL ANALYTICS & AI SUGGESTIONS ---

def calculate_analytics(user_email):
    """Compute financial summary metrics and category distributions."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_email = ? AND trans_type = 'income'", (user_email,))
    total_income = cursor.fetchone()[0] or 0.0
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_email = ? AND trans_type = 'expense'", (user_email,))
    total_expense = cursor.fetchone()[0] or 0.0
    
    cursor.execute("""
        SELECT category, SUM(amount) 
        FROM transactions 
        WHERE user_email = ? AND trans_type = 'expense' 
        GROUP BY category
    """, (user_email,))
    category_rows = cursor.fetchall()
    category_breakdown = {cat: amt for cat, amt in category_rows}
    
    conn.close()
    
    net_savings = total_income - total_expense
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0.0
    
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_savings": net_savings,
        "savings_rate": round(savings_rate, 2),
        "category_breakdown": category_breakdown
    }

def generate_suggestions(analytics):
    """Evaluate financial standing and generate smart suggestions."""
    suggestions = []
    income = analytics["total_income"]
    expense = analytics["total_expense"]
    rate = analytics["savings_rate"]
    breakdown = analytics["category_breakdown"]

    if income == 0:
        suggestions.append({
            "title": "Add Income Source",
            "type": "warning",
            "desc": "No active income recorded. Add your salary or allowance to start generating automated financial budgets."
        })
    elif rate < 20:
        suggestions.append({
            "title": "Low Savings Rate Notice",
            "type": "danger",
            "desc": f"Your current savings rate is {rate}%. Aim to save at least 20% of net monthly earnings."
        })
    else:
        suggestions.append({
            "title": "Optimal Savings Target",
            "type": "success",
            "desc": f"Excellent work! You are saving {rate}% of your income. Consider placing surplus capital into index funds."
        })

    food_exp = breakdown.get("Food & Dining", 0)
    if income > 0 and (food_exp / income) > 0.3:
        suggestions.append({
            "title": "High Food Outlay Alert",
            "type": "warning",
            "desc": "Food & Dining costs exceed 30% of your total income. Try reducing restaurant spending."
        })

    return suggestions

# --- API ROUTER & SERVER HANDLER ---

class FinanceEnterpriseHandler(BaseHTTPRequestHandler):
    """High-performance request handler serving HTML frontends and JSON REST APIs."""
  def check_auth(self):
    auth_header = self.headers.get("Authorization")
    if not auth_header:
      return False
    try:
      auth_type, encoded = auth_header.split(" ", 1)
      if auth_type.lower() != "basic":
        return False
      decoded = base64.b64decode(encoded).decode("utf-8")
      user, pwd = decoded.split(":", 1)
      return user == USERNAME and pwd == PASSWORD
    except Exception:
      return False

  def send_auth_challenge(self):
    self.send_response(401)
    self.send_header(
        "WWW-Authenticate", 'Basic realm="Personal Finance Enterprise"'
    )
    self.end_headers()
    self.wfile.write(b"Access Denied: Password Required")
    

    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors()
        self.end_headers()

    def do_GET(self):
        if not self.check_auth():
            return self.send_auth_challenge()

        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            if os.path.exists("index.html"):
                with open("index.html", "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(b"<h1>404: index.html not found</h1>")
                
        elif parsed.path == "/api/data":
            params = urllib.parse.parse_qs(parsed.query)
            email = params.get("email", [DEV_EMAIL])[0]
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT trans_id, title, amount, category, trans_type, trans_date 
                FROM transactions WHERE user_email = ? ORDER BY trans_date DESC
            """, (email,))
            rows = cursor.fetchall()
            conn.close()

            transactions = [{"id": r[0], "title": r[1], "amount": r[2], "category": r[3], "type": r[4], "date": r[5]} for r in rows]
            analytics = calculate_analytics(email)
            suggestions = generate_suggestions(analytics)

            with open(PICKLE_FILE, "rb") as f:
                pickle_state = pickle.load(f)

            payload = {
                "user_email": email,
                "transactions": transactions,
                "analytics": analytics,
                "suggestions": suggestions,
                "system_state": pickle_state
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors()
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if not self.check_auth():
            return self.send_auth_challenge()
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        payload = json.loads(body.decode('utf-8')) if body else {}

        # AUTHENTICATION API
        if parsed.path == "/api/auth":
            name = payload.get("name", "User")
            email = payload.get("email", DEV_EMAIL)
            provider = payload.get("provider", "Local")

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO users (name, email, auth_provider) VALUES (?, ?, ?)", (name, email, provider))
                conn.commit()
                log_audit_event("AUTH_REGISTER", f"Registered {email} via {provider}")
            else:
                log_audit_event("AUTH_LOGIN", f"Logged in {email} via {provider}")
            conn.close()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "user": {"name": name, "email": email, "provider": provider}}).encode('utf-8'))

        # ADD TRANSACTION API
        elif parsed.path == "/api/transaction/add":
            email = payload.get("email", DEV_EMAIL)
            title = payload.get("title", "Untitled")
            amount = float(payload.get("amount", 0.0))
            category = payload.get("category", "General")
            trans_type = payload.get("type", "expense")
            trans_date = payload.get("date", str(datetime.date.today()))

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (user_email, title, amount, category, trans_type, trans_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (email, title, amount, category, trans_type, trans_date))
            conn.commit()
            conn.close()

            log_audit_event("TRANSACTION_ADD", f"Added {trans_type} of ₹{amount} for {email}")
            sync_db_to_csv()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": "Transaction added successfully"}).encode('utf-8'))

        # DELETE TRANSACTION API
        elif parsed.path == "/api/transaction/delete":
            trans_id = payload.get("id")
            email = payload.get("email", DEV_EMAIL)

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE trans_id = ? AND user_email = ?", (trans_id, email))
            conn.commit()
            conn.close()

            log_audit_event("TRANSACTION_DELETE", f"Deleted transaction {trans_id} for {email}")
            sync_db_to_csv()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": "Transaction deleted"}).encode('utf-8'))

        # SUPPORT TICKET API
        elif parsed.path == "/api/support":
            user_email = payload.get("user_email")
            recipient_email = payload.get("recipient_email", DEV_EMAIL)
            inquiry_type = payload.get("inquiry_type", "General")
            message = payload.get("message", "")

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO support_tickets (user_email, recipient_email, inquiry_type, message)
                VALUES (?, ?, ?, ?)
            """, (user_email, recipient_email, inquiry_type, message))
            conn.commit()
            conn.close()

            log_audit_event("SUPPORT_TICKET", f"Ticket sent from {user_email} to {recipient_email}")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors()
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success", 
                "message": f"Support ticket registered! Developer support notified at {recipient_email}"
            }).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()

def main():
    init_databases()
    init_csv_storage()
    init_pickle_storage()
    server = HTTPServer((HOST, PORT), FinanceEnterpriseHandler)
    print(f"[*] ENTERPRISE BACKEND SERVER RUNNING ON http://localhost:{PORT}")
    print(f"[*] Developer Email: {DEV_EMAIL}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server shutdown complete.")
        server.server_close()

if __name__ == "__main__":
    main()
