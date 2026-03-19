import math
import streamlit as st

st.set_page_config(page_title="CT Reel Calculator", page_icon="🧮", layout="wide")


def mm_to_m(x_mm: float) -> float:
    return x_mm / 1000.0


def inch_to_m(x_in: float) -> float:
    return x_in * 0.0254


def m_to_mm(x_m: float) -> float:
    return x_m * 1000.0


def m_to_inch(x_m: float) -> float:
    return x_m / 0.0254


def calc_turns_per_layer(width_m: float, tubing_od_m: float, pitch_factor: float = 1.0) -> float:
    pitch_m = tubing_od_m * pitch_factor
    return width_m / pitch_m


def calc_layers(core_d_m: float, outer_d_m: float, tubing_od_m: float) -> float:
    return (outer_d_m - core_d_m) / (2.0 * tubing_od_m)


def calc_total_turns(turns_per_layer: float, layers: float) -> float:
    return turns_per_layer * layers


def calc_length_from_geometry(width_m: float, tubing_od_m: float, core_d_m: float, outer_d_m: float, pitch_factor: float = 1.0) -> float:
    # L ≈ πW/(4 d p) * (Do^2 - Dc^2), with p = pitch_factor*d
    pitch_m = tubing_od_m * pitch_factor
    return math.pi * width_m * (outer_d_m**2 - core_d_m**2) / (4.0 * tubing_od_m * pitch_m)


def calc_outer_diameter(length_m: float, width_m: float, tubing_od_m: float, core_d_m: float, pitch_factor: float = 1.0) -> float:
    # Do ≈ sqrt(Dc^2 + 4 L d p / (πW)), with p = pitch_factor*d
    pitch_m = tubing_od_m * pitch_factor
    inside = core_d_m**2 + (4.0 * length_m * tubing_od_m * pitch_m) / (math.pi * width_m)
    return math.sqrt(inside)


def calc_average_diameter(core_d_m: float, outer_d_m: float) -> float:
    return 0.5 * (core_d_m + outer_d_m)


def calc_turns_from_average_diameter(length_m: float, avg_d_m: float) -> float:
    return length_m / (math.pi * avg_d_m)


st.title("Coiled Tubing Reel Calculator")
st.write(
    "Estimate reel capacity, required outer diameter, turns per layer, number of radial layers, and total windings."
)

with st.sidebar:
    st.header("Inputs")
    units = st.selectbox("Input units", ["Metric (m, mm)", "Oilfield (m, inch for diameters)"])
    mode = st.radio(
        "Calculation mode",
        [
            "Known outer diameter → calculate windings and capacity",
            "Known length → calculate required outer diameter and windings",
        ],
    )
    pitch_factor = st.number_input(
        "Winding pitch factor",
        min_value=1.0,
        max_value=1.3,
        value=1.00,
        step=0.01,
        help="1.00 means side-by-side packing with pitch equal to tubing OD. Use a slightly higher value for looser packing.",
    )

left, right = st.columns(2)

with left:
    st.subheader("Geometry")

    if units == "Metric (m, mm)":
        length_m = st.number_input("Tubing length [m]", min_value=0.0, value=4000.0, step=100.0)
        tubing_od_m = mm_to_m(st.number_input("Tubing OD [mm]", min_value=1.0, value=50.8, step=1.0))
        width_m = st.number_input("Usable reel width W [m]", min_value=0.1, value=2.0, step=0.1)
        core_d_m = st.number_input("Core diameter Dc [m]", min_value=0.1, value=2.35, step=0.05)
        outer_d_input_m = st.number_input("Outer wound diameter Do [m]", min_value=0.1, value=3.48, step=0.05)
    else:
        length_m = st.number_input("Tubing length [m]", min_value=0.0, value=4000.0, step=100.0)
        tubing_od_m = inch_to_m(st.number_input("Tubing OD [in]", min_value=0.1, value=2.0, step=0.125))
        width_m = inch_to_m(st.number_input("Usable reel width W [in]", min_value=1.0, value=78.7, step=1.0))
        core_d_m = inch_to_m(st.number_input("Core diameter Dc [in]", min_value=1.0, value=92.5, step=1.0))
        outer_d_input_m = inch_to_m(st.number_input("Outer wound diameter Do [in]", min_value=1.0, value=137.0, step=1.0))

    if width_m <= 0 or tubing_od_m <= 0:
        st.error("Width and tubing OD must be greater than zero.")
        st.stop()

    if mode == "Known outer diameter → calculate windings and capacity":
        outer_d_m = outer_d_input_m
        if outer_d_m <= core_d_m:
            st.error("Outer diameter must be greater than core diameter.")
            st.stop()
    else:
        outer_d_m = calc_outer_diameter(length_m, width_m, tubing_od_m, core_d_m, pitch_factor)
        if outer_d_m <= core_d_m:
            st.error("Calculated outer diameter is not valid. Check inputs.")
            st.stop()

