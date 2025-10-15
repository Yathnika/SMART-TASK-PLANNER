# app.py (Final version with Database)

import os
import json
import re
import math
import sqlite3 # Built-in library for SQLite
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# --- NEW: Database Setup ---
def init_db():
    # Establishes a connection to the database file (creates it if it doesn't exist)
    conn = sqlite3.connect('plans.db')
    cursor = conn.cursor()
    # Creates a 'plans' table if it doesn't already exist
    # We store the plan_data as a JSON text string
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            plan_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('models/gemini-pro-latest') 
except KeyError:
    print("🔴 Error: GOOGLE_API_KEY not found. Please set it in the .env file.")
    exit()

# --- Page Routes ---
@app.route('/')
def index():
    return render_template('index.html')

# --- NEW: Route to view all saved plans ---
@app.route('/plans')
def view_plans():
    conn = sqlite3.connect('plans.db')
    # Use a dictionary cursor to get column names
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    # Fetch all plans, newest first
    cursor.execute("SELECT id, project_name, created_at FROM plans ORDER BY created_at DESC")
    plans = cursor.fetchall()
    conn.close()
    # Render a new HTML page to display the list of plans
    return render_template('plans.html', plans=plans)

# --- API Endpoints ---
@app.route('/create-plan', methods=['POST'])
def create_plan_endpoint():
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    
    data = request.get_json()
    goal = data.get('goal')

    if not goal:
        return jsonify({"error": "The 'goal' field is required."}), 400
    
    print(f"🚀 Received goal: {goal}")
    plan = generate_plan(goal)
    
    if "error" in plan:
        # Map certain known errors to HTTP status codes
        err_msg = str(plan.get('error', ''))
        if 'quota' in err_msg.lower() or '429' in err_msg:
            # Try to extract a retry delay in seconds from common message patterns
            retry_after = None
            m = re.search(r'Please retry in\s*(\d+(?:\.\d+)?)s', err_msg, flags=re.IGNORECASE)
            if not m:
                m = re.search(r'retry_delay\s*\{[^}]*seconds:\s*(\d+)', err_msg)
            if m:
                try:
                    retry_after = int(math.ceil(float(m.group(1))))
                except Exception:
                    retry_after = None

            # Build response with Retry-After header when available
            from flask import make_response
            body = {"error": err_msg}
            if retry_after is not None:
                body['retry_after'] = retry_after
                resp = make_response(jsonify(body), 429)
                resp.headers['Retry-After'] = str(retry_after)
                return resp
            return jsonify(body), 429
        # Generic server error
        return jsonify({"error": err_msg}), 500
    
    # --- NEW: Save the successful plan to the database ---
    try:
        conn = sqlite3.connect('plans.db')
        cursor = conn.cursor()
        # Convert the plan dictionary to a JSON string for storage
        plan_json_string = json.dumps(plan)
        cursor.execute(
            "INSERT INTO plans (project_name, plan_data) VALUES (?, ?)",
            (plan.get('project_name', 'Untitled Plan'), plan_json_string)
        )
        conn.commit()
        conn.close()
        print("💾 Plan saved to database successfully!")
    except Exception as e:
        print(f"🔴 Database save error: {e}")

    print("✅ Plan generated successfully!")
    return jsonify(plan)

# --- NEW: API endpoint to get a single saved plan ---
@app.route('/plans/<int:plan_id>')
def get_plan(plan_id):
    conn = sqlite3.connect('plans.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT plan_data FROM plans WHERE id = ?", (plan_id,))
    plan_record = cursor.fetchone()
    conn.close()
    if plan_record:
        # The data is stored as a string, so we parse it back into JSON
        plan_data = json.loads(plan_record['plan_data'])
        return jsonify(plan_data)
    return jsonify({"error": "Plan not found"}), 404

def generate_plan(goal):
    prompt = f"""
    Break down the following goal into a detailed plan.
    The goal is: "{goal}"

    Provide a valid JSON object as output. Do not include any text or markdown formatting before or after the JSON.
    The object must have a key "project_name" with a creative name for the project, and a key "tasks" which is a list of task objects.
    Each task object must have these keys: "task_id", "task_name", "description", "timeline_days", and "dependencies".
    "dependencies" must be a list of "task_id"s. If there are no dependencies, it must be an empty list [].
    """
    
    # Local testing fallback: set DISABLE_AI=1 (or true) in your environment to avoid calling the external API
    if os.environ.get('DISABLE_AI', '').lower() in ('1', 'true', 'yes'):
        print('⚠️ DISABLE_AI is set — returning a local dummy plan for testing.')
        return {
            "project_name": "Local Test Plan",
            "tasks": [
                {"task_id": 1, "task_name": "Test task", "description": goal, "timeline_days": 1, "dependencies": []}
            ]
        }

    try:
        response = model.generate_content(prompt)
        # Log the raw response for debugging when parsing fails
        raw_text = getattr(response, 'text', None)
        print(f"🔎 Raw model response:\n{raw_text}")

        # Try to clean up common prefixes/suffixes the model might include
        json_response_text = (raw_text or '').strip()

        # Remove common Markdown code fences (```json or ```)
        json_response_text = re.sub(r"^```(?:json)?\s*", '', json_response_text, flags=re.IGNORECASE)
        json_response_text = re.sub(r"\s*```$", '', json_response_text)

        # Remove a leading 'json' or 'JSON' token if present
        if json_response_text.lower().startswith('json'):
            json_response_text = json_response_text[len('json'):].strip()

        # If the model included surrounding text, try to extract the first JSON object/braced block
        json_match = re.search(r"\{[\s\S]*\}", json_response_text)
        if json_match:
            json_candidate = json_match.group(0).strip()
        else:
            json_candidate = json_response_text

        try:
            plan = json.loads(json_candidate)
            return plan
        except json.JSONDecodeError as jde:
            print(f"🔴 JSON decode error: {jde}")
            # Save the raw text to a file to help debugging (low risk)
            try:
                with open('last_raw_model_response.txt', 'w', encoding='utf-8') as f:
                    f.write(raw_text or '')
            except Exception:
                pass
            return {"error": "AI returned invalid JSON. See server logs or last_raw_model_response.txt for details."}
    except Exception as e:
        # Propagate the exception message (useful for returning 429/quota messages to the client)
        print(f"🔴 An error occurred calling the model: {e}")
        return {"error": str(e)}

# Initialize the database when the app starts
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)