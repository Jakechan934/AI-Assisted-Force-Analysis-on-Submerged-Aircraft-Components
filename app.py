import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Submerged Component Hydrostatic Simulator",
    page_icon="🌊",
    layout="wide"
)

# ==========================================
# HYDROSTATIC ANALYSIS FUNCTION
# ==========================================

def analyze(rho, g, h_top, width, height):

    if rho <= 0 or g <= 0 or width <= 0 or height <= 0 or h_top < 0:
        raise ValueError("Invalid simulation parameters.")

    area = width * height

    h_centroid = h_top + height / 2

    I_G = width * height**3 / 12

    p_top = rho * g * h_top

    p_bottom = rho * g * (h_top + height)

    force = rho * g * h_centroid * area

    h_cp = h_centroid + I_G / (h_centroid * area)

    # Numerical integration

    y = np.linspace(0, height, 10001)

    depth = h_top + y

    pressure = rho * g * depth

    force_num = width * np.trapz(pressure, y)

    h_cp_num = (
        width * np.trapz(pressure * depth, y) / force_num
    )

    return {
        "area": area,
        "h_centroid": h_centroid,
        "I_G": I_G,
        "p_top": p_top,
        "p_bottom": p_bottom,
        "force": force,
        "h_cp": h_cp,
        "force_num": force_num,
        "h_cp_num": h_cp_num,
        "force_error_pct": abs(force_num - force) / force * 100,
        "cp_error_pct": abs(h_cp_num - h_cp) / h_cp * 100
    }


# ==========================================
# WEBSITE TITLE
# ==========================================

st.title("Hydrostatic Force Analysis on a Submerged Component")

st.caption(
    "AI-assisted Fluid Mechanics Simulation | "
    "25PCAS201 | USN: 25BTRAS023"
)

st.markdown(
    "Calculate hydrostatic pressure, resultant force and "
    "centre of pressure for a fully submerged vertical "
    "rectangular plate."
)


# ==========================================
# SIDEBAR INPUTS
# ==========================================

with st.sidebar:

    st.header("Simulation Inputs")

    rho = st.number_input(
        "Fluid density, ρ (kg/m³)",
        min_value=0.001,
        value=1000.0,
        step=10.0
    )

    g = st.number_input(
        "Gravitational acceleration, g (m/s²)",
        min_value=0.001,
        value=9.81,
        step=0.01
    )

    h_top = st.number_input(
        "Depth of top edge, h₀ (m)",
        min_value=0.0,
        value=2.0,
        step=0.1
    )

    width = st.number_input(
        "Plate width, b (m)",
        min_value=0.001,
        value=1.0,
        step=0.1
    )

    height = st.number_input(
        "Plate height, H (m)",
        min_value=0.001,
        value=1.5,
        step=0.1
    )

    run = st.button(
        "Run Simulation",
        type="primary",
        use_container_width=True
    )


# ==========================================
# RUN SIMULATION
# ==========================================

try:

    result = analyze(rho, g, h_top, width, height)

except ValueError as exc:

    st.error(str(exc))
    st.stop()


# ==========================================
# CALCULATED RESULTS
# ==========================================

st.subheader("Calculated Results")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Resultant Force",
    f"{result['force']:,.2f} N",
    f"{result['force']/1000:.3f} kN"
)

c2.metric(
    "Centre of Pressure",
    f"{result['h_cp']:.5f} m"
)

c3.metric(
    "Submerged Area",
    f"{result['area']:.4f} m²"
)

c4, c5, c6 = st.columns(3)

c4.metric(
    "Centroid Depth",
    f"{result['h_centroid']:.4f} m"
)

c5.metric(
    "Pressure at Top",
    f"{result['p_top']:,.2f} Pa"
)

c6.metric(
    "Pressure at Bottom",
    f"{result['p_bottom']:,.2f} Pa"
)

st.divider()


# ==========================================
# GRAPH 1: HYDROSTATIC PRESSURE DISTRIBUTION
# ==========================================

st.subheader("Graph 1: Hydrostatic Pressure Distribution")

y = np.linspace(0, height, 250)

pressure = rho * g * (h_top + y)

fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(
    pressure / 1000,
    y,
    linewidth=2,
    label="Pressure distribution"
)

ax.invert_yaxis()

ax.set_xlabel("Gauge Pressure (kPa)")
ax.set_ylabel("Distance Below Top Edge (m)")

ax.set_title("Hydrostatic Pressure Distribution")

ax.grid(True)

ax.legend()

fig.tight_layout()

st.pyplot(fig)

plt.close(fig)


# ==========================================
# GRAPH 2: RESULTANT FORCE VS IMMERSION DEPTH
# ==========================================

st.subheader("Graph 2: Resultant Force vs Immersion Depth")

depths = np.linspace(
    max(0.0, h_top),
    max(0.5, h_top) + 8,
    150
)

forces = (
    rho * g * width * height *
    (depths + height / 2)
)

fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(
    depths,
    forces / 1000,
    linewidth=2,
    label="Resultant force"
)

ax.scatter(
    [h_top],
    [result["force"] / 1000],
    label="Current input",
    zorder=3
)

