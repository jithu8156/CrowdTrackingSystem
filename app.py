from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
from shapely.geometry import Point, Polygon

app = Flask(__name__)
app.secret_key = "supersecretkey123"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

user_locations = {}

event_polygon = None
SQUARES = {}

GRID_SIZE = 4   # 4x4 grid


# -------------------------
# Check inside event
# -------------------------
def inside_event(lat, lon):

    if not event_polygon:
        return False

    point = Point(lon, lat)

    return event_polygon.buffer(0.0003).contains(point)


# -------------------------
# Generate grid squares
# -------------------------
def generate_grid(coords):

    global SQUARES

    lats = [lat for lon, lat in coords]
    lons = [lon for lon, lat in coords]

    lat_min = min(lats)
    lat_max = max(lats)
    lon_min = min(lons)
    lon_max = max(lons)

    lat_step = (lat_max - lat_min) / GRID_SIZE
    lon_step = (lon_max - lon_min) / GRID_SIZE

    SQUARES = {}

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):

            square_id = f"{chr(65+i)}{j+1}"

            SQUARES[square_id] = {
                "lat_min": lat_min + i * lat_step,
                "lat_max": lat_min + (i + 1) * lat_step,
                "lon_min": lon_min + j * lon_step,
                "lon_max": lon_min + (j + 1) * lon_step,
                "count": 0,
                "limit": 5
            }

    print("Generated Squares:", SQUARES)


# -------------------------
# Detect square
# -------------------------
def get_square(lat, lon):

    for square_id, square in SQUARES.items():

        if (square["lat_min"] <= lat <= square["lat_max"] and
            square["lon_min"] <= lon <= square["lon_max"]):

            return square_id

    return None


# -------------------------
# Home
# -------------------------
@app.route('/')
def home():
    return render_template('index.html')


# -------------------------
# Update location
# -------------------------
@app.route('/update_location', methods=['POST'])
def update_location():

    data = request.json
    lat = float(data["latitude"])
    lon = float(data["longitude"])

    user_id = request.remote_addr
    previous_square = user_locations.get(user_id)

    if not inside_event(lat, lon):

        if previous_square:
            SQUARES[previous_square]["count"] -= 1
            del user_locations[user_id]

        return jsonify({"message": "Outside Event Area"})

    square = get_square(lat, lon)

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

    return jsonify({"message": "Inside event but not mapped square"})


# -------------------------
# Save boundary
# -------------------------
@app.route('/save_boundary', methods=['POST'])
def save_boundary():

    global event_polygon

    data = request.json
    coordinates = data.get("coordinates")

    if not coordinates:
        return jsonify({"status": "error"})

    try:

        corrected_coords = [(float(lon), float(lat)) for lon, lat in coordinates]

        if corrected_coords[0] != corrected_coords[-1]:
            corrected_coords.append(corrected_coords[0])

        event_polygon = Polygon(corrected_coords)

        generate_grid(corrected_coords)

        print("EVENT POLYGON SET")

        return jsonify({"status": "success"})

    except Exception as e:

        return jsonify({"status": "error", "message": str(e)})


# -------------------------
# Admin login
# -------------------------
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session['admin'] = True

            return redirect(url_for('dashboard'))

        return render_template('admin_login.html', error="Invalid Credentials")

    return render_template('admin_login.html')


# -------------------------
# Dashboard
# -------------------------
@app.route('/dashboard')
def dashboard():

    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    return render_template("dashboard.html", squares=SQUARES)


# -------------------------
# Map
# -------------------------
@app.route('/admin/map')
def admin_map():

    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    return render_template("admin_map.html")


# -------------------------
# Logout
# -------------------------
@app.route('/logout')
def logout():

    session.pop('admin', None)

    return redirect(url_for('admin_login'))


# -------------------------
# Run
# -------------------------
if __name__ == '__main__':

    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)