turns_per_layer = calc_turns_per_layer(width_m, tubing_od_m, pitch_factor)
layers = calc_layers(core_d_m, outer_d_m, tubing_od_m)
total_turns_grid = calc_total_turns(turns_per_layer, layers)
capacity_length_m = calc_length_from_geometry(width_m, tubing_od_m, core_d_m, outer_d_m, pitch_factor)
avg_d_m = calc_average_diameter(core_d_m, outer_d_m)
total_turns_avg = calc_turns_from_average_diameter(capacity_length_m if mode.startswith("Known outer diameter") else length_m, avg_d_m)
selected_length_m = capacity_length_m if mode.startswith("Known outer diameter") else length_m
fill_ratio = selected_length_m / capacity_length_m if capacity_length_m > 0 else float('nan')

with right:
    st.subheader("Results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Turns per layer", f"{turns_per_layer:.1f}")
    c2.metric("Radial layers", f"{layers:.1f}")
    c3.metric("Total windings", f"{total_turns_grid:.0f}")

    c4, c5, c6 = st.columns(3)
    c4.metric("Outer diameter Do", f"{outer_d_m:.3f} m")
    c5.metric("Capacity from geometry", f"{capacity_length_m:.0f} m")
    c6.metric("Avg-diameter turns", f"{total_turns_avg:.0f}")

    st.write("### Converted dimensions")
    st.write(
        f"Tubing OD = **{m_to_mm(tubing_od_m):.1f} mm** = **{m_to_inch(tubing_od_m):.3f} in**  \\\n"
        f"Width W = **{width_m:.3f} m** = **{m_to_inch(width_m):.1f} in**  \\\n"
        f"Core diameter Dc = **{core_d_m:.3f} m** = **{m_to_inch(core_d_m):.1f} in**  \\\n"
        f"Outer diameter Do = **{outer_d_m:.3f} m** = **{m_to_inch(outer_d_m):.1f} in**"
    )

st.write("---")

st.subheader("Interpretation")
if mode == "Known outer diameter → calculate windings and capacity":
    st.write(
        f"With the entered geometry, the reel capacity is about **{capacity_length_m:.0f} m** of tubing. "
        f"That corresponds to about **{turns_per_layer:.1f} turns per layer**, **{layers:.1f} radial layers**, "
        f"and **{total_turns_grid:.0f} total windings**."
    )
else:
    st.write(
        f"To fit **{length_m:.0f} m** of tubing on this reel, the required outer wound diameter is about **{outer_d_m:.3f} m**. "
        f"That corresponds to about **{turns_per_layer:.1f} turns per layer**, **{layers:.1f} radial layers**, "
        f"and **{total_turns_grid:.0f} total windings**."
    )

st.subheader("Formulas used")
st.latex(r"N_w \approx \frac{W}{p}, \qquad p = \text{pitch factor} \cdot d")
st.latex(r"N_r \approx \frac{D_o - D_c}{2d}")
st.latex(r"N \approx N_w N_r")
st.latex(r"L \approx \frac{\pi W}{4 d p}\left(D_o^2 - D_c^2\right)")
st.latex(r"D_o \approx \sqrt{D_c^2 + \frac{4 L d p}{\pi W}}")

with st.expander("Notes and assumptions"):
    st.markdown(
        """
- This is an engineering estimate based on idealized side-by-side winding.
- The **pitch factor** lets you account for looser packing. Use **1.00** for ideal packing and perhaps **1.02–1.10** for more conservative estimates.
- Real reels differ due to flange clearances, crossover near the ends, allowable fill height, tubing flattening/ovalization, cable inside the tubing, and operating practices.
- The **total windings** shown from the layer model are usually the most intuitive number for reel wraps.
- The **average-diameter turns** is a quick cross-check based on total length divided by circumference at average diameter.
        """
    )
