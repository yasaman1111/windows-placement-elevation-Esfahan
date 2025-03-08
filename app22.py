import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

st.title("Panel with Windows Modulated by Mean Fourier Series")
st.write("This app displays two panel designs: one using the desired number of windows per row, and one using the ideal number based on the mean Fourier series pattern.")

# --------------------------
# 1) Define the Mean Fourier Series Function
# --------------------------
def f(x):
    """
    f(x) = 2.79909091 + 0.07663636*cos(x) - 0.17145455*sin(x) + 1.8216*cos(2*x)
    """
    return 2.79909091 + 0.07663636*np.cos(x) - 0.17145455*np.sin(x) + 1.8216*np.cos(2*x)

def normalized_f(x):
    # Normalize f(x) so that its variation roughly lies in [-1, 1].
    return (f(x) - 2.79909091) / 2.00938

# --------------------------
# 2) Get User Inputs (via Streamlit Sidebar)
# --------------------------
st.sidebar.header("Panel and Windows Settings")
panel_width = st.sidebar.number_input("Panel width (m):", value=50.0, min_value=10.0, step=1.0)
panel_height = st.sidebar.number_input("Panel height for windows region (m):", value=15.0, min_value=3.0, step=1.0)
desired_windows = st.sidebar.number_input("Desired number of windows per row:", value=5, min_value=1, step=1)
# Row settings: every 3.20 m, and the first row’s center is at 2.30 m from the floor.
row_spacing = st.sidebar.number_input("Row spacing (m):", value=3.20, min_value=1.0, step=0.1)
offset = st.sidebar.number_input("Window row offset from floor (m):", value=2.30, min_value=0.0, step=0.1)

# --------------------------
# 3) Compute the Ideal Number of Windows per Row Based on Fourier Series
# --------------------------
# Since the Fourier series function is periodic with period 2π, we approximate the ideal count by:
fourier_period = 2 * np.pi
ideal_windows = round(panel_width / fourier_period)
st.sidebar.write(f"Ideal number of windows per row based on Fourier series: **{ideal_windows}**")

# --------------------------
# 4) Set Window and Row Parameters
# --------------------------
window_width = 2.0    # in meters (width of each window)
window_height = 1.20  # in meters (height of each window)

# Calculate the number of rows based on the available vertical region from offset up to panel_height.
num_rows = int(np.floor((panel_height - offset) / row_spacing)) + 1
if panel_height < offset:
    num_rows = 1
row_y_positions = [offset + i * row_spacing for i in range(num_rows)]
if panel_height < row_spacing:
    row_y_positions = [panel_height / 2.0]

# --------------------------
# 5) Determine Horizontal Window Positions in a Row
# --------------------------
def compute_x_positions(num):
    displacement_factor = 1.0  # horizontal displacement factor (in meters)
    positions = []
    for j in range(num):
        base_x = (j + 0.5) * (panel_width / num)
        # Compute parameter u for modulation (divide the full cycle evenly among windows)
        u = (j + 0.5) * (2 * np.pi / num)
        mod = normalized_f(u)  # roughly in [-1, 1]
        x_modulated = base_x + displacement_factor * mod
        # Clamp the x position so that the window remains within the panel
        half_w = window_width / 2.0
        if x_modulated < half_w:
            x_modulated = half_w
        elif x_modulated > panel_width - half_w:
            x_modulated = panel_width - half_w
        positions.append(x_modulated)
    return positions

desired_x_positions = compute_x_positions(desired_windows)
ideal_x_positions = compute_x_positions(ideal_windows)

# --------------------------
# 6) Draw Two Panels in Two Subplots
# --------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

def draw_panel(ax, x_positions, title_text):
    # Draw the panel outline as a rectangle
    panel_rect = Rectangle((0, 0), panel_width, panel_height,
                           edgecolor='black', facecolor='none', linewidth=2)
    ax.add_patch(panel_rect)
    # Draw windows on each row
    for y_center in row_y_positions:
        for x_center in x_positions:
            lower_left = (x_center - window_width/2, y_center - window_height/2)
            win_rect = Rectangle(lower_left, window_width, window_height,
                                 edgecolor='red', facecolor='none', linewidth=2)
            ax.add_patch(win_rect)
            # Optionally, plot the window center
            ax.plot(x_center, y_center, 'bo')
    ax.set_xlim(-1, panel_width + 1)
    ax.set_ylim(-1, panel_height + 1)
    ax.set_aspect('equal', adjustable='box')
    ax.set_title(title_text)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")

draw_panel(ax1, desired_x_positions, 
           f"Panel with Desired Windows per Row ({desired_windows})\n(Row centers at {offset} m, spaced {row_spacing} m)")
draw_panel(ax2, ideal_x_positions, 
           f"Panel with Ideal Windows per Row ({ideal_windows})\n(Based on Fourier series, row centers at {offset} m, spaced {row_spacing} m)")

st.pyplot(fig)
