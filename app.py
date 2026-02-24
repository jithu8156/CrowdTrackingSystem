from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Store user current square
user_locations = {}

# Define grid squares
SQUARES = {
    "A1": {
        "lat_min": 9.9300,
        "lat_max": 9.9315,
        "lon_min": 76.2660,
        "lon_max": 76.2675,
        "count": 0,
        "limit": 3
    },
    "A2": {
        "lat_min": 9.9300,
        "lat_max": 9.9315,
        "lon_min": 76.2675,
        "lon_max": 76.2690,
        "count": 0,
        "limit": 3
    },
    "B1": {
        "lat_min": 9.9315,
        "lat_max": 9.9330,
        "lon_min": 76.2660,
        "lon_max": 76.2675,
        "count": 0,
        "limit": 3
    },
    "B2": {
        "lat_min": 9.9315,
        "lat_max": 9.9330,
        "lon_min": 76.2675,
        "lon_max": 76.2690,
        "count": 0,
        "limit": 3
    }
}

# Detect square based on location
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

    # Identify user using IP address
    user_id = request.remote_addr

    previous_square = user_locations.get(user_id)

    # If user is inside event area
    if square:

        # If user moved to new square
        if previous_square and previous_square != square:
            SQUARES[previous_square]["count"] -= 1

        # If first time entering or changed square
        if previous_square != square:
            SQUARES[square]["count"] += 1

        # Update user location
        user_locations[user_id] = square

        alert = SQUARES[square]["count"] > SQUARES[square]["limit"]

        return jsonify({
            "square": square,
            "count": SQUARES[square]["count"],
            "limit": SQUARES[square]["limit"],
            "alert": alert
        })

    # If user left event area
    else:
        if previous_square:
            SQUARES[previous_square]["count"] -= 1
            del user_locations[user_id]

        return jsonify({"message": "Outside event area"})


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html", squares=SQUARES)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)