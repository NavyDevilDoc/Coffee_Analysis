# Coffee cooling time comparison between preheated and non-preheated mug

# Assumptions: Coffee temperature in the pot is uniformly distrubuted at 180 deg F
# and interactions at the boundaries produce negligible temperature difference.


import numpy as np
import matplotlib.pyplot as plt

def newtons_law_cooling(T0, Ta, k, t):
    """Compute the temperature at time t, given an initial temperature T0, 
    an ambient temperature Ta, and a cooling constant k according to 
    Newton's law of cooling."""
    return Ta + (T0 - Ta) * np.exp(-k * t)

def cooling_time(T0, Ta, k, T_target):
    """Compute the time it takes for the temperature to reach a target 
    temperature T_target, given an initial temperature T0, an ambient 
    temperature Ta, and a cooling constant k."""
    return -np.log((T_target - Ta) / (T0 - Ta)) / k

def newtons_law_cooling_with_creamer(T0, Ta, k, t, T_creamer, v_creamer, v_coffee, t_add):
    """Compute the temperature at time t, given an initial temperature T0, 
    an ambient temperature Ta, a cooling constant k, the time t, the 
    temperature T_creamer and volume v_creamer of the creamer, the volume 
    v_coffee of the coffee, and the time t_add at which the creamer is added."""
    T_no_creamer = Ta + (T0 - Ta) * np.exp(-k * t)
    T_with_creamer = (v_coffee * T_no_creamer + v_creamer * T_creamer) / (v_coffee + v_creamer)
    return np.where(t <= t_add, T_no_creamer, T_with_creamer)


# Parameters
h_cup = 4 * 0.0254 # height of the cup (m), converted from inches
d_cup = 3 * 0.0254 # diameter of the cup (m), converted from inches
t_cup = 0.1825 * 0.0254 # thickness of the cup (m), converted from inches
rho_ceramic = 3000 # density of ceramic (kg/m^3)
c_ceramic = 900 # specific heat capacity of ceramic (J/kg°C)
rho_coffee = 1000 # density of coffee (approximately water) in kg/m^3
c_coffee = 4186 # specific heat capacity of coffee (approximately water) in J/kg°C

V_cup = np.pi * (d_cup / 2) ** 2 * h_cup # volume of the cup (m^3)
V_cup_wall = np.pi * ((d_cup / 2) ** 2 - ((d_cup - 2 * t_cup) / 2) ** 2) * h_cup # volume of the cup wall (m^3)
m_cup = rho_ceramic * V_cup_wall # mass of the cup (kg)
C_cup = m_cup * c_ceramic # heat capacity of the cup (J/°C)

m_coffee = rho_coffee * V_cup # mass of the coffee (kg)
C_coffee = m_coffee * c_coffee # heat capacity of the coffee (J/°C)

T0_cold_cup = 21 # initial temperature of the cold cup (°C)
T0_hot_cup = 55 # initial temperature of the preheated cup (°C)
T0_coffee = 74 # initial temperature of the coffee (°C)
Ta = T0_cold_cup # room temperature (°C)
k_coffee = 0.02 # cooling constant of the coffee (1/min), arbitrarily chosen for this example
k_cup = 0.02 # cooling constant of the cup (1/min), arbitrarily chosen for this example
T_target = 45 # target drinkable temperature (°C)

T0_cold = (T0_coffee + C_cup / (C_cup + C_coffee) * (T0_cold_cup - T0_coffee))
T0_hot = (T0_coffee + C_cup / (C_cup + C_coffee) * (T0_hot_cup - T0_coffee))

time_cold = cooling_time(T0_cold, Ta, k_coffee, T_target)
time_hot = cooling_time(T0_hot, Ta, k_coffee, T_target)

print("Cold cup cooling time (min):", time_cold)
print("Hot cup cooling time (min):", time_hot)

# Parameters for the creamer
T_creamer = (38 - 32) * 5 / 9  # Convert from Fahrenheit to Celsius
v_creamer = 50 / 1000  # Convert from ml to l
t_add = 0.5  # Time of addition of the creamer (minutes)
v_coffee = V_cup * 1000  # Convert volume of the coffee from m^3 to l

# Compute new cooling times and temperatures with creamer
T0_hot_creamer = (v_coffee * T0_hot + v_creamer * T_creamer) / (v_coffee + v_creamer)
time_hot_creamer = cooling_time(T0_hot_creamer, Ta, k_coffee, T_target)

print("Hot cup with creamer cooling time (min):", time_hot_creamer)

t = np.linspace(0, 60, 1000) # time; should be one hour
T_cold = newtons_law_cooling(T0_cold, Ta, k_coffee, t)
T_hot = newtons_law_cooling(T0_hot, Ta, k_coffee, t)
T_hot_creamer = newtons_law_cooling_with_creamer(T0_hot, Ta, k_coffee, t, T_creamer, v_creamer, v_coffee, t_add)

plt.plot(t, T_cold, label='Cold cup', color='blue')
plt.plot(t, T_hot, label='Hot cup', color='orange')
plt.plot(t, T_hot_creamer, label='Hot cup with creamer', color='green')

plt.axhline(T_target, color='red', linestyle='--', label='Target temp')

plt.axvline(time_cold, 0, (T_target-Ta)/(T0_cold-Ta), color='blue', linestyle='--')
plt.axvline(time_hot, 0, (T_target-Ta)/(T0_hot-Ta), color='orange', linestyle='--')
plt.axvline(time_hot_creamer, 0, (T_target-Ta)/(T0_hot_creamer-Ta), color='green', linestyle='--')

# Generate equations for the curves
equation_cold = f"T(t) = {Ta:.3f} + ({T0_cold:.3f} - {Ta:.3f}) * e^(-{k_coffee:.3f}t)"
equation_hot = f"T(t) = {Ta:.3f} + ({T0_hot:.3f} - {Ta:.3f}) * e^(-{k_coffee:.3f}t)"
equation_hot_creamer = f"T(t) = {Ta:.3f} + ({T0_hot_creamer:.3f} - {Ta:.3f}) * e^(-{k_coffee:.3f}t) (t < {t_add}) / ({T0_hot:.3f} with creamer (t >= {t_add}))"

plt.legend(loc='upper right')
plt.xlabel('Time (min)')
plt.ylabel('Temperature (deg C)')
plt.title('Cooling of Coffee in Room Temp and Preheated Cups')
plt.show()
