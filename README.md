# 🌱 AI Energy Dashboard (Open Data)

Dieses Projekt visualisiert und prognostiziert den **Energieverbrauch (kWh)** und die daraus resultierenden **CO₂-Emissionen (kg)** von KI-Modellen.  
Ziel ist es, den Zusammenhang zwischen Energiebedarf, Strommix und Emissionen zu verstehen – und mit Hilfe von **[Facebook Prophet](https://facebook.github.io/prophet/)** eine **Vorhersage bis 2030** zu erstellen.

---

## 📊 Features

- 📈 **Interaktives Streamlit-Dashboard**
  - Energieverbrauch & CO₂-Emissionen pro Jahr  
  - Vergleich mehrerer Länder basierend auf Strommix (z. B. US, DE, AT, CN, FR)
- 🤖 **Forecast bis 2030**  
  - Mit Prophet wird der historische Trend extrapoliert  
  - Anzeige von **Konfidenzintervallen** (Unsicherheitsbereich oben/unten)
- 🌍 **Ländervergleich**  
  - Reale Daten vs. Prognosen auf gleicher Energie-Basis  
  - Visualisierung des Einflusses unterschiedlicher Stromintensitäten
- ⚡ **Automatische Berechnung von CO₂ aus Energieverbrauch × Stromintensität**

## 🗂️ Projektstruktur
AI-Energy-Dashboard/
├── app/
│ └── dashboard.py # Haupt-App (Streamlit Dashboard)
├── data/
│ ├── grid_intensity.csv # gCO₂/kWh pro Land
│ └── models_energy.csv # Energieverbrauch historischer KI-Modelle
├── README.md
├── requirements.txt
└── .gitignore

## ⚙️ Installation & Setup

Folge diesen Schritten, um das Dashboard lokal auszuführen 👇

---

### 1️⃣ Projekt klonen
Lade das Repository herunter oder klone es direkt über die Konsole:
```bash
git clone https://github.com/dein-nutzername/AI-Energy-Dashboard.git
cd AI-Energy-Dashboard

# 2️⃣ Virtuelle Umgebung mit Conda erstellen
conda create -n energy python=3.11 -y
conda activate energy
pip install -r requirements.txt

# Wenn du kein Conda nutzt, kannst du alternativ eine virtuelle Umgebung mit venv anlegen:
python -m venv energy
source energy/bin/activate  # macOS / Linux
energy\Scripts\activate     # Windows

# 3️⃣ Abhängigkeiten installieren - requirements.txt
pip install -r requirements.txt

# 4️⃣ Dashboard starten 🚀
streamlit run app/dashboard.py

# 🧠 Hinweise
Reale Daten werden aus den CSV-Dateien im data/-Ordner geladen.
CO₂-Emissionen werden dynamisch anhand des Landes und Strommixes berechnet.
Prophet extrapoliert Trends bis 2030 – inklusive oberem/unterem Konfidenzintervall.

## 💚 Autorin
**Vanessa Dungl**  
Studierende der Medizintechnik & AI/Data Science  
📍 JKU Linz | FH St. Pölten  
🚀 Ziel: Nachhaltige KI-Modelle sichtbar & verständlich machen

---# AI-Energy-Dashboard
