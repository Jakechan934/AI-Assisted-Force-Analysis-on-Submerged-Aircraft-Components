import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Submerged Aircraft Component Simulation",
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

    centroid_depth = h_top + height / 2

    I_G = width * height**3 / 12

    top_pressure = rho * g * h_top

    bottom_pressure = rho * g * (h_top + height)

    resultant_force = rho * g * centroid_depth * area

    centre_of_pressure = (
        centroid_depth + I_G / (area * centroid_depth)
    )

    # Numerical integration

    y = np.linspace(0, height, 10001)

    depth = h_top + y

    pressure = rho * g * depth

    numerical_force = width * np.trapezoid(pressure, y)

    numerical_cp = (
        width * np.trapezoid(pressure * depth, y)
        / numerical_force
    )

    force_error = (
        abs(numerical_force - resultant_force)
        / resultant_force * 100
    )

    cp_error = (
        abs(numerical_cp - centre_of_pressure)
        / centre_of_pressure * 100
    )

    return {
        "area": area,
        "centroid_depth": centroid_depth,
        "I_G": I_G,
        "top_pressure": top_pressure,
        "bottom_pressure": bottom_pressure,
        "force": resultant_force,
        "cp": centre_of_pressure,
        "numerical_force": numerical_force,
        "numerical_cp": numerical_cp,
        "force_error": force_error,
        "cp_error": cp_error
    }


# ==========================================
# WEBSITE HEADER
# ==========================================

st.title(
    "Hydrostatic Force Analysis on a Submerged Component"
)

st.caption(
    "AI-Assisted Fluid Mechanics Simulation | "
    "25PCAS201 | USN: 25BTRAS023"
)

st.write(
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

    st.markdown("---")

    run = st.button(
        "Run Simulation",
        type="primary",
        use_container_width=True
    )


# ==========================================
# PERFORM CALCULATIONS
# ==========================================

try:

    result = analyze(
        rho, g, h_top, width, height
    )

except ValueError as error:

    st.error(str(error))
    st.stop()


# ==========================================
# CALCULATED RESULTS
# ==========================================

st.subheader("Calculated Results")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Resultant Force",
    f"{result['force']:,.2f} N",
    f"{result['force']/1000:.3f} kN"
)

col2.metric(
    "Centre of Pressure",
    f"{result['cp']:.5f} m"
)

col3.metric(
    "Submerged Area",
    f"{result['area']:.4f} m²"
)

col4, col5, col6 = st.columns(3)

col4.metric(
    "Centroid Depth",
    f"{result['centroid_depth']:.4f} m"
)

col5.metric(
    "Pressure at Top",
    f"{result['top_pressure']:,.2f} Pa"
)

col6.metric(
    "Pressure at Bottom",
    f"{result['bottom_pressure']:,.2f} Pa"
)

st.divider()


# ==========================================
# GRAPH 1: HYDROSTATIC PRESSURE DISTRIBUTION
# ==========================================

st.subheader(
    "Graph 1: Hydrostatic Pressure Distribution"
)

y = np.linspace(0, height, 250)

pressure = rho * g * (h_top + y)

fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(
    pressure / 1000,
    y,
    linewidth=2,
    label="Pressure distribution"
)

