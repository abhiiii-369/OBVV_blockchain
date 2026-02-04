from flask import Flask, render_template, request, redirect
import sqlite3
import qrcode
import json
from datetime import datetime
from cryptography.fernet import Fernet
import os
import re

app = Flask(__name__)

DB_NAME = "voters.db"
QR_FOLDER = "static/qrs"
os.makedirs(QR_FOLDER, exist_ok=True)

# Load booth secret key
with open("booth_secret.key", "rb") as f:
    cipher = Fernet(f.read())


def get_db():
    return sqlite3.connect(DB_NAME)


# Home page
@app.route("/")
def index():
    db = get_db()
    voters = db.execute(
        "SELECT voter_id, name, qr_filename FROM voters"
    ).fetchall()
    db.close()
    return render_template("index.html", voters=voters)


# Add voter + generate QR
@app.route("/add", methods=["POST"])
def add_voter():
    voter_id = request.form["voter_id"].strip().upper()
    name = request.form["name"].strip()

    # Backend validation (extra safety)
    if not re.match(r"^[A-Z]{3}[0-9]{7}$", voter_id):
        return redirect("/")

    voter_data = {
        "voter_id": voter_id,
        "name": name
    }

    encrypted = cipher.encrypt(json.dumps(voter_data).encode())

    qr_filename = f"{voter_id}.png"
    qr_path = os.path.join(QR_FOLDER, qr_filename)

    qr = qrcode.make(encrypted.decode())
    qr.save(qr_path)

    db = get_db()
    db.execute(
        "INSERT INTO voters (voter_id, name, qr_filename, created_at) VALUES (?, ?, ?, ?)",
        (voter_id, name, qr_filename, datetime.now().isoformat())
    )
    db.commit()
    db.close()

    return redirect("/")


# Delete voter
@app.route("/delete/<voter_id>", methods=["POST"])
def delete_voter(voter_id):
    db = get_db()

    row = db.execute(
        "SELECT qr_filename FROM voters WHERE voter_id = ?",
        (voter_id,)
    ).fetchone()

    if row:
        qr_file = row[0]
        qr_path = os.path.join(QR_FOLDER, qr_file)

        db.execute("DELETE FROM voters WHERE voter_id = ?", (voter_id,))
        db.commit()

        if os.path.exists(qr_path):
            os.remove(qr_path)

    db.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
