import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. UTILITY FUNCTIONS ---
def to_celsius(f):
    return (f - 32) * 5.0 / 9.0

def to_fahrenheit(c):
    return (c * 9.0 / 5.0) + 32

# --- 2. PHYSICS ENGINE (Internal Logic in Metric/Celsius) ---
def newtons_law_cooling(T0, Ta, k, t):
    """Standard exponential cooling."""
    return Ta + (T0 - Ta) * np.exp(-k * t)

def simulate_creamer_addition(T0_coffee, Ta, k, t_array, T_creamer, v_creamer, v_coffee, t_add):
    """
    Simulates cooling with an event-based volume/temp change.
    Inputs must be consistent (e.g., all Celsius, all Liters).
    """
    # 1. Pre-mixing phase
    mask_before = t_array <= t_add
    t_before = t_array[mask_before]
    T_before = newtons_law_cooling(T0_coffee, Ta, k, t_before)
    
    if len(t_before) == 0: # Edge case: adding at t=0
        T_mixture_start = (v_coffee * T0_coffee + v_creamer * T_creamer) / (v_coffee + v_creamer)
        return newtons_law_cooling(T_mixture_start, Ta, k, t_array)

    # 2. Mixing Event
    T_coffee_at_moment = T_before[-1]
    
    # Weighted Average Mixing
    T_mixture_start = (v_coffee * T_coffee_at_moment + v_creamer * T_creamer) / (v_coffee + v_creamer)
    
    # 3. Post-mixing phase
    mask_after = t_array > t_add
    t_after = t_array[mask_after]
    
    t_elapsed = t_after - t_add
    T_after = newtons_law_cooling(T_mixture_start, Ta, k, t_elapsed)
    
    return np.concatenate((T_before, T_after))

def calculate_initial_equilibrium(T0_liquid, m_liquid, c_liquid, T0_cup, m_cup, c_cup):
    """Calculates equilibrium temp of cup+liquid at t=0 (Lumped Capacitance)."""
    C_liquid = m_liquid * c_liquid
    C_cup = m_cup * c_cup
    return (T0_liquid * C_liquid + T0_cup * C_cup) / (C_cup + C_liquid)

# --- 3. STREAMLIT UI ---
st.set_page_config(page_title="Thermodynamics of Coffee", layout="wide")

st.title("☕ The Thermodynamics of Coffee Cooling")
st.markdown("Comparison of cooling strategies using **Newton's Law of Cooling**.")

# --- Sidebar Controls (Fahrenheit) ---
st.sidebar.header("Experimental Parameters")

with st.sidebar.expander("🌡️ Temperatures & Environment", expanded=True):
    # Inputs in Fahrenheit
    Ta_f = st.number_input("Room Temp (°F)", value=70.0, step=1.0)
    T0_coffee_f = st.number_input("Initial Coffee Temp (°F)", value=170.0, step=1.0)
    T_target_f = st.slider("Target 'Drinkable' Temp (°F)", 100, 150, 120)
    k_coffee = st.slider("Cooling Constant k (1/min)", 0.01, 0.10, 0.025, step=0.005, format="%.3f")

with st.sidebar.expander("🍶 Creamer Injection Strategy", expanded=True):
    t_add = st.slider("Time of Addition (min)", 0.0, 30.0, 0.0, step=0.5)
    T_creamer_f = st.number_input("Creamer Temp (°F)", value=40.0) # Fridge temp
    vol_ratio = st.slider("Creamer Volume (% of cup)", 1, 20, 5)
    
with st.sidebar.expander("🧱 Cup Properties (Advanced)"):
    # Preheated cup in F
    T0_hot_cup_f = st.number_input("Preheated Cup Temp (°F)", value=140.0)
    
    # Physics Constants (Metric)
    rho_coffee = 1000   # kg/m^3
    c_coffee = 4186     # J/kgC
    h_cup = 0.10        # m
    d_cup = 0.08        # m
    t_cup = 0.005       # m
    rho_ceramic = 3000  # kg/m^3
    c_ceramic = 900     # J/kgC
    
    # Calculate Masses
    V_cup_m3 = np.pi * (d_cup / 2) ** 2 * h_cup
    V_cup_wall_m3 = np.pi * ((d_cup / 2) ** 2 - ((d_cup - 2 * t_cup) / 2) ** 2) * h_cup
    m_cup = rho_ceramic * V_cup_wall_m3
    m_coffee = rho_coffee * V_cup_m3
    
    v_coffee_L = V_cup_m3 * 1000
    v_creamer_L = v_coffee_L * (vol_ratio / 100)