ax.fill_betweenx(
    y,
    0,
    pressure / 1000,
    alpha=0.15
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

st.subheader(
    "Graph 2: Resultant Force vs Immersion Depth"
)

depths = np.linspace(
    max(0.0, h_top),
    max(0.5, h_top) + 8,
    150
)

forces = (
    rho * g * width * height *
    (depths + height / 2)
)

fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(
    depths,
    forces / 1000,
    linewidth=2,
    label="Resultant force"
)

ax.scatter(
    [h_top],
    [result["force"] / 1000],
    s=70,
    label="Current input",
    zorder=3
)

ax.set_xlabel("Depth of Top Edge (m)")
ax.set_ylabel("Resultant Force (kN)")

ax.set_title(
    "Resultant Force vs Immersion Depth"
)

ax.grid(True)
ax.legend()

fig.tight_layout()

st.pyplot(fig)

plt.close(fig)


# ==========================================
# GRAPH 3: CENTRE OF PRESSURE VS DEPTH
# ==========================================

st.subheader(
    "Graph 3: Centre of Pressure vs Immersion Depth"
)

depths_cp = np.linspace(
    max(0.0, h_top),
    max(0.5, h_top) + 8,
    150
)

centroid_depths = depths_cp + height / 2

cp_values = (
    centroid_depths +
    height**2 / (12 * centroid_depths)
)

fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(
    depths_cp,
    cp_values,
    linewidth=2,
    label="Centre of pressure"
)

ax.scatter(
    [h_top],
    [result["cp"]],
    s=70,
    label="Current input",
    zorder=3
)

ax.set_xlabel("Depth of Top Edge (m)")

ax.set_ylabel(
    "Centre of Pressure Below Free Surface (m)"
)

ax.set_title(
    "Centre of Pressure vs Immersion Depth"
)

ax.grid(True)
ax.legend()

fig.tight_layout()

st.pyplot(fig)

plt.close(fig)


# ==========================================
# GRAPH 4: ANALYTICAL VS NUMERICAL VALIDATION
# ==========================================

st.subheader(
    "Graph 4: Analytical vs Numerical Force Validation"
)

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

numerical_forces = []

for depth_value in validation_depths:

    pressure_values = (
        rho * g * (depth_value + y_validation)
    )

    numerical_force = (
        width * np.trapezoid(
            pressure_values,
            y_validation
        )
    )

    numerical_forces.append(numerical_force)

numerical_forces = np.array(numerical_forces)

fig, ax = plt.subplots(figsize=(9, 5))

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
    s=70,
    label="Current input",
    zorder=3
)

ax.set_xlabel("Depth of Top Edge (m)")
ax.set_ylabel("Resultant Force (kN)")

ax.set_title(
    "Analytical vs Numerical Force Validation"
)

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
    "The analytical solution is compared with numerical "
    "integration of the hydrostatic pressure distribution."
)

validation_table = {

    "Parameter": [
        "Resultant Force",
        "Centre of Pressure"
    ],

    "Analytical Result": [
        f"{result['force']:,.5f} N",
        f"{result['cp']:.7f} m"
    ],

    "Numerical Result": [
        f"{result['numerical_force']:,.5f} N",
        f"{result['numerical_cp']:.7f} m"
    ],

    "Percentage Difference": [
        f"{result['force_error']:.8f}%",
        f"{result['cp_error']:.8f}%"
    ]

}

st.table(validation_table)


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

st.latex(
    r"h_{cp} = h_c + \frac{I_G}{h_c A}"
)


# ==========================================
# MODEL ASSUMPTIONS
# ==========================================

st.subheader("Model Assumptions")

st.info(
    "1. Static homogeneous liquid.\n\n"
    "2. Constant fluid density and gravitational acceleration.\n\n"
    "3. Rigid vertical rectangular plate.\n\n"
    "4. Plate is fully submerged.\n\n"
    "5. Gauge pressure is considered.\n\n"
    "6. Dynamic fluid impact and fluid-structure interaction "
    "are not included."
)


# ==========================================
# CSV DOWNLOAD
# ==========================================

st.divider()

st.subheader("Download Simulation Results")

csv_data = (
    "Parameter,Analytical Value,Numerical Value\n"
    f"Area,{result['area']},{result['area']}\n"
    f"Centroid Depth,{result['centroid_depth']},"
    f"{result['centroid_depth']}\n"
    f"Top Pressure,{result['top_pressure']},"
    f"{result['top_pressure']}\n"
    f"Bottom Pressure,{result['bottom_pressure']},"
    f"{result['bottom_pressure']}\n"
    f"Resultant Force,{result['force']},"
    f"{result['numerical_force']}\n"
    f"Centre of Pressure,{result['cp']},"
    f"{result['numerical_cp']}\n"
)

st.download_button(
    label="Download Results (CSV)",
    data=csv_data,
    file_name="hydrostatic_simulation_results.csv",
    mime="text/csv"
)


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Educational Simulation | Fluid Mechanics | "
    "25PCAS201 | USN: 25BTRAS023"
)

st.caption(
    "Verify calculations and assumptions before "
    "using results in engineering design."
)
