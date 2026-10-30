import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Submerged Component Hydrostatic Simulator",
    page_icon="🌊",
    layout="wide"
)

def analyze(rho, g, h_top, width, height):
    if rho <= 0 or g <= 0 or width <= 0 or height <= 0 or h_top < 0:
        raise ValueError("Density, gravity, width and height must be positive. Top-edge depth cannot be negative.")

    area = width * height
    h_centroid = h_top + height / 2
    I_G = width * height**3 / 12
    p_top = rho * g * h_top
    p_bottom = rho * g * (h_top + height)
    force = rho * g * h_centroid * area
    h_cp = h_centroid + I_G / (h_centroid * area)

    y = np.linspace(0, height, 10001)
    depth = h_top + y
    pressure = rho * g * depth
    force_num = width * np.trapezoid(pressure, y)
    h_cp_num = width * np.trapezoid(pressure * depth, y) / force_num

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
        "cp_error_pct": abs(h_cp_num - h_cp) / h_cp * 100,
    }

st.title("Hydrostatic Force Analysis on a Submerged Component")
st.caption("AI-assisted Fluid Mechanics simulation | 25PCAS201 | USN: 25BTRAS023")
st.markdown(
    "Calculate hydrostatic pressure, resultant force and centre of pressure "
    "for a fully submerged vertical rectangular plate."
)

with st.sidebar:
    st.header("Simulation Inputs")
    rho = st.number_input("Fluid density, ρ (kg/m³)", min_value=0.001, value=1000.0, step=10.0)
    g = st.number_input("Gravitational acceleration, g (m/s²)", min_value=0.001, value=9.81, step=0.01)
    h_top = st.number_input("Depth of top edge, h₀ (m)", min_value=0.0, value=2.0, step=0.1)
    width = st.number_input("Plate width, b (m)", min_value=0.001, value=1.0, step=0.1)
    height = st.number_input("Plate height, H (m)", min_value=0.001, value=1.5, step=0.1)
    run = st.button("Run Simulation", type="primary", use_container_width=True)

if "simulation" not in st.session_state:
    st.session_state.simulation = True

if run or st.session_state.simulation:
    try:
        result = analyze(rho, g, h_top, width, height)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    st.subheader("Calculated Results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Resultant Force", f"{result['force']:,.2f} N", f"{result['force']/1000:.3f} kN")
    c2.metric("Centre of Pressure", f"{result['h_cp']:.5f} m")
    c3.metric("Submerged Area", f"{result['area']:.4f} m²")

    c4, c5, c6 = st.columns(3)
    c4.metric("Centroid Depth", f"{result['h_centroid']:.4f} m")
    c5.metric("Pressure at Top", f"{result['p_top']:,.2f} Pa")
    c6.metric("Pressure at Bottom", f"{result['p_bottom']:,.2f} Pa")

    st.divider()
    left, right = st.columns(2)

    with left:
        st.subheader("Hydrostatic Pressure Distribution")
        y = np.linspace(0, height, 250)
        pressure = rho * g * (h_top + y)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(pressure / 1000, y, linewidth=2)
        ax.invert_yaxis()
        ax.set_xlabel("Gauge pressure (kPa)")
        ax.set_ylabel("Distance below top edge (m)")
        ax.grid(True)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with right:
        st.subheader("Resultant Force vs Immersion Depth")
        depths = np.linspace(max(0.0, h_top), max(0.5, h_top) + 8, 150)
        forces = rho * g * width * height * (depths + height / 2) / 1000
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(depths, forces, linewidth=2)
        ax.scatter([h_top], [result["force"] / 1000], zorder=3, label="Current input")
        ax.set_xlabel("Depth of top edge (m)")
        ax.set_ylabel("Resultant force (kN)")
        ax.grid(True)
        ax.legend()
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    st.subheader("Numerical Validation")
    st.write(
        "The analytical solution is checked using numerical integration of the "
        "pressure distribution over 10,001 points."
    )
    validation = {
        "Parameter": ["Resultant force", "Centre of pressure"],
        "Analytical result": [
            f"{result['force']:,.5f} N",
            f"{result['h_cp']:.7f} m below free surface"
        ],
        "Numerical result": [
            f"{result['force_num']:,.5f} N",
            f"{result['h_cp_num']:.7f} m below free surface"
        ],
        "Percentage difference": [
            f"{result['force_error_pct']:.8f}%",
            f"{result['cp_error_pct']:.8f}%"
        ]
    }
    st.table(validation)

    st.subheader("Governing Equations")
    st.latex(r"p = \\rho g h")
    st.latex(r"A = bH, \\qquad h_c = h_0 + \\frac{H}{2}")
    st.latex(r"F = \\rho g h_c A")
    st.latex(r"I_G = \\frac{bH^3}{12}, \\qquad h_{cp} = h_c + \\frac{I_G}{h_c A}")

    st.info(
        "Model assumptions: static homogeneous liquid, constant density and gravity, "
        "rigid vertical rectangular plate, fully submerged, and gauge pressure. "
        "This is a hydrostatic model; it does not simulate dynamic water impact or "
        "fluid–structure interaction."
    )

    csv = (
        "Parameter,Analytical value,Numerical value\\n"
        f"Area,{result['area']},{result['area']}\\n"
        f"Centroid depth,{result['h_centroid']},{result['h_centroid']}\\n"
        f"Top pressure,{result['p_top']},{result['p_top']}\\n"
        f"Bottom pressure,{result['p_bottom']},{result['p_bottom']}\\n"
        f"Resultant force,{result['force']},{result['force_num']}\\n"
        f"Centre of pressure,{result['h_cp']},{result['h_cp_num']}\\n"
    )
    st.download_button(
        "Download Results (CSV)",
        data=csv,
        file_name="hydrostatic_simulation_results.csv",
        mime="text/csv"
    )

st.caption("Educational simulation. Verify calculations and assumptions before using results in engineering design.")
