# app.py
import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from route_utils import optimize_open_route, google_maps_url, haversine_km

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Ensure absolute paths & default /static URL
app = Flask(
    __name__,
    template_folder=TEMPLATES_DIR,
    static_folder=STATIC_DIR,
    static_url_path="/static",
)

# -------------------- DATA --------------------
DEFAULT_HOUSES = [
    {"name": "Ambiorix 46", "address": "Rue des Deux Tours 46, 1210 Saint-Josse-ten-Noode", "lat": 50.85105495407479, "lon": 4.3782560115086575, "is_airbnb": False},
    {"name": "Artan 112", "address": "Rue Artan 112, 1030 Schaerbeek", "lat": 50.85364680806313, "lon": 4.383660167330543, "is_airbnb": False},
    {"name": "Botanique 31", "address": "Chau. de Haecht 31, 1210 Saint-Josse-ten-Noode", "lat": 50.85592825310391, "lon": 4.367923365481105, "is_airbnb": False},
    {"name": "Botanique 42", "address": "Rue du Méridien 42, 1210 Saint-Josse-ten-Noode", "lat": 50.854565830029024, "lon": 4.369158338494917, "is_airbnb": False},
    {"name": "Brugman 53", "address": "Av. Louis Lepoutre 53, 1050 Ixelles", "lat": 50.81912136605574, "lon": 4.357256511506246, "is_airbnb": False},
    {"name": "Colignon 31", "address": "Rue Herman 31, 1030 Schaerbeek", "lat": 50.86468744645891, "lon": 4.377417184523553, "is_airbnb": False},
    {"name": "Fernand 12", "address": "Rue Mercelis 12, 1050 Ixelles", "lat": 50.832579262484806, "lon": 4.3660458673289915, "is_airbnb": False},
    {"name": "Fernand 3", "address": "Rue du Viaduc 3, 1050 Ixelles", "lat": 50.832376723699724, "lon": 4.3676680961646195, "is_airbnb": False},
    {"name": "Flagey 16", "address": "Rue Maes 16, 1050 Ixelles", "lat": 50.831473175030396, "lon": 4.369378880821944, "is_airbnb": False},
    {"name": "Flagey 21", "address": "Rue du Serpentin 21, 1050 Ixelles", "lat": 50.82793441321475, "lon": 4.374789453835611, "is_airbnb": False},
    {"name": "Louise 13", "address": "Rue d'Ecosse 13, 1060 Saint-Gilles", "lat": 50.83328226728295, "lon": 4.352356296164707, "is_airbnb": False},
    {"name": "Louise 65", "address": "Rue Mercelis 65, 1050 Ixelles", "lat": 50.83107722398169, "lon": 4.363488094314956, "is_airbnb": False},
    {"name": "Parvis 4", "address": "Rue de la Filature 4, 1060 Saint-Gilles", "lat": 50.83203942132771, "lon": 4.345137138493248, "is_airbnb": False},
    {"name": "Leopold 1", "address": "Rue Vandenbroeck 1", "lat": 50.835676118178, "lon": 4.374911192465664, "is_airbnb": False},
    {"name": "Leopold 55", "address": "Rue du Chateau 55", "lat": 50.83131861580924, "lon": 4.380596035899892, "is_airbnb": False},
    {"name": "Neybor Office", "address": "Chaussée de Boondael 365, Ixelles 1050", "lat": 50.8177318, "lon": 4.3864221, "is_airbnb": False},
]
START_DEFAULT = "Neybor Office"
END_DEFAULT   = "Neybor Office"

# -------------------- VIEWS --------------------
@app.route("/")
def index():
    return render_template(
        "index.html",
        default_houses=DEFAULT_HOUSES,
        start_default=START_DEFAULT,
        end_default=END_DEFAULT,
        cachebuster=str(os.path.getmtime(os.path.join(STATIC_DIR, "style.css"))) if os.path.exists(os.path.join(STATIC_DIR, "style.css")) else "1"
    )

@app.post("/optimize")
def optimize():
    data = request.get_json(force=True)
    houses = list(data["houses"])
    start_name = data["start_name"]
    end_name = data["end_name"]
    auto_optimize = bool(data.get("auto_optimize", True))

    # Ensure start/end included
    name_map = {h["name"]: h for h in DEFAULT_HOUSES}
    if start_name not in {h["name"] for h in houses}:
        houses.insert(0, name_map[start_name])
    if end_name not in {h["name"] for h in houses}:
        houses.append(name_map[end_name])

    if auto_optimize:
        ordered, dist = optimize_open_route(houses, start_name, end_name)
    else:
        names = [h["name"] for h in houses]
        if names[0] != start_name:
            i = names.index(start_name); houses.insert(0, houses.pop(i))
        names = [h["name"] for h in houses]
        if names[-1] != end_name:
            i = names.index(end_name); houses.append(houses.pop(i))
        ordered = houses
        dist = 0.0
        for i in range(len(ordered) - 1):
            dist += haversine_km(ordered[i], ordered[i+1])

    gmaps = google_maps_url(ordered)
    return jsonify({"ordered": ordered, "distance_km": round(dist, 3), "google_maps_url": gmaps})

# Optional: quick check route to see static files exist
@app.route("/_debug/static/<path:name>")
def debug_static(name):
    path = os.path.join(STATIC_DIR, name)
    exists = os.path.exists(path)
    return {"exists": exists, "path": path}

# -------------------- NGROK STARTUP --------------------
def _try_flask_ngrok(app_):
    try:
        from flask_ngrok import run_with_ngrok
        run_with_ngrok(app_)
        print("🌍 Ngrok (flask-ngrok) will start automatically.")
        return True
    except Exception as e:
        print("ℹ️ flask-ngrok not used:", e)
        return False

def _try_pyngrok():
    try:
        from pyngrok import ngrok
        tunnel = ngrok.connect(5000, "http")
        print(f"🌐 pyngrok tunnel: {tunnel.public_url} -> http://127.0.0.1:5000")
        return True
    except Exception as e:
        print("ℹ️ pyngrok not used:", e)
        return False

if __name__ == "__main__":
    used = _try_flask_ngrok(app)
    if used:
        app.run()
    else:
        if _try_pyngrok():
            app.run()
        else:
            print("⚠️ Running locally only. Install flask-ngrok or pyngrok to expose publicly.")
            app.run()
