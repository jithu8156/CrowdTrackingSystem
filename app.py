from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # Needed for session

# -------------------------
# ADMIN CREDENTIALS
# -------------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

# -------------------------
# USER LOCATION STORAGE
# -------------------------
user_locations = {}

# -------------------------
# GRID SQUARES
# -------------------------
SQUARES = {
    "A1": {"lat_min": 9.9300, "lat_max": 9.9315,
           "lon_min": 76.2660, "lon_max": 76.2675,
           "count": 0, "limit": 3},

    "A2": {"lat_min": 9.9300, "lat_max": 9.9315,
           "lon_min": 76.2675, "lon_max": 76.2690,
           "count": 0, "limit": 3},

    "B1": {"lat_min": 9.9315, "lat_max": 9.9330,
           "lon_min": 76.2660, "lon_max": 76.2675,
           "count": 0, "limit": 3},

    "B2": {"lat_min": 9.9315, "lat_max": 9.9330,
           "lon_min": 76.2675, "lon_max": 76.2690,
           "count": 0, "limit": 3}
}

# -------------------------
# Detect square
# -------------------------
def get_square(lat, lon):
    for square_id, square in SQUARES.items():
        if (square["lat_min"] <= lat <= square["lat_max"] and
            square["lon_min"] <= lon <= square["lon_max"]):
            return square_id
    return None


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/update_location', methods=['POST'])
def update_location():
    data = request.json
    lat = data["latitude"]
    lon = data["longitude"]

    square = get_square(lat, lon)
    user_id = request.remote_addr
    previous_square = user_locations.get(user_id)

    if square:

        if previous_square and previous_square != square:
            SQUARES[previous_square]["count"] -= 1

        if previous_square != square:
            SQUARES[square]["count"] += 1

        user_locations[user_id] = square

        alert = SQUARES[square]["count"] > SQUARES[square]["limit"]

        return jsonify({
            "square": square,
            "count": SQUARES[square]["count"],
            "alert": alert
        })

    else:
        if previous_square:
            SQUARES[previous_square]["count"] -= 1
            del user_locations[user_id]

        return jsonify({"message": "Outside event area"})


# -------------------------
# ADMIN LOGIN ROUTE
# -------------------------
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('admin_login.html', error="Invalid Credentials")

    return render_template('admin_login.html')


# -------------------------
# PROTECTED DASHBOARD
# -------------------------
@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    return render_template("dashboard.html", squares=SQUARES)


# -------------------------
# LOGOUT
# -------------------------
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)