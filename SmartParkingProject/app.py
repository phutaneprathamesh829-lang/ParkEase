from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Helper function to get JSON database file per branch
def get_db_file(branch):
    return f"parking_database_{branch}.json"

def load_data(branch):
    db_file = get_db_file(branch)
    if os.path.exists(db_file):
        try:
            with open(db_file, "r") as f:
                return json.load(f)
        except Exception:
            pass
    # Default initial state
    return {
        "totalSlots": 12,
        "rates": {"Bike": 10, "Car": 20, "SUV": 30},
        "fineRate": 50,
        "parking": {},
        "history": []
    }

def save_data(branch, data):
    db_file = get_db_file(branch)
    with open(db_file, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def api_status():
    branch = request.args.get("branch", "vashi")
    data = load_data(branch)
    return jsonify(data)

@app.route("/api/checkin", methods=["POST"])
def api_checkin():
    req = request.json
    branch = req.get("branch", "vashi")
    slot = req.get("slot")
    
    data = load_data(branch)
    data["parking"][slot] = {
        "slot": slot,
        "vehicleNo": req.get("vehicleNo"),
        "vehicleType": req.get("vehicleType"),
        "customerName": req.get("customerName"),
        "phone": req.get("phone"),
        "bookedHours": int(req.get("bookedHours", 1)),
        "checkin": req.get("checkin", os.popen('date').read() if os.name != 'nt' else __import__('datetime').datetime.now().isoformat())
    }
    save_data(branch, data)
    return jsonify({"success": True, "message": "Check-in successful"})

@app.route("/api/checkout", methods=["POST"])
def api_checkout():
    req = request.json
    branch = req.get("branch", "vashi")
    slot = req.get("slot")
    
    data = load_data(branch)
    if slot in data["parking"]:
        record = data["parking"].pop(slot)
        
        # Calculate fee & record history
        rates = data.get("rates", {"Bike": 10, "Car": 20, "SUV": 30})
        booked_hrs = record.get("bookedHours", 1)
        v_type = record.get("vehicleType", "Bike")
        parking_fee = booked_hrs * float(rates.get(v_type, 10))
        fine = 0 # Simulated fine if applicable
        
        from datetime import datetime
        record["checkout"] = datetime.now().isoformat()
        record["parkingFee"] = parking_fee
        record["fine"] = fine
        record["total"] = parking_fee + fine
        
        if "history" not in data:
            data["history"] = []
        data["history"].append(record)
        save_data(branch, data)
        return jsonify({"success": True, "message": "Checkout successful"})
    
    return jsonify({"success": False, "message": "Slot not found"})

@app.route("/api/update-settings", methods=["POST"])
def api_update_settings():
    req = request.json
    branch = req.get("branch", "vashi")
    data = load_data(branch)
    
    data["totalSlots"] = int(req.get("totalSlots", data["totalSlots"]))
    data["rates"] = req.get("rates", data["rates"])
    data["fineRate"] = float(req.get("fineRate", data["fineRate"]))
    
    save_data(branch, data)
    return jsonify({"success": True, "message": "Settings updated successfully"})

@app.route("/api/login", methods=["POST"])
def api_login():
    return jsonify({"success": True, "message": "Login successful"})

@app.route("/api/register", methods=["POST"])
def api_register():
    return jsonify({"success": True, "message": "Registration successful"})

@app.route("/api/forgot-password", methods=["POST"])
def api_forgot_password():
    return jsonify({"success": True, "message": "Password reset link sent"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)