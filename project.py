import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np

def load_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("Text files", "*.txt")])
    if file_paths:
        process_files(file_paths)

def process_files(file_paths):
    all_time_points = []

    for file_path in file_paths:
        with open(file_path, 'r') as file:
            content = file.read().strip()
            # Modified block splitting with empty line check
            blocks = [b.strip() for b in content.split('\n') if b.strip()]
            time_points = []

            for block in blocks:
                values = list(map(float, block.split(',')))
                source = np.mean(values[:5])
                sink = np.mean(values[-5:])
                normalized = [(x - sink)/(source - sink)*100 for x in values]

                time_points.append({
                    'raw': values,
                    'normalized': normalized,
                    'distance': [i*10 for i in range(len(values))]
                })

            all_time_points.extend(time_points)

    plot_data(all_time_points)

def plot_data(time_points):
    if not time_points:
        print("No valid data to plot")
        return

    cmap = plt.colormaps.get_cmap('viridis')
    time_colors = cmap(np.linspace(0, 1, len(time_points)))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 15))

    for idx, tp in enumerate(time_points):
        # Show label each 15 min
        # hours = (idx * 0.25) % 24
        # color = time_colors[idx]
        # ax1.plot(tp['distance'], tp['raw'], color=color, label=f'{hours:.2f}h')
        # ax2.plot(tp['distance'], tp['normalized'], color=color, label=f'{hours:.2f}h')

        # Show label each hour
        hours = (idx * 0.25) % 24  # 0.25h = 15 min
        color = time_colors[idx]
        # Only label lines at full hours
        if abs(hours - round(hours)) < 1e-6:  # Handles floating point errors
            label = f'Time {int(hours):02d}.00h'
        else:
            label = None
        ax1.plot(tp['distance'], tp['raw'], color=color, label=label)
        ax2.plot(tp['distance'], tp['normalized'], color=color, label=label)


    ax1.set_title('Raw Fluorescence Data')
    ax1.set_ylabel('Fluorescence (a.u.)')
    ax1.grid(True)

    ax2.set_title('Normalized Fluorescence Data')
    ax2.set_xlabel('Distance (µm)')
    ax2.set_ylabel('Normalized Intensity (%)')
    ax2.set_ylim(-10, 110)
    ax2.grid(True)

    # Place the legend outside the plot area, fully visible
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, title='Time Points',
               loc='upper right', bbox_to_anchor=(0.9, 0.8), fontsize='small', title_fontsize='medium')

    plt.tight_layout()
    plt.subplots_adjust(right=0.8)  # Make enough space for the legend
    plt.show()


# GUI setup
root = tk.Tk()
root.title("Fluorescence Analyzer")
tk.Button(root, text="Load Experiment Replicates", command=load_files).pack(padx=20, pady=20)
root.mainloop()
