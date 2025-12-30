# Neybor Route Optimizer
Interactive web app to plan and optimize neyborhood delivery routes or visits.

A lightweight Flask web app that helps optimize routes between Neybor houses in Brussels using straight-line (Haversine) distances.  
It calculates the most efficient visiting order between addresses and provides a direct link to view the route in Google Maps.

---

## Features

- Displays a list of Neybor houses with preloaded coordinates
- Optimizes travel routes between selected houses
- Returns:
  - Optimized order of houses
  - Total distance in kilometers
  - Google Maps directions URL
- Interactive frontend (via `index.html` in `/templates`)
- Can be exposed publicly using **ngrok** or **pyngrok**

- ![Neybor Route Optimizer Map](maps_itinerary.png)

---

## How It Works

1. **Data source:** A predefined list of Neybor houses with names, addresses, and coordinates.
2. **Optimization:**  
   Uses a greedy nearest-neighbor algorithm + 2-opt local improvement to minimize total travel distance.
3. **Distance Calculation:**  
   Based on the [Haversine formula](https://en.wikipedia.org/wiki/Haversine_formula) for accurate great-circle distances.
4. **Visualization:**  
   Generates a shareable [Google Maps Directions](https://www.google.com/maps/dir/) URL for your optimized route.

---

## Project Structure
```
├── app.py # Main Flask app
├── route_utils.py # Route optimization logic
├── templates/
│ └── index.html # Web interface
├── static/
│ └── style.css # Stylesheet
```

---

## ⚙️ Installation

### 1. Clone the repository
```
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```
## Run locally
```
python app.py
```

## Open your browser and go to:
```
http://127.0.0.1:5000
```
## Run with ngrok (to share publicly)
```
pip install flask-ngrok pyngrok
python app.py
```
You’ll see a public URL printed in the terminal.

---
## License

This project is open-source under the MIT License.

## Author

Amel GHRIBI from Neybor Team
Built for internal route visualization and optimization across Neybor houses in Brussels.