# --- 4. RUN SIMULATION ---

# Convert User Inputs (F) -> Physics Engine (C)
Ta_c = to_celsius(Ta_f)
T0_coffee_c = to_celsius(T0_coffee_f)
T_creamer_c = to_celsius(T_creamer_f)
T0_hot_cup_c = to_celsius(T0_hot_cup_f)
T0_cold_cup_c = Ta_c # Assume cold cup is at room temp

# Calculate Initial States (Thermal Equilibrium in C)
T0_start_cold_c = calculate_initial_equilibrium(T0_coffee_c, m_coffee, c_coffee, T0_cold_cup_c, m_cup, c_ceramic)
T0_start_hot_c = calculate_initial_equilibrium(T0_coffee_c, m_coffee, c_coffee, T0_hot_cup_c, m_cup, c_ceramic)

# Time array
t = np.linspace(0, 60, 1000)

# Generate Curves (in C)
y_cold_c = newtons_law_cooling(T0_start_cold_c, Ta_c, k_coffee, t)
y_hot_c = newtons_law_cooling(T0_start_hot_c, Ta_c, k_coffee, t)
y_creamer_c = simulate_creamer_addition(T0_start_hot_c, Ta_c, k_coffee, t, T_creamer_c, v_creamer_L, v_coffee_L, t_add)

# Convert Curves back to F for Plotting
y_cold = to_fahrenheit(y_cold_c)
y_hot = to_fahrenheit(y_hot_c)
y_creamer = to_fahrenheit(y_creamer_c)

# Find Crossing Times
def find_crossing_time(t, y, target):
    if np.min(y) > target: return None
    idx = np.argmax(y <= target)
    return t[idx]

time_cold = find_crossing_time(t, y_cold, T_target_f)
time_hot = find_crossing_time(t, y_hot, T_target_f)
time_creamer = find_crossing_time(t, y_creamer, T_target_f)

# --- 5. VISUALIZATION ---
col1, col2 = st.columns([3, 1])

with col1:
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(t, y_cold, label='Cold Cup', color='#1f77b4', linewidth=2)
    ax.plot(t, y_hot, label='Preheated Cup', color='#ff7f0e', linewidth=2)
    ax.plot(t, y_creamer, label=f'Preheated + Creamer (@ {t_add}m)', color='#2ca02c', linewidth=2, linestyle='-')
    
    # Target Line
    ax.axhline(T_target_f, color='red', linestyle='--', alpha=0.5, label=f'Target ({T_target_f}°F)')
    
    # Drop Lines
    if time_cold: ax.vlines(time_cold, 0, T_target_f, colors='#1f77b4', linestyles=':', alpha=0.5)
    if time_hot: ax.vlines(time_hot, 0, T_target_f, colors='#ff7f0e', linestyles=':', alpha=0.5)
    if time_creamer: ax.vlines(time_creamer, 0, T_target_f, colors='#2ca02c', linestyles=':', alpha=0.5)

    ax.set_xlabel('Time (minutes)')
    ax.set_ylabel('Temperature (°F)')
    ax.set_title('Coffee Cooling Profiles')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Dynamic limits based on F
    ax.set_ylim(Ta_f - 5, T0_coffee_f + 5)
    ax.set_xlim(0, 60)
    
    st.pyplot(fig)

with col2:
    st.subheader("Results")
    st.markdown("Time to reach target:")
    
    def display_metric(label, val, ref=None):
        if val is None:
            st.metric(label, "> 60 min")
        else:
            delta = None
            if ref is not None and val is not None:
                delta = f"{val - ref:.1f} min"
            st.metric(label, f"{val:.1f} min", delta=delta, delta_color="inverse")

    display_metric("Cold Cup", time_cold)
    display_metric("Preheated Cup", time_hot, ref=time_cold)
    display_metric("With Creamer", time_creamer, ref=time_hot)
    
    st.info("The physics engine runs in Celsius (Metric) internally to keep Specific Heat constants correct, but inputs/outputs are converted to Fahrenheit for you.")
