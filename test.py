import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Create figure and axis
fig, ax = plt.subplots(figsize=(7, 5))  # Optional: scale to match shape

# Draw rectangle: (x, y), width, height
rect = patches.Rectangle((0, 0), 500, 700, linewidth=2, edgecolor='black', facecolor='lightgrey')

# Add to plot
ax.add_patch(rect)

# Set limits and labels
ax.set_xlim(-50, 550)
ax.set_ylim(-50, 750)
ax.set_aspect('equal')
ax.set_title('Grid Cell (500 x 700)')
ax.set_xlabel('Width (units)')
ax.set_ylabel('Height (units)')

# Show gridlines
ax.grid(True, linestyle='--', alpha=0.5)

plt.show()
