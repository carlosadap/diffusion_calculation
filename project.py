import tkinter as tk
from tkinter import filedialog, ttk
import matplotlib.pyplot as plt
import numpy as np

class FluorescenceAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Fluorescence Analyzer")
        self.time_points = []
        self.selected_distance = tk.DoubleVar(value=0.0)
        self.min_distance = tk.DoubleVar(value=0.0)
        self.max_distance = tk.DoubleVar(value=40.0)
        self.plot_time_series = tk.BooleanVar(value=False)

        # Time point selection variables
        self.min_time = tk.DoubleVar(value=0.0)
        self.max_time = tk.DoubleVar(value=10.0)
        self.selected_times = []  # Will store checkbutton variables

        # Main container frames
        file_frame = tk.Frame(root)
        file_frame.pack(padx=20, pady=10, fill=tk.X)

        distance_frame = tk.LabelFrame(root, text="Distance Controls")
        distance_frame.pack(padx=20, pady=5, fill=tk.X)

        time_frame = tk.LabelFrame(root, text="Time Controls")
        time_frame.pack(padx=20, pady=5, fill=tk.X)

        button_frame = tk.Frame(root)
        button_frame.pack(padx=20, pady=10, fill=tk.X)

        # File controls
        tk.Button(file_frame, text="Load Experiment Replicates", command=self.load_files).pack(pady=5)

        # Distance controls
        dist_select_frame = tk.Frame(distance_frame)
        dist_select_frame.pack(pady=5, fill=tk.X)

        tk.Label(dist_select_frame, text="Distance to check (µm):").pack(side=tk.LEFT)
        self.distance_entry = tk.Entry(dist_select_frame, textvariable=self.selected_distance, width=10)
        self.distance_entry.pack(side=tk.LEFT, padx=5)

        # Add checkbox for time series plot
        self.time_series_check = tk.Checkbutton(dist_select_frame, text="Plot time series at this distance",
                                             variable=self.plot_time_series)
        self.time_series_check.pack(side=tk.LEFT, padx=5)

        # Distance range controls
        dist_range_frame = tk.Frame(distance_frame)
        dist_range_frame.pack(pady=5, fill=tk.X)

        tk.Label(dist_range_frame, text="Min distance (µm):").pack(side=tk.LEFT)
        self.min_distance_entry = tk.Entry(dist_range_frame, textvariable=self.min_distance, width=8)
        self.min_distance_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(dist_range_frame, text="Max distance (µm):").pack(side=tk.LEFT)
        self.max_distance_entry = tk.Entry(dist_range_frame, textvariable=self.max_distance, width=8)
        self.max_distance_entry.pack(side=tk.LEFT, padx=5)

        # Time range controls
        time_range_frame = tk.Frame(time_frame)
        time_range_frame.pack(pady=5, fill=tk.X)

        tk.Label(time_range_frame, text="Min time (h):").pack(side=tk.LEFT)
        self.min_time_entry = tk.Entry(time_range_frame, textvariable=self.min_time, width=8)
        self.min_time_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(time_range_frame, text="Max time (h):").pack(side=tk.LEFT)
        self.max_time_entry = tk.Entry(time_range_frame, textvariable=self.max_time, width=8)
        self.max_time_entry.pack(side=tk.LEFT, padx=5)

        # Container for time checkboxes (will be populated after loading data)
        self.time_select_frame = tk.Frame(time_frame)
        self.time_select_frame.pack(pady=5, fill=tk.X)
        tk.Label(self.time_select_frame, text="No time points loaded yet. Load data first.").pack()

        # Control buttons
        tk.Button(button_frame, text="Update Plot", command=self.update_plot).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Select All Times", command=self.select_all_times).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Deselect All Times", command=self.deselect_all_times).pack(side=tk.LEFT, padx=5)

    def load_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Text files", "*.txt")])
        if file_paths:
            self.process_files(file_paths)
            self.create_time_checkboxes()
            self.update_plot()

    def process_files(self, file_paths):
        self.time_points = []
        all_blocks = []

        # First, collect all blocks from all files
        for file_path in file_paths:
            with open(file_path, 'r') as file:
                content = file.read().strip()
                file_blocks = [b.strip() for b in content.split('\n') if b.strip()]
                all_blocks.extend(file_blocks)

        # Then process all blocks with correct chronological time
        for idx, block in enumerate(all_blocks):
            values = list(map(float, block.split(',')))
            source = np.mean(values[:5])
            sink = np.mean(values[-5:])
            normalized = [(x - sink)/(source - sink)*100 for x in values]

            # Store time point information (15 min intervals) without modulo
            hours = idx * 0.25  # Cumulative time (fixed)

            self.time_points.append({
                'raw': values,
                'normalized': normalized,
                'distance': [i*10 for i in range(len(values))],
                'time': hours
            })

    def create_time_checkboxes(self):
        # Clear existing checkboxes
        for widget in self.time_select_frame.winfo_children():
            widget.destroy()

        # Reset list of selected time variables
        self.selected_times = []

        # Find unique time points
        unique_times = sorted(list(set([tp['time'] for tp in self.time_points])))

        if not unique_times:
            tk.Label(self.time_select_frame, text="No time points found in data.").pack()
            return

        # Create container for time checkboxes with scrollbar if needed
        tk.Label(self.time_select_frame, text="Select time points to display:").pack(anchor=tk.W)

        if len(unique_times) > 10:
            # Create scrollable frame for many time points
            canvas = tk.Canvas(self.time_select_frame, height=150)
            scrollbar = tk.Scrollbar(self.time_select_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            check_frame = scrollable_frame
        else:
            # Use simple frame for few time points
            check_frame = tk.Frame(self.time_select_frame)
            check_frame.pack(fill=tk.X)

        # Add checkboxes for time points in rows
        row_frame = tk.Frame(check_frame)
        row_frame.pack(anchor=tk.W, fill=tk.X)

        for i, time in enumerate(unique_times):
            if i > 0 and i % 5 == 0:  # New row every 5 checkboxes
                row_frame = tk.Frame(check_frame)
                row_frame.pack(anchor=tk.W, fill=tk.X)

            var = tk.BooleanVar(value=True)  # Default selected
            self.selected_times.append((time, var))

            cb = tk.Checkbutton(row_frame, text=f"{time:.2f}h", variable=var)
            cb.pack(side=tk.LEFT, padx=5)

    def select_all_times(self):
        for _, var in self.selected_times:
            var.set(True)

    def deselect_all_times(self):
        for _, var in self.selected_times:
            var.set(False)

    def update_plot(self):
        if not self.time_points:
            return

        try:
            distance = float(self.distance_entry.get())
            min_dist = float(self.min_distance_entry.get())
            max_dist = float(self.max_distance_entry.get())
            min_time = float(self.min_time_entry.get())
            max_time = float(self.max_time_entry.get())

            if min_dist >= max_dist:
                min_dist = 0.0
                max_dist = 40.0
                self.min_distance.set(min_dist)
                self.max_distance.set(max_dist)

            if min_time >= max_time:
                min_time = 0.0
                max_time = 10.0
                self.min_time.set(min_time)
                self.max_time.set(max_time)
        except ValueError:
            distance = 0.0
            min_dist = 0.0
            max_dist = 40.0
            min_time = 0.0
            max_time = 10.0

        # Check if time series plot is requested
        if self.plot_time_series.get() and distance >= 0:
            self.plot_time_series_at_distance(distance)
        else:
            self.plot_standard_graphs(distance, min_dist, max_dist, min_time, max_time)

    def plot_standard_graphs(self, distance, min_dist, max_dist, min_time, max_time):
        """Plot the standard distance vs fluorescence graphs"""
        # Filter time points by selected times and time range
        selected_time_values = [time for time, var in self.selected_times if var.get()]

        filtered_time_points = [
            tp for tp in self.time_points
            if (tp['time'] in selected_time_values and
                min_time <= tp['time'] <= max_time)
        ]

        if not filtered_time_points:
            print("No data points match the selected criteria.")
            return

        cmap = plt.colormaps.get_cmap('viridis')
        time_colors = cmap(np.linspace(0, 1, len(filtered_time_points)))

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 15))

        for idx, tp in enumerate(filtered_time_points):
            hours = tp['time']
            color = time_colors[idx]

            label = f'Time {hours:.2f}h'

            x_data = np.array(tp['distance'])
            y_raw = np.array(tp['raw'])
            y_norm = np.array(tp['normalized'])

            mask = (x_data >= min_dist) & (x_data <= max_dist)

            ax1.plot(x_data[mask], y_raw[mask], color=color, label=label)
            ax2.plot(x_data[mask], y_norm[mask], color=color, label=label)

            # Highlight the selected distance if it's in range
            if min_dist <= distance <= max_dist and distance in tp['distance']:
                idx_dist = tp['distance'].index(distance)
                ax1.plot(distance, tp['raw'][idx_dist], 'o', color=color, markersize=10, markeredgecolor='k')
                ax2.plot(distance, tp['normalized'][idx_dist], 'o', color=color, markersize=10, markeredgecolor='k')

        # Set axis limits based on user input
        ax1.set_xlim(min_dist, max_dist)
        ax2.set_xlim(min_dist, max_dist)

        ax1.set_title('Raw Fluorescence Data')
        ax1.set_ylabel('Fluorescence (a.u.)')
        ax1.grid(True)

        ax2.set_title('Normalized Fluorescence Data')
        ax2.set_xlabel('Distance (µm)')
        ax2.set_ylabel('Normalized Intensity (%)')
        ax2.set_ylim(-10, 110)
        ax2.grid(True)

        # Updated legend positioning as requested
        handles, labels = ax1.get_legend_handles_labels()
        fig.legend(handles, labels, title='Time Points',
                   loc='upper right', bbox_to_anchor=(0.9, 0.8),
                   fontsize='small', title_fontsize='medium')

        plt.tight_layout()
        plt.subplots_adjust(right=0.85)
        plt.show()

    def plot_time_series_at_distance(self, distance):
        """Plot time on X-axis and normalized fluorescence at selected distance on Y-axis"""
        # Find the closest distance in our data to the user-selected distance
        times = []
        normalized_values = []

        # Get selected time points
        selected_time_values = [time for time, var in self.selected_times if var.get()]

        for tp in self.time_points:
            if tp['time'] not in selected_time_values:
                continue

            distances = tp['distance']
            # Find closest distance to the selected one
            closest_index = min(range(len(distances)), key=lambda i: abs(distances[i] - distance))
            closest_distance = distances[closest_index]

            # Only include if the closest distance is reasonably close
            if abs(closest_distance - distance) <= 5:  # Within 5µm tolerance
                times.append(tp['time'])
                normalized_values.append(tp['normalized'][closest_index])

        if not times:
            print(f"No data found at or near distance {distance}µm")
            return

        # Sort by time to ensure proper chronological order
        time_norm_pairs = sorted(zip(times, normalized_values))
        times, normalized_values = zip(*time_norm_pairs)

        # Create time series plot
        plt.figure(figsize=(10, 8))
        plt.plot(times, normalized_values, 'o-', color='blue', linewidth=2)
        plt.xlabel('Time (hours)')
        plt.ylabel('Normalized Fluorescence (%)')
        plt.title(f'Normalized Fluorescence Over Time at Distance {distance}µm')
        plt.grid(True)
        plt.ylim(-10, 110)
        plt.tight_layout()
        plt.show()

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = FluorescenceAnalyzer(root)
    root.mainloop()
