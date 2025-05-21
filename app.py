
from flask import Flask, render_template, request, redirect, url_for, send_file
from datetime import datetime, timedelta
import sqlite3
from weasyprint import HTML

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    last_paid TEXT,
                    next_due TEXT
                )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/members')
def members():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM members")
    members = c.fetchall()
    conn.close()
    return render_template('members.html', members=members)

@app.route('/add_member', methods=['POST'])
def add_member():
    name = request.form['name']
    email = request.form['email']
    last_paid = request.form['last_paid']
    next_due = (datetime.strptime(last_paid, "%Y-%m-%d") + timedelta(days=365)).strftime("%Y-%m-%d")

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO members (name, email, last_paid, next_due) VALUES (?, ?, ?, ?)",
              (name, email, last_paid, next_due))
    conn.commit()
    conn.close()
    return redirect(url_for('members'))

@app.route('/delete_member/<int:member_id>')
def delete_member(member_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM members WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('members'))

@app.route('/generate_receipt/<int:member_id>')
def generate_receipt(member_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM members WHERE id = ?", (member_id,))
    member = c.fetchone()
    conn.close()

    html = render_template('receipt.html', member=member)
    pdf = HTML(string=html).write_pdf()

    filename = f"{member[1].replace(' ', '_')}_receipt.pdf"
    with open(filename, 'wb') as f:
        f.write(pdf)

    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
