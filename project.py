import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np

class FluorescenceAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Fluorescence Analyzer")
        self.time_points = []
        self.selected_distance = tk.DoubleVar(value=0.0)
        self.min_distance = tk.DoubleVar(value=0.0)
        self.max_distance = tk.DoubleVar(value=2000.0)
        self.use_max_distance = tk.BooleanVar(value=True)
        self.min_time = tk.DoubleVar(value=0.0)
        self.max_time = tk.DoubleVar(value=30.0)
        self.use_max_time = tk.BooleanVar(value=True)
        self.time_interval = tk.DoubleVar(value=0.25)
        self.selected_interval = tk.StringVar(value="All")
        self.interval_map = {
            "All": None,
            "Every 15 min": 0.25,
            "Every 30 min": 0.5,
            "Hourly": 1.0,
            "Every 2 hours": 2.0
        }

        # --- TIME CONTROLS (at the top) ---
        time_frame = tk.LabelFrame(root, text="Time Controls")
        time_frame.pack(padx=20, pady=5, fill=tk.X)
        interval_frame = tk.Frame(time_frame)
        interval_frame.pack(pady=5, fill=tk.X)
        tk.Label(interval_frame, text="Time interval (hours):").pack(side=tk.LEFT)
        self.interval_entry = tk.Entry(interval_frame, textvariable=self.time_interval, width=8)
        self.interval_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(interval_frame, text="(e.g., 0.25 = 15min, 0.5 = 30min, 1.0 = 1h)").pack(side=tk.LEFT, padx=5)
        time_range_frame = tk.Frame(time_frame)
        time_range_frame.pack(pady=5, fill=tk.X)
        tk.Label(time_range_frame, text="Min time (h):").pack(side=tk.LEFT)
        self.min_time_entry = tk.Entry(time_range_frame, textvariable=self.min_time, width=8)
        self.min_time_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(time_range_frame, text="Max time (h):").pack(side=tk.LEFT)
        self.max_time_entry = tk.Entry(time_range_frame, textvariable=self.max_time, width=8, state="disabled")
        self.max_time_entry.pack(side=tk.LEFT, padx=5)
        self.max_time_check = tk.Checkbutton(time_range_frame, text="Use max in data", variable=self.use_max_time,
                                             command=self.toggle_max_time)
        self.max_time_check.pack(side=tk.LEFT, padx=5)

        # --- RADIO BUTTONS FOR TIME POINT SELECTION ---
        radio_frame = tk.Frame(time_frame)
        radio_frame.pack(pady=5, fill=tk.X)
        tk.Label(radio_frame, text="Show time points:").pack(side=tk.LEFT)
        for label in self.interval_map:
            tk.Radiobutton(
                radio_frame, text=label, variable=self.selected_interval, value=label,
                command=self.update_plot
            ).pack(side=tk.LEFT, padx=3)

        # --- PLOT CUSTOMIZATION MENU ---
        custom_frame = tk.LabelFrame(root, text="Plot Customization")
        custom_frame.pack(padx=20, pady=5, fill=tk.X)
        tk.Label(custom_frame, text="Line style:").pack(side=tk.LEFT)
        self.line_style = tk.StringVar(value='-')
        tk.OptionMenu(custom_frame, self.line_style, '-', '--', '-.', ':').pack(side=tk.LEFT)
        tk.Label(custom_frame, text="Marker:").pack(side=tk.LEFT)
        self.marker_style = tk.StringVar(value='None')
        tk.OptionMenu(custom_frame, self.marker_style, 'None', 'o', 's', '^', 'd').pack(side=tk.LEFT)
        tk.Label(custom_frame, text="Colormap:").pack(side=tk.LEFT)
        self.data_cmap = tk.StringVar(value='viridis')
        tk.OptionMenu(custom_frame, self.data_cmap, 'viridis', 'plasma', 'inferno', 'cividis', 'tab10').pack(side=tk.LEFT)
        self.show_grid = tk.BooleanVar(value=True)
        tk.Checkbutton(custom_frame, text="Show grid", variable=self.show_grid).pack(side=tk.LEFT)
        tk.Label(custom_frame, text="Font size:").pack(side=tk.LEFT)
        self.font_size = tk.IntVar(value=12)
        tk.Entry(custom_frame, textvariable=self.font_size, width=4).pack(side=tk.LEFT)

        # --- LEGEND COLOR STYLE MENU ---
        legend_menu_frame = tk.Frame(root)
        legend_menu_frame.pack(padx=20, pady=5, fill=tk.X)
        self.legend_cmap = tk.StringVar(value="Same as data")
        legend_cmap_options = ["Same as data", "plasma", "inferno", "cividis", "tab10"]
        tk.Label(legend_menu_frame, text="Legend color style:").pack(side=tk.LEFT)
        tk.OptionMenu(legend_menu_frame, self.legend_cmap, *legend_cmap_options).pack(side=tk.LEFT)

        # --- LOAD BUTTON (middle) ---
        file_frame = tk.Frame(root)
        file_frame.pack(padx=20, pady=10, fill=tk.X)
        tk.Button(file_frame, text="Load Experiment Replicates", command=self.load_files).pack(pady=5)

        # --- DISTANCE CONTROLS (below load button) ---
        distance_frame = tk.LabelFrame(root, text="Distance Controls")
        distance_frame.pack(padx=20, pady=5, fill=tk.X)
        dist_select_frame = tk.Frame(distance_frame)
        dist_select_frame.pack(pady=5, fill=tk.X)
        tk.Label(dist_select_frame, text="Distance to check (µm):").pack(side=tk.LEFT)
        self.distance_entry = tk.Entry(dist_select_frame, textvariable=self.selected_distance, width=10)
        self.distance_entry.pack(side=tk.LEFT, padx=5)
        dist_range_frame = tk.Frame(distance_frame)
        dist_range_frame.pack(pady=5, fill=tk.X)
        tk.Label(dist_range_frame, text="Min distance (µm):").pack(side=tk.LEFT)
        self.min_distance_entry = tk.Entry(dist_range_frame, textvariable=self.min_distance, width=8)
        self.min_distance_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(dist_range_frame, text="Max distance (µm):").pack(side=tk.LEFT)
        self.max_distance_entry = tk.Entry(dist_range_frame, textvariable=self.max_distance, width=8, state="disabled")
        self.max_distance_entry.pack(side=tk.LEFT, padx=5)
        self.max_distance_check = tk.Checkbutton(dist_range_frame, text="Use max in data", variable=self.use_max_distance,
                                                 command=self.toggle_max_distance)
        self.max_distance_check.pack(side=tk.LEFT, padx=5)

        # --- CONTROL BUTTONS ---
        button_frame = tk.Frame(root)
        button_frame.pack(padx=20, pady=10, fill=tk.X)
        tk.Button(button_frame, text="Update Plot", command=self.update_plot).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Plot Time Series", command=self.plot_time_series_button).pack(side=tk.LEFT, padx=5)

    def toggle_max_distance(self):
        if self.use_max_distance.get():
            self.max_distance_entry.config(state="disabled")
        else:
            self.max_distance_entry.config(state="normal")

    def toggle_max_time(self):
        if self.use_max_time.get():
            self.max_time_entry.config(state="disabled")
        else:
            self.max_time_entry.config(state="normal")

    def load_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Text files", "*.txt")])
        if file_paths:
            self.process_files(file_paths)
            self.update_plot()

    def process_files(self, file_paths):
        self.time_points = []
        all_blocks = []
        try:
            time_interval = float(self.time_interval.get())
        except ValueError:
            time_interval = 0.25
            self.time_interval.set(time_interval)
        for file_path in file_paths:
            with open(file_path, 'r') as file:
                content = file.read().strip()
                file_blocks = [b.strip() for b in content.split('\n') if b.strip()]
                all_blocks.extend(file_blocks)
        for idx, block in enumerate(all_blocks):
            values = list(map(float, block.split(',')))
            source = np.mean(values[:5])
            sink = np.mean(values[-5:])
            normalized = [(x - sink)/(source - sink)*100 for x in values]
            hours = idx * time_interval
            self.time_points.append({
                'raw': values,
                'normalized': normalized,
                'distance': [i*10 for i in range(len(values))],
                'time': hours
            })

    def get_max_distance_from_data(self):
        if not self.time_points:
            return 2000.0
        return max([max(tp['distance']) for tp in self.time_points])

    def get_max_time_from_data(self):
        if not self.time_points:
            return 30.0
        return max([tp['time'] for tp in self.time_points])

    def update_plot(self):
        if not self.time_points:
            return
        try:
            distance = float(self.distance_entry.get())
            min_dist = float(self.min_distance_entry.get())
            if self.use_max_distance.get():
                max_dist = self.get_max_distance_from_data()
            else:
                max_dist = float(self.max_distance_entry.get())
            min_time = float(self.min_time_entry.get())
            if self.use_max_time.get():
                max_time = self.get_max_time_from_data()
            else:
                max_time = float(self.max_time_entry.get())
            if min_dist >= max_dist:
                min_dist = 0.0
                max_dist = self.get_max_distance_from_data()
                self.min_distance.set(min_dist)
                self.max_distance.set(max_dist)
            if min_time >= max_time:
                min_time = 0.0
                max_time = self.get_max_time_from_data()
                self.min_time.set(min_time)
                self.max_time.set(max_time)
        except ValueError:
            distance = 0.0
            min_dist = 0.0
            max_dist = self.get_max_distance_from_data()
            min_time = 0.0
            max_time = self.get_max_time_from_data()

        # --- Filter time points based on radio selection ---
        interval_label = self.selected_interval.get()
        interval = self.interval_map[interval_label]
        filtered_time_points = []
        if interval is None:
            # All time points
            filtered_time_points = [
                tp for tp in self.time_points if min_time <= tp['time'] <= max_time
            ]
        else:
            filtered_time_points = [
                tp for tp in self.time_points
                if min_time <= tp['time'] <= max_time and abs((tp['time'] / interval) - round(tp['time'] / interval)) < 1e-6
            ]

        if not filtered_time_points:
            print("No data points match the selected criteria.")
            return

        # --- Customization ---
        style = self.line_style.get()
        marker = None if self.marker_style.get() == 'None' else self.marker_style.get()
        cmap = plt.colormaps.get_cmap(self.data_cmap.get())
        fontsize = self.font_size.get()
        show_grid = self.show_grid.get()

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 15))
        lines = []
        for idx, tp in enumerate(filtered_time_points):
            hours = tp['time']
            color = cmap(idx / max(1, len(filtered_time_points)-1))
            label = f'Time {hours:.2f}h'
            x_data = np.array(tp['distance'])
            y_raw = np.array(tp['raw'])
            y_norm = np.array(tp['normalized'])
            mask = (x_data >= min_dist) & (x_data <= max_dist)
            l1, = ax1.plot(x_data[mask], y_raw[mask], color=color, label=label, linestyle=style, marker=marker)
            l2, = ax2.plot(x_data[mask], y_norm[mask], color=color, label=label, linestyle=style, marker=marker)
            lines.append(l2)
            if min_dist <= distance <= max_dist and distance in tp['distance']:
                idx_dist = tp['distance'].index(distance)
                ax1.plot(distance, tp['raw'][idx_dist], 'o', color=color, markersize=10, markeredgecolor='k')
                ax2.plot(distance, tp['normalized'][idx_dist], 'o', color=color, markersize=10, markeredgecolor='k')
        ax1.set_xlim(min_dist, max_dist)
        ax2.set_xlim(min_dist, max_dist)
        ax1.set_title('Raw Fluorescence Data', fontsize=fontsize)
        ax1.set_ylabel('Fluorescence (a.u.)', fontsize=fontsize)
        ax1.grid(show_grid)
        ax2.set_title('Normalized Fluorescence Data', fontsize=fontsize)
        ax2.set_xlabel('Distance (µm)', fontsize=fontsize)
        ax2.set_ylabel('Normalized Intensity (%)', fontsize=fontsize)
        ax2.set_ylim(-10, 110)
        ax2.grid(show_grid)
        ax1.tick_params(labelsize=fontsize)
        ax2.tick_params(labelsize=fontsize)
        handles, labels = ax1.get_legend_handles_labels()
        legend = fig.legend(handles, labels, title='Time Points',
                            loc='upper right', bbox_to_anchor=(0.9, 0.8),
                            fontsize=fontsize, title_fontsize=fontsize)

        # --- Apply legend color style ---
        legend_cmap_name = self.legend_cmap.get()
        if legend_cmap_name != "Same as data":
            legend_cmap = plt.colormaps.get_cmap(legend_cmap_name)
            for i, text in enumerate(legend.get_texts()):
                text.set_color(legend_cmap(i / (len(handles)-1 if len(handles) > 1 else 1)))
        else:
            for i, text in enumerate(legend.get_texts()):
                if i < len(handles):
                    text.set_color(handles[i].get_color())

        plt.tight_layout()
        plt.subplots_adjust(right=0.85)
        plt.show()

    def plot_time_series_button(self):
        try:
            distance = float(self.distance_entry.get())
        except ValueError:
            distance = 0.0
        self.plot_time_series_at_distance(distance)

    def plot_time_series_at_distance(self, distance):
        times = []
        normalized_values = []
        interval_label = self.selected_interval.get()
        interval = self.interval_map[interval_label]
        # --- Customization ---
        style = self.line_style.get()
        marker = None if self.marker_style.get() == 'None' else self.marker_style.get()
        cmap = plt.colormaps.get_cmap(self.data_cmap.get())
        fontsize = self.font_size.get()
        show_grid = self.show_grid.get()
        # For legend, only show every Nth (e.g., per hour)
        legend_interval = 1.0  # hours, can be made user-configurable

        for tp in self.time_points:
            t = tp['time']
            if interval is not None and abs((t / interval) - round(t / interval)) >= 1e-6:
                continue
            distances = tp['distance']
            closest_index = min(range(len(distances)), key=lambda i: abs(distances[i] - distance))
            closest_distance = distances[closest_index]
            if abs(closest_distance - distance) <= 5:
                times.append(t)
                normalized_values.append(tp['normalized'][closest_index])
        if not times:
            print(f"No data found at or near distance {distance}µm")
            return
        time_norm_pairs = sorted(zip(times, normalized_values))
        times, normalized_values = zip(*time_norm_pairs)
        fig, ax = plt.subplots(figsize=(10, 8))
        # Plot all points
        colors = [cmap(i / max(1, len(times)-1)) for i in range(len(times))]
        ax.plot(times, normalized_values, linestyle=style, marker=marker, color='blue', label=None)
        # For legend: only show per legend_interval (e.g., per hour)
        handles = []
        labels = []
        for i, (t, val) in enumerate(zip(times, normalized_values)):
            if abs(t % legend_interval) < 1e-6:
                h, = ax.plot(t, val, marker=marker, linestyle='None', color=colors[i], label=f"{t:.2f}h")
                handles.append(h)
                labels.append(f"{t:.2f}h")
        ax.set_xlabel('Time (hours)', fontsize=fontsize)
        ax.set_ylabel('Normalized Fluorescence (%)', fontsize=fontsize)
        ax.set_title(f'Normalized Fluorescence Over Time at {distance}µm', fontsize=fontsize)
        ax.grid(show_grid)
        ax.tick_params(labelsize=fontsize)
        # Legend coloring
        legend_cmap_name = self.legend_cmap.get()
        legend = ax.legend(handles, labels, title="Legend (per hour)", fontsize=fontsize)
        if legend_cmap_name != "Same as data":
            legend_cmap = plt.colormaps.get_cmap(legend_cmap_name)
            for i, text in enumerate(legend.get_texts()):
                text.set_color(legend_cmap(i / (len(handles)-1 if len(handles) > 1 else 1)))
        else:
            for i, text in enumerate(legend.get_texts()):
                if i < len(handles):
                    text.set_color(handles[i].get_color())
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = FluorescenceAnalyzer(root)
    root.mainloop()
