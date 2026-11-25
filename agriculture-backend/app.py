from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

import os

app.secret_key = os.environ.get("SECRET_KEY")

DATABASE = "agriculture.db"


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ==================================================
# CREATE DATABASE TABLES
# ==================================================

def init_db():

    conn = get_db()

    # Farmers table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            location TEXT
        )
    """)

    # Crops table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS crops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            soil TEXT NOT NULL,
            season TEXT NOT NULL,
            fertilizer TEXT NOT NULL,
            description TEXT
        )
    """)

    # Market prices table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS market_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_name TEXT NOT NULL,
            market TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)

    # Weather table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            temperature TEXT NOT NULL,
            rainfall TEXT NOT NULL,
            condition TEXT NOT NULL
        )
    """)

    # --------------------------------------------------
    # DEFAULT CROPS
    # --------------------------------------------------

    crop_count = conn.execute(
        "SELECT COUNT(*) FROM crops"
    ).fetchone()[0]

    if crop_count == 0:

        sample_crops = [
            (
                "Rice",
                "Clay Soil",
                "June - November",
                "Urea, DAP",
                "Rice requires sufficient water and warm climate."
            ),
            (
                "Wheat",
                "Loamy Soil",
                "November - March",
                "Nitrogen Fertilizer",
                "Wheat grows well in cool and dry weather."
            ),
            (
                "Tomato",
                "Loamy Soil",
                "October - February",
                "NPK Fertilizer",
                "Tomato requires sunlight and well-drained soil."
            ),
            (
                "Cotton",
                "Black Soil",
                "June - December",
                "Urea, Potash",
                "Cotton grows well in warm climate."
            )
        ]

        conn.executemany("""
            INSERT INTO crops
            (name, soil, season, fertilizer, description)
            VALUES (?, ?, ?, ?, ?)
        """, sample_crops)

    # --------------------------------------------------
    # DEFAULT MARKET PRICES
    # --------------------------------------------------

    market_count = conn.execute(
        "SELECT COUNT(*) FROM market_prices"
    ).fetchone()[0]

    if market_count == 0:

        sample_prices = [
            ("Rice", "Coimbatore Market", 3200),
            ("Wheat", "Chennai Market", 2800),
            ("Tomato", "Coimbatore Market", 2500),
            ("Cotton", "Erode Market", 7200)
        ]

        conn.executemany("""
            INSERT INTO market_prices
            (crop_name, market, price)
            VALUES (?, ?, ?)
        """, sample_prices)

    # --------------------------------------------------
    # DEFAULT WEATHER
    # --------------------------------------------------

    weather_count = conn.execute(
        "SELECT COUNT(*) FROM weather"
    ).fetchone()[0]

    if weather_count == 0:

        sample_weather = [
            ("Coimbatore", "29°C", "20%", "Partly Cloudy"),
            ("Chennai", "32°C", "10%", "Sunny"),
            ("Erode", "30°C", "15%", "Sunny"),
            ("Madurai", "31°C", "25%", "Cloudy")
        ]

        conn.executemany("""
            INSERT INTO weather
            (location, temperature, rainfall, condition)
            VALUES (?, ?, ?, ?)
        """, sample_weather)

    conn.commit()
    conn.close()


# ==================================================
# LOGIN REQUIRED
# ==================================================

def login_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "farmer_id" not in session:

            flash(
                "Please login first.",
                "warning"
            )

            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return decorated_function


# ==================================================
# HOME
# ==================================================

@app.route("/")
def index():

    conn = get_db()

    crop_count = conn.execute(
        "SELECT COUNT(*) FROM crops"
    ).fetchone()[0]

    farmer_count = conn.execute(
        "SELECT COUNT(*) FROM farmers"
    ).fetchone()[0]

    market_count = conn.execute(
        "SELECT COUNT(*) FROM market_prices"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        crop_count=crop_count,
        farmer_count=farmer_count,
        market_count=market_count
    )


# ==================================================
# REGISTER
# ==================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form.get("phone", "")
        location = request.form.get("location", "")

        password_hash = generate_password_hash(password)

        conn = get_db()

        try:

            conn.execute("""
                INSERT INTO farmers
                (name, email, password, phone, location)
                VALUES (?, ?, ?, ?, ?)
            """, (
                name,
                email,
                password_hash,
                phone,
                location
            ))

            conn.commit()

            flash(
                "Registration successful. Please login.",
                "success"
            )

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            flash(
                "Email already registered.",
                "danger"
            )

        finally:

            conn.close()

    return render_template("register.html")


# ==================================================
# LOGIN
# ==================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        farmer = conn.execute("""
            SELECT * FROM farmers
            WHERE email = ?
        """, (email,)).fetchone()

        conn.close()

        if farmer and check_password_hash(
            farmer["password"],
            password
        ):

            session["farmer_id"] = farmer["id"]
            session["farmer_name"] = farmer["name"]

            flash(
                "Login successful.",
                "success"
            )

            return redirect(url_for("dashboard"))

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template("login.html")


# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("index"))


# ==================================================
# FARMER DASHBOARD
# ==================================================

@app.route("/dashboard")
@login_required
def dashboard():

    conn = get_db()

    # Recent crops
    crops = conn.execute("""
        SELECT * FROM crops
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()

    # Recent market prices
    prices = conn.execute("""
        SELECT * FROM market_prices
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()

    # Total crops
    crop_count = conn.execute("""
        SELECT COUNT(*) AS count
        FROM crops
    """).fetchone()["count"]

    # Total market prices
    market_count = conn.execute("""
        SELECT COUNT(*) AS count
        FROM market_prices
    """).fetchone()["count"]

    # Total farmers
    farmer_count = conn.execute("""
        SELECT COUNT(*) AS count
        FROM farmers
    """).fetchone()["count"]

    conn.close()

    return render_template(
        "dashboard.html",
        crops=crops,
        prices=prices,
        total_crops=crop_count,
        total_prices=market_count,
        total_farmers=farmer_count
    )


# ==================================================
# CROPS
# ==================================================

@app.route("/crops")
def crops():

    conn = get_db()

    crop_data = conn.execute("""
        SELECT * FROM crops
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "crops.html",
        crops=crop_data
    )


