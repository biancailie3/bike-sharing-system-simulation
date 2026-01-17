# 🚲 EcoRide: Smart City Bike Sharing Simulation

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://bike-sharing-system-simulation-aw6dd37pqn3txndmjkvmhc.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Library](https://img.shields.io/badge/SimPy-Simulation-green)

**EcoRide** is a Digital Twin simulation designed to optimize bike-sharing operations in **Timișoara, Romania**.

Using **Discrete Event Simulation (DES)**, this application models customer behavior, station capacity, and maintenance logistics to visualize potential bottlenecks in a real-world city infrastructure.

## 🚀 Live Demo
**Try the interactive application here:** 👉 **[Launch EcoRide App]([https://bike-sharing-system-simulation-aw6dd37pqn3txndmjkvmhc.streamlit.app/](https://bike-sharing-system-simulation-suftp89drzfgpbqy4sgkba.streamlit.app/)**

---

## 💡 Key Features

* **Geospatial Visualization:** Integrated **Folium** maps to visualize station status (Empty/Full/Balanced) using real GPS coordinates of Timișoara locations (Piața Unirii, Complex, Iulius Town).
* **Discrete Event Simulation:** Powered by **SimPy** to model asynchronous events (rentals, returns, truck rebalancing) with mathematical precision.
* **Interactive Parameters:** Users can adjust simulation variables (fleet size, demand, truck frequency) via the **Streamlit** sidebar to test different scenarios.
* **KPI Tracking:** Real-time monitoring of "Unhappy Customers" (Lost sales due to empty stations or full docks).
* **Data Analytics:** Line charts tracking inventory levels over time for trend analysis.

---

## ⚙️ How It Works (The Logic)

The simulation runs two parallel processes in a virtual environment:

### 1. The Customer Process
* A customer arrives at a random station.
* **Rental Check:** Is there a bike? 
    * If `No` → **Lost Customer** (Revenue Loss).
* **Journey:** The customer rides for a random duration (10-25 mins).
* **Return Check:** Is there a dock?
    * If `Yes` → **Happy Customer** (Revenue Gain).
    * If `No` → **Rerouting Event**: The customer travels to the nearest station. The ride is free (Revenue Loss) and the customer is flagged as *"Unhappy/Rerouted"*.

### 2. The Logistics Process (The Truck)
* Every `X` minutes, the truck calculates the average fleet density.
* It collects bikes from **"Overloaded"** stations (High Surplus).
* It distributes bikes to **"Starving"** stations (High Deficit).

---

## 📊 Data Visualization

* **Interactive Folium Map:** Geospatial view of stations in Timișoara (Piața Unirii, Gara de Nord, Complex, Iulius Mall) with dynamic status coloring (Red/Orange/Green).
* **Operational KPIs:** Trackers for Happy Customers, Lost Demand (No Bike), and Rerouted Customers (No Space).
* **Tabbed Analytics:** Detailed charts for individual station inventory history and loss cause analysis.

---

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (Web Framework)
* **Simulation Engine:** [SimPy](https://simpy.readthedocs.io/) (Process-based discrete-event simulation)
* **Geospatial:** [Folium](https://python-visualization.github.io/folium/) & `streamlit-folium`
* **Data Manipulation:** Pandas
* **Language:** Python 3

---

## 📂 Project Structure

The project follows a modular architecture separating logic from presentation:

```text
├── app.py           # The View/Controller: Streamlit interface & User inputs
├── logic.py         # The Model: Simulation classes (BikeStation, System)
├── requirements.txt # Dependencies list
└── README.md        # Project documentation