ax.set_xlabel("Depth of Top Edge (m)")

ax.set_ylabel("Resultant Force (kN)")

ax.set_title("Resultant Force vs Immersion Depth")

ax.grid(True)

ax.legend()

fig.tight_layout()

st.pyplot(fig)

plt.close(fig)


# ==========================================
# GRAPH 3: CENTRE OF PRESSURE VS DEPTH
# ==========================================

st.subheader("Graph 3: Centre of Pressure vs Immersion Depth")

depths_cp = np.linspace(
    max(0.0, h_top),
    max(0.5, h_top) + 8,
    150
)

centroid_depths = depths_cp + height / 2

cp_depths = (
    centroid_depths +
    height**2 / (12 * centroid_depths)
)

fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(
    depths_cp,
    cp_depths,
    linewidth=2,
    label="Centre of pressure"
)

ax.scatter(
    [h_top],
    [result["h_cp"]],
    label="Current input",
    zorder=3
)

ax.set_xlabel("Depth of Top Edge (m)")

ax.set_ylabel("Centre of Pressure Below Free Surface (m)")

ax.set_title("Centre of Pressure vs Immersion Depth")

ax.grid(True)

ax.legend()

fig.tight_layout()

st.pyplot(fig)

plt.close(fig)


# ==========================================
# GRAPH 4: ANALYTICAL VS NUMERICAL VALIDATION
# ==========================================

st.subheader("Graph 4: Analytical vs Numerical Force Validation")

validation_depths = np.linspace(
    max(0.0, h_top),
    max(0.5, h_top) + 8,
    60
)

analytical_forces = (
    rho * g * width * height *
    (validation_depths + height / 2)
)

y_validation = np.linspace(0, height, 1001)

numerical_forces = np.array([

    width * np.trapz(
        rho * g * (depth_value + y_validation),
        y_validation
    )

    for depth_value in validation_depths

])

fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(
    validation_depths,
    analytical_forces / 1000,
    linewidth=2,
    label="Analytical force"
)

ax.plot(
    validation_depths,
    numerical_forces / 1000,
    linestyle="--",
    linewidth=2,
    label="Numerical integration"
)

ax.scatter(
    [h_top],
    [result["force"] / 1000],
    label="Current input",
    zorder=3
)

ax.set_xlabel("Depth of Top Edge (m)")

ax.set_ylabel("Resultant Force (kN)")

ax.set_title("Analytical vs Numerical Force Validation")

ax.grid(True)

ax.legend()

fig.tight_layout()

st.pyplot(fig)

plt.close(fig)


# ==========================================
# NUMERICAL VALIDATION TABLE
# ==========================================

st.divider()

st.subheader("Numerical Validation")

st.write(
    "The analytical solution is checked using numerical "
    "integration of the pressure distribution over 10,001 points."
)

validation = {

    "Parameter": [
        "Resultant Force",
        "Centre of Pressure"
    ],

    "Analytical Result": [
        f"{result['force']:,.5f} N",
        f"{result['h_cp']:.7f} m"
    ],

    "Numerical Result": [
        f"{result['force_num']:,.5f} N",
        f"{result['h_cp_num']:.7f} m"
    ],

    "Percentage Difference": [
        f"{result['force_error_pct']:.8f}%",
        f"{result['cp_error_pct']:.8f}%"
    ]

}

st.table(validation)


# ==========================================
# GOVERNING EQUATIONS
# ==========================================

st.divider()

st.subheader("Governing Equations")

st.latex(r"p = \rho g h")

st.latex(r"A = bH")

st.latex(r"h_c = h_0 + \frac{H}{2}")

st.latex(r"F = \rho g h_c A")

st.latex(r"I_G = \frac{bH^3}{12}")

st.latex(r"h_{cp} = h_c + \frac{I_G}{h_c A}")


# ==========================================
# MODEL ASSUMPTIONS
# ==========================================

st.subheader("Model Assumptions")

st.info(
    "Static homogeneous liquid, constant density and gravity, "
    "rigid vertical rectangular plate, fully submerged, and "
    "gauge pressure. This is a hydrostatic model; it does not "
    "simulate dynamic water impact or fluid-structure interaction."
)


# ==========================================
# CSV DOWNLOAD
# ==========================================

st.subheader("Download Simulation Results")

csv = (
    "Parameter,Analytical Value,Numerical Value\n"
    f"Area,{result['area']},{result['area']}\n"
    f"Centroid Depth,{result['h_centroid']},{result['h_centroid']}\n"
    f"Top Pressure,{result['p_top']},{result['p_top']}\n"
    f"Bottom Pressure,{result['p_bottom']},{result['p_bottom']}\n"
    f"Resultant Force,{result['force']},{result['force_num']}\n"
    f"Centre of Pressure,{result['h_cp']},{result['h_cp_num']}\n"
)

st.download_button(
    "Download Results (CSV)",
    data=csv,
    file_name="hydrostatic_simulation_results.csv",
    mime="text/csv"
)


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Educational simulation | Fluid Mechanics | 25PCAS201 | "
    "USN: 25BTRAS023"
)

st.caption(
    "Verify calculations and assumptions before using "
    "results in engineering design."
)