# ==================================================
# ADD CROP
# ==================================================

@app.route("/add-crop", methods=["GET", "POST"])
@login_required
def add_crop():

    if request.method == "POST":

        name = request.form["name"]
        soil = request.form["soil"]
        season = request.form["season"]
        fertilizer = request.form["fertilizer"]
        description = request.form.get("description", "")

        conn = get_db()

        conn.execute("""
            INSERT INTO crops
            (name, soil, season, fertilizer, description)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            soil,
            season,
            fertilizer,
            description
        ))

        conn.commit()
        conn.close()

        flash(
            "Crop information added successfully.",
            "success"
        )

        return redirect(url_for("crops"))

    return render_template("add_crop.html")


# ==================================================
# WEATHER
# ==================================================

@app.route("/weather")
def weather():

    location = request.args.get(
        "location",
        ""
    )

    conn = get_db()

    if location:

        weather_data = conn.execute("""
            SELECT * FROM weather
            WHERE location LIKE ?
        """, (
            "%" + location + "%",
        )).fetchall()

    else:

        weather_data = conn.execute("""
            SELECT * FROM weather
        """).fetchall()

    conn.close()

    return render_template(
        "weather.html",
        weather=weather_data,
        location=location
    )


# ==================================================
# MARKET PRICE
# ==================================================

@app.route("/market")
def market():

    search = request.args.get(
        "search",
        ""
    )

    conn = get_db()

    if search:

        prices = conn.execute("""
            SELECT * FROM market_prices
            WHERE crop_name LIKE ?
            OR market LIKE ?
        """, (
            "%" + search + "%",
            "%" + search + "%"
        )).fetchall()

    else:

        prices = conn.execute("""
            SELECT * FROM market_prices
            ORDER BY id DESC
        """).fetchall()

    conn.close()

    return render_template(
        "market.html",
        prices=prices,
        search=search
    )


# ==================================================
# ADMIN DASHBOARD
# ==================================================

@app.route("/admin")
def admin():

    conn = get_db()

    farmers = conn.execute("""
        SELECT id, name, email, phone, location
        FROM farmers
        ORDER BY id DESC
    """).fetchall()

    crops = conn.execute("""
        SELECT * FROM crops
        ORDER BY id DESC
    """).fetchall()

    prices = conn.execute("""
        SELECT * FROM market_prices
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        farmers=farmers,
        crops=crops,
        prices=prices
    )


# ==================================================
# DISEASE INFORMATION
# ==================================================

@app.route("/disease")
def disease():

    return render_template(
        "disease.html"
    )


# ==================================================
# START APPLICATION
# ==================================================

if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )