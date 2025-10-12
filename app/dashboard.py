
import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet
import plotly.graph_objects as go


st.set_page_config(page_title="AI Energy Dashboard", layout="wide")
st.title("🌱 AI Energy Dashboard (Open Data)")

# --- Load data
# NEU (relativ zum Projektordner)
models = pd.read_csv("data/models_energy.csv")
grid   = pd.read_csv("data/grid_intensity.csv")

# Sidebar filters
st.sidebar.header("Filter")
country = st.sidebar.selectbox("Land (für CO₂-Umrechnung)", grid["country"].unique(), index=0)
max_year = int(models["year"].max())
min_year = int(models["year"].min())
year = st.sidebar.slider("Jahr (bis)", min_year, max_year, max_year)

# Compute adjusted CO2 for selected country
g_intensity = grid.loc[grid["country"]==country, "gco2_per_kwh"].values[0]
df = models[models["year"] <= year].copy()
df["co2_adjusted_kg"] = df["kwh"] * g_intensity / 1000.0

# KPI tiles
total_kwh = df["kwh"].sum()
total_co2 = df["co2_adjusted_kg"].sum()
c1, c2 = st.columns(2)
c1.metric("Gesamtenergie (kWh)", f"{total_kwh:,.0f}")
c2.metric(f"Gesamtemissionen in {country} (kg CO₂)", f"{total_co2:,.0f}")

# Scatter: CO2 vs Params
fig = px.scatter(df, x="params_m", y="co2_adjusted_kg", size="kwh", hover_name="model",
                 title=f"CO₂ vs. Modellgröße – Standort: {country} (bis {year})",
                 log_x=True, labels={"params_m":"Parameter (Mio.)","co2_adjusted_kg":"kg CO₂ (angepasst)"})
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
# ======================= DATENVORSCHAU =======================
# Energie (kWh) – Jahresaggregation
models["year"] = models["year"].astype(int)

annual_kwh = models.groupby("year", as_index=False)["kwh"].sum()
annual_kwh["ds"] = pd.to_datetime(annual_kwh["year"].astype(str) + "-01-01")
annual_kwh = annual_kwh.rename(columns={"kwh": "y"})
annual_kwh = annual_kwh[["ds", "y"]].sort_values("ds").reset_index(drop=True)

with st.expander("Datenvorschau (Jahre, kWh)", expanded=False):
    st.dataframe(annual_kwh.style.format({"y": "{:,.0f}"}), use_container_width=True)

# CO₂ (kg) – abgeleitet aus kWh × gCO₂/kWh des gewählten Landes
g_intensity = grid.loc[grid["country"] == country, "gco2_per_kwh"].values[0]
annual_co2 = models.groupby("year", as_index=False)["kwh"].sum()
annual_co2["ds"] = pd.to_datetime(annual_co2["year"].astype(str) + "-01-01")
annual_co2["y"]  = annual_co2["kwh"] * g_intensity / 1000.0
annual_co2 = annual_co2[["ds", "y"]].sort_values("ds").reset_index(drop=True)

with st.expander(f"Datenvorschau (Jahre, CO₂ in kg) – {country}", expanded=False):
    st.dataframe(annual_co2.style.format({"y": "{:,.0f}"}), use_container_width=True)

yr_min, yr_max = int(models["year"].min()), int(models["year"].max())
st.subheader(f"📊 Energieverbrauch {yr_min}–{yr_max} Daten")

# Prepare yearly total kWh time series
annual = models.groupby("year", as_index=False)["kwh"].sum().rename(columns={"kwh":"y","year":"ds"})
# Prophet expects a datetime-like 'ds'; convert year to timestamp (Jan 1 of each year)
annual["ds"] = pd.to_datetime(annual["ds"].astype(str) + "-01-01")

with st.expander("Datenvorschau (Jahre, kWh)", expanded=False):
    st.dataframe(annual)

# =======================  FORECAST: Energie & CO2 bis 2030  =======================
st.markdown("---")

# ---------- Datenbasis (global kWh, CO2 landabhängig) ----------
# Jahreswerte (Energie) global
annual_kwh = models.groupby("year", as_index=False)["kwh"].sum().copy()
annual_kwh["ds"] = pd.to_datetime(annual_kwh["year"].astype(int).astype(str) + "-01-01")
annual_kwh = annual_kwh.rename(columns={"kwh": "y"})

# CO2 für gewähltes Land
g_intensity = grid.loc[grid["country"] == country, "gco2_per_kwh"].values[0]
annual_co2 = models.groupby("year", as_index=False)["kwh"].sum().copy()
annual_co2["co2_kg"] = annual_co2["kwh"] * g_intensity / 1000.0
annual_co2["ds"] = pd.to_datetime(annual_co2["year"].astype(int).astype(str) + "-01-01")
annual_co2 = annual_co2.rename(columns={"co2_kg": "y"})

# ---------- Prophet-Helferfunktion ----------
def make_prophet_forecast(df_dsy: pd.DataFrame, horizon_year: int = 2030):
    m = Prophet()
    m.fit(df_dsy[["ds", "y"]])
    last_year = int(df_dsy["ds"].dt.year.max())
    periods = max(0, horizon_year - last_year)
    future = m.make_future_dataframe(periods=periods, freq="Y")
    fc = m.predict(future)
    # exakt zwei Rückgaben: (Historie, Forecast)
    return df_dsy.copy(), fc[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()

# ---------- Forecasts berechnen ----------
energy_actual, energy_fc = make_prophet_forecast(annual_kwh, horizon_year=2030)
co2_actual,    co2_fc    = make_prophet_forecast(annual_co2,  horizon_year=2030)

# ---------- Visualisierung in Tabs ----------
tab1, tab2 = st.tabs(["⚡ Energie (kWh)", "🌍 CO₂ (kg)"])

with tab1:
    fig_e = px.line(energy_fc, x="ds", y="yhat", title="Prognose Energieverbrauch bis 2030 (kWh)")
    fig_e.add_scatter(x=energy_actual["ds"], y=energy_actual["y"], mode="markers+lines", name="Reale Daten")
    fig_e.add_scatter(x=energy_fc["ds"], y=energy_fc["yhat_lower"], mode="lines", name="Konfidenz (unten)", line=dict(dash="dot"))
    fig_e.add_scatter(x=energy_fc["ds"], y=energy_fc["yhat_upper"], mode="lines", name="Konfidenz (oben)",  line=dict(dash="dot"))
    fig_e.update_layout(xaxis_title="Jahr", yaxis_title="kWh")
    st.plotly_chart(fig_e, use_container_width=True)

with tab2:
    fig_c = px.line(co2_fc, x="ds", y="yhat", title=f"Prognose CO₂-Emissionen bis 2030 (kg) – Standort: {country}")
    fig_c.add_scatter(x=co2_actual["ds"], y=co2_actual["y"], mode="markers+lines", name="Reale Daten")
    fig_c.add_scatter(x=co2_fc["ds"], y=co2_fc["yhat_lower"], mode="lines", name="Konfidenz (unten)", line=dict(dash="dot"))
    fig_c.add_scatter(x=co2_fc["ds"], y=co2_fc["yhat_upper"], mode="lines", name="Konfidenz (oben)",  line=dict(dash="dot"))
    fig_c.update_layout(xaxis_title="Jahr", yaxis_title="kg CO₂")
    st.plotly_chart(fig_c, use_container_width=True)

st.caption("Hinweis: Energie (kWh) ist global aus den CSV-Jahressummen abgeleitet. "
           "CO₂ = kWh × gCO₂/kWh des ausgewählten Landes. Prophet extrapoliert bis 2030.")

# ---------- (Optional) Ländervergleich: CO₂-Forecasts nebeneinander ----------
st.markdown("---")
st.subheader("🌍 Ländervergleich: CO₂-Prognose bis 2030 (gleiche kWh-Basis, unterschiedl. Strommix)")

compare_countries = st.multiselect(
    "Länder auswählen",
    options=grid["country"].unique().tolist(),
    default=["US", "DE", "FR"]
)

fig_cmp = go.Figure()
palette = ["#1f77b4","#2ca02c","#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f"]

for i, ctry in enumerate(compare_countries):
    gi = grid.loc[grid["country"] == ctry, "gco2_per_kwh"].values[0]
    co2_series = models.groupby("year", as_index=False)["kwh"].sum().copy()
    co2_series["co2_kg"] = co2_series["kwh"] * gi / 1000.0
    co2_series["ds"] = pd.to_datetime(co2_series["year"].astype(int).astype(str) + "-01-01")
    co2_series = co2_series.rename(columns={"co2_kg": "y"})
    act, fc = make_prophet_forecast(co2_series, horizon_year=2030)
    fig_cmp.add_trace(go.Scatter(x=fc["ds"], y=fc["yhat"], mode="lines",
                                 name=f"{ctry} (Forecast)", line=dict(color=palette[i % len(palette)])))
    fig_cmp.add_trace(go.Scatter(x=act["ds"], y=act["y"], mode="markers",
                                 name=f"{ctry} (Real)", marker=dict(size=6, color=palette[i % len(palette)])))

fig_cmp.update_layout(title="CO₂-Forecast nach Land (gleiche kWh-Basis, Strommix variiert)",
                      xaxis_title="Jahr", yaxis_title="kg CO₂")
st.plotly_chart(fig_cmp, use_container_width=True)
# =====================  /FORECAST: Energie & CO2 bis 2030  =======================

# Fit Prophet model
m = Prophet()
m.fit(annual)

# Make future until 2030
future = m.make_future_dataframe(periods=max(0, 2030 - annual["ds"].dt.year.max()), freq="Y")
forecast = m.predict(future)

# Plot forecast using Plotly
fc = forecast[["ds","yhat","yhat_lower","yhat_upper"]].copy()
hist = annual.rename(columns={"y":"yhat"})

fig2 = px.line(fc, x="ds", y="yhat", title="Prognose jährlicher Gesamtenergie (kWh) bis 2030")
fig2.add_scatter(x=hist["ds"], y=hist["yhat"], mode="markers+lines", name="Historie")
fig2.add_scatter(x=fc["ds"], y=fc["yhat_lower"], mode="lines", name="Konf. Unter", line=dict(dash="dot"))
fig2.add_scatter(x=fc["ds"], y=fc["yhat_upper"], mode="lines", name="Konf. Ober", line=dict(dash="dot"))
fig2.update_layout(xaxis_title="Jahr", yaxis_title="kWh")
st.plotly_chart(fig2, use_container_width=True)

st.info("Hinweis: Forecast basiert auf jährlicher Summe der in 'models_energy.csv' gelisteten Trainingsläufe. "
        "Erweitere die Historie mit zusätzlichen offenen Einträgen, um die Prognose realistischer zu machen.")
