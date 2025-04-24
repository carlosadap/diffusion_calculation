import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import numpy as np
import os

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class FluorescenceAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Fluorescence Analyzer")
        self.file_paths = []
        self.time_groups = {}
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
        self.line_style = tk.StringVar(value='-')
        self.marker_style = tk.StringVar(value='None')
        self.data_cmap = tk.StringVar(value='viridis')
        self.show_grid = tk.BooleanVar(value=True)
        self.font_size = tk.IntVar(value=12)
        self.main_legend_interval = tk.DoubleVar(value=1.0)
        self.legend_interval = tk.DoubleVar(value=1.0)
        self.ss_legend_interval = tk.DoubleVar(value=1.0)
        self.omit_intervals = tk.StringVar(value="")
        self.ts_line_style = tk.StringVar(value='-')
        self.ts_marker_style = tk.StringVar(value='o')
        self.ts_data_cmap = tk.StringVar(value='viridis')
        self.ts_show_grid = tk.BooleanVar(value=True)
        self.ts_font_size = tk.IntVar(value=12)
        self.ss_line_style = tk.StringVar(value='-')
        self.ss_marker_style = tk.StringVar(value='None')
        self.ss_show_grid = tk.BooleanVar(value=True)
        self.ss_font_size = tk.IntVar(value=12)
        self.show_std = tk.BooleanVar(value=True)
        self._setup_gui()

    def _setup_gui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        controls_frame = tk.Frame(main_frame)
        controls_frame.grid(row=0, column=0, sticky="nsew")
        img_frame = tk.Frame(main_frame, width=340)
        img_frame.grid(row=0, column=1, sticky="ns", padx=10, pady=10)
        if PIL_AVAILABLE and os.path.exists("pictures/virtual_analyzer.jpg"):
            image = Image.open("pictures/virtual_analyzer.jpg").resize((320, 240))
            self.tk_img = ImageTk.PhotoImage(image)
            tk.Label(img_frame, image=self.tk_img).pack(pady=10)
        else:
            tk.Label(img_frame, text="Fluorescence Analyzer", font=('Arial', 16)).pack(pady=20)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)
        self._create_controls(controls_frame)

    def _create_controls(self, parent):
        # Time Controls
        time_frame = tk.LabelFrame(parent, text="Time Controls")
        time_frame.pack(padx=10, pady=5, fill=tk.X)
        interval_frame = tk.Frame(time_frame)
        interval_frame.pack(pady=2, fill=tk.X)
        tk.Label(interval_frame, text="Time interval (hours):").pack(side=tk.LEFT)
        tk.Entry(interval_frame, textvariable=self.time_interval, width=8).pack(side=tk.LEFT, padx=5)
        tk.Label(interval_frame, text="(e.g., 0.25 = 15min, 0.5 = 30min, 1.0 = 1h)").pack(side=tk.LEFT, padx=5)
        time_range_frame = tk.Frame(time_frame)
        time_range_frame.pack(pady=2, fill=tk.X)
        tk.Label(time_range_frame, text="Min time (h):").pack(side=tk.LEFT)
        tk.Entry(time_range_frame, textvariable=self.min_time, width=8).pack(side=tk.LEFT, padx=5)
        tk.Label(time_range_frame, text="Max time (h):").pack(side=tk.LEFT)
        self.max_time_entry = tk.Entry(time_range_frame, textvariable=self.max_time, width=8, state="disabled")
        self.max_time_entry.pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(time_range_frame, text="Use max in data", variable=self.use_max_time,
                       command=self.toggle_max_time).pack(side=tk.LEFT, padx=5)
        radio_frame = tk.Frame(time_frame)
        radio_frame.pack(pady=2, fill=tk.X)
        tk.Label(radio_frame, text="Show time points:").pack(side=tk.LEFT)
        for label in self.interval_map:
            tk.Radiobutton(radio_frame, text=label, variable=self.selected_interval, value=label
            ).pack(side=tk.LEFT, padx=3)

        # Legend Interval Controls
        legend_frame = tk.LabelFrame(parent, text="Legend Options")
        legend_frame.pack(padx=10, pady=5, fill=tk.X)
        tk.Label(legend_frame, text="Main Plot Interval (h):").pack(side=tk.LEFT)
        tk.Entry(legend_frame, textvariable=self.main_legend_interval, width=5).pack(side=tk.LEFT)
        tk.Label(legend_frame, text="Time Series Interval (h):").pack(side=tk.LEFT)
        tk.Entry(legend_frame, textvariable=self.legend_interval, width=5).pack(side=tk.LEFT)
        tk.Label(legend_frame, text="Omit intervals (e.g. 2,4,6):").pack(side=tk.LEFT)
        tk.Entry(legend_frame, textvariable=self.omit_intervals, width=10).pack(side=tk.LEFT)

        # STD Display
        std_frame = tk.Frame(parent)
        std_frame.pack(padx=10, pady=5, fill=tk.X)
        tk.Label(std_frame, text="Standard Deviation Display:").pack(side=tk.LEFT)
        tk.Checkbutton(std_frame, text="Show STD", variable=self.show_std).pack(side=tk.LEFT)

        # Load Button
        file_frame = tk.Frame(parent)
        file_frame.pack(padx=10, pady=10, fill=tk.X)
        tk.Button(file_frame, text="Load Experiment Replicates", command=self.load_files).pack(pady=5)

        # Distance Controls
        distance_frame = tk.LabelFrame(parent, text="Distance Controls")
        distance_frame.pack(padx=10, pady=5, fill=tk.X)
        dist_select_frame = tk.Frame(distance_frame)
        dist_select_frame.pack(pady=2, fill=tk.X)
        tk.Label(dist_select_frame, text="Distance to check (µm):").pack(side=tk.LEFT)
        tk.Entry(dist_select_frame, textvariable=self.selected_distance, width=10).pack(side=tk.LEFT, padx=5)
        dist_range_frame = tk.Frame(distance_frame)
        dist_range_frame.pack(pady=2, fill=tk.X)
        tk.Label(dist_range_frame, text="Min distance (µm):").pack(side=tk.LEFT)
        tk.Entry(dist_range_frame, textvariable=self.min_distance, width=8).pack(side=tk.LEFT, padx=5)
        tk.Label(dist_range_frame, text="Max distance (µm):").pack(side=tk.LEFT)
        self.max_distance_entry = tk.Entry(dist_range_frame, textvariable=self.max_distance, width=8, state="disabled")
        self.max_distance_entry.pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(dist_range_frame, text="Use max in data", variable=self.use_max_distance,
                       command=self.toggle_max_distance).pack(side=tk.LEFT, padx=5)

        # Plot Customization
        custom_frame = tk.LabelFrame(parent, text="Main Plot Customization")
        custom_frame.pack(padx=10, pady=2, fill=tk.X)
        tk.Label(custom_frame, text="Line style:").pack(side=tk.LEFT)
        tk.OptionMenu(custom_frame, self.line_style, '-', '--', '-.', ':').pack(side=tk.LEFT)
        tk.Label(custom_frame, text="Marker:").pack(side=tk.LEFT)
        tk.OptionMenu(custom_frame, self.marker_style, 'None', 'o', 's', '^', 'd').pack(side=tk.LEFT)
        tk.Label(custom_frame, text="Colormap:").pack(side=tk.LEFT)
        tk.OptionMenu(custom_frame, self.data_cmap, 'viridis', 'plasma', 'inferno', 'cividis', 'tab10').pack(side=tk.LEFT)
        tk.Checkbutton(custom_frame, text="Show grid", variable=self.show_grid).pack(side=tk.LEFT)
        tk.Label(custom_frame, text="Font size:").pack(side=tk.LEFT)
        tk.Entry(custom_frame, textvariable=self.font_size, width=4).pack(side=tk.LEFT)

        # Control Buttons
        button_frame = tk.Frame(parent)
        button_frame.pack(padx=10, pady=10, fill=tk.X)
        tk.Button(button_frame, text="Update Plot", command=self.plot_data).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Plot Time Series", command=self.plot_time_series_button).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Plot Source/Sink", command=self.plot_source_sink).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Export", command=self.export_plot_dialog).pack(side=tk.LEFT, padx=5)

    def toggle_max_distance(self):
        self.max_distance_entry.config(state="disabled" if self.use_max_distance.get() else "normal")

    def toggle_max_time(self):
        self.max_time_entry.config(state="disabled" if self.use_max_time.get() else "normal")

    def load_files(self):
        self.file_paths = filedialog.askopenfilenames(filetypes=[("Text files", "*.txt")])
        if self.file_paths:
            self.process_files(self.file_paths)
            self.plot_data()

    def process_files(self, file_paths):
        self.time_groups = {}
        try:
            time_interval = float(self.time_interval.get())
        except ValueError:
            time_interval = 0.25
            self.time_interval.set(time_interval)

        for file_path in file_paths:
            with open(file_path, 'r') as file:
                content = file.read().strip()
                blocks = [b.strip() for b in content.split('\n') if b.strip()]
                for idx, block in enumerate(blocks):  # Use per-file index
                    values = list(map(float, block.split(',')))
                    source = np.mean(values[:5])
                    sink = np.mean(values[-5:])
                    normalized = [(x - sink)/(source - sink)*100 for x in values]
                    hours = idx * time_interval  # Time based on block position in file
                    if hours not in self.time_groups:
                        self.time_groups[hours] = []
                    self.time_groups[hours].append({
                        'distance': [i*10 for i in range(len(values))],
                        'raw': values,
                        'normalized': normalized,
                        'source': source,
                        'sink': sink
                    })

    def get_max_distance_from_data(self):
        if not self.time_groups:
            return 2000.0
        return max(max(rep['distance']) for group in self.time_groups.values() for rep in group)

    def get_max_time_from_data(self):
        if not self.time_groups:
            return 30.0
        return max(self.time_groups.keys())

    def plot_data(self):
        if not self.time_groups:
            return

        try:
            min_dist = float(self.min_distance.get())
            max_dist = (self.get_max_distance_from_data() if self.use_max_distance.get()
                        else float(self.max_distance.get()))
            min_time = float(self.min_time.get())
            max_time = (self.get_max_time_from_data() if self.use_max_time.get()
                       else float(self.max_time.get()))
        except ValueError:
            min_dist = 0.0
            max_dist = self.get_max_distance_from_data()
            min_time = 0.0
            max_time = self.get_max_time_from_data()

        interval = self.interval_map[self.selected_interval.get()]
        filtered_times = [t for t in self.time_groups if min_time <= t <= max_time and
                         (interval is None or abs((t / interval) - round(t / interval)) < 1e-6)]
        filtered_times.sort()

        if not filtered_times:
            messagebox.showinfo("No Data", "No data points match the selected criteria.")
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 15))
        cmap = plt.colormaps.get_cmap(self.data_cmap.get())
        legend_handles = []
        legend_labels = []

        for idx, t in enumerate(filtered_times):
            color = cmap(idx / max(1, len(filtered_times)-1))
            group = self.time_groups[t]
            distances = group[0]['distance']

            # Plot raw data
            if len(group) > 1 and self.show_std.get():
                raw_mean = np.mean([rep['raw'] for rep in group], axis=0)
                raw_std = np.std([rep['raw'] for rep in group], axis=0)
                line, = ax1.plot(distances, raw_mean, color=color, linestyle=self.line_style.get())
                ax1.fill_between(distances, raw_mean-raw_std, raw_mean+raw_std, color=color, alpha=0.2)
            else:
                for rep in group:
                    line, = ax1.plot(rep['distance'], rep['raw'], color=color, linestyle=self.line_style.get())

            # Plot normalized data
            if len(group) > 1 and self.show_std.get():
                norm_mean = np.mean([rep['normalized'] for rep in group], axis=0)
                norm_std = np.std([rep['normalized'] for rep in group], axis=0)
                line, = ax2.plot(distances, norm_mean, color=color, linestyle=self.line_style.get())
                ax2.fill_between(distances, norm_mean-norm_std, norm_mean+norm_std, color=color, alpha=0.2)
            else:
                for rep in group:
                    line, = ax2.plot(rep['distance'], rep['normalized'], color=color, linestyle=self.line_style.get())

            # Add to legend
            if abs(t % self.main_legend_interval.get()) < 1e-6:
                legend_handles.append(line)
                legend_labels.append(f'Time {t:.2f}h')

        # Configure axes
        ax1.set_xlim(min_dist, max_dist)
        ax2.set_xlim(min_dist, max_dist)
        ax1.set_title('Raw Fluorescence Data', fontsize=self.font_size.get())
        ax1.set_ylabel('Fluorescence (a.u.)', fontsize=self.font_size.get())
        ax1.grid(self.show_grid.get())
        ax2.set_title('Normalized Fluorescence Data', fontsize=self.font_size.get())
        ax2.set_xlabel('Distance (µm)', fontsize=self.font_size.get())
        ax2.set_ylabel('Normalized Intensity (%)', fontsize=self.font_size.get())
        ax2.set_ylim(-10, 110)
        ax2.grid(self.show_grid.get())

        # Add legend
        if legend_handles:
            legend = fig.legend(legend_handles, legend_labels, title='Time Points',
                              loc='upper right', bbox_to_anchor=(0.95, 0.8),
                              fontsize=self.font_size.get(), ncol=3)
            for i, text in enumerate(legend.get_texts()):
                text.set_color(legend_handles[i].get_color())

        self.last_fig = fig
        plt.tight_layout()
        plt.subplots_adjust(right=0.85)
        plt.show()

    def plot_time_series_button(self):
        try:
            distance = float(self.selected_distance.get())
        except ValueError:
            distance = 0.0
        self.plot_time_series_at_distance(distance)

    def plot_time_series_at_distance(self, distance):
        interval = self.interval_map[self.selected_interval.get()]
        times = []
        raw_values = []
        norm_values = []
        raw_stds = []
        norm_stds = []

        for t in sorted(self.time_groups.keys()):
            if interval and abs((t / interval) - round(t / interval)) >= 1e-6:
                continue

            raw_group = []
            norm_group = []
            for rep in self.time_groups[t]:
                distances = rep['distance']
                idx = min(range(len(distances)), key=lambda i: abs(distances[i] - distance))
                if abs(distances[idx] - distance) <= 5:
                    raw_group.append(rep['raw'][idx])
                    norm_group.append(rep['normalized'][idx])

            if raw_group and norm_group:
                times.append(t)
                raw_values.append(np.mean(raw_group))
                norm_values.append(np.mean(norm_group))
                raw_stds.append(np.std(raw_group) if len(raw_group) > 1 else 0)
                norm_stds.append(np.std(norm_group) if len(norm_group) > 1 else 0)

        if not times:
            messagebox.showinfo("No Data", f"No data found at or near distance {distance}µm")
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

        # Raw values plot with std
        ax1.errorbar(times, raw_values, yerr=raw_stds if self.show_std.get() else None,
                    linestyle=self.ts_line_style.get(), color='blue', label='Raw Fluorescence',
                    marker=self.ts_marker_style.get() if self.ts_marker_style.get() != 'None' else None)
        ax1.set_ylabel('Fluorescence (a.u.)', fontsize=self.ts_font_size.get())
        ax1.grid(self.ts_show_grid.get())
        ax1.tick_params(labelsize=self.ts_font_size.get())

        # Normalized values plot with std
        ax2.errorbar(times, norm_values, yerr=norm_stds if self.show_std.get() else None,
                    linestyle=self.ts_line_style.get(), color='green', label='Normalized Fluorescence',
                    marker=self.ts_marker_style.get() if self.ts_marker_style.get() != 'None' else None)
        ax2.set_xlabel('Time (hours)', fontsize=self.ts_font_size.get())
        ax2.set_ylabel('Normalized (%)', fontsize=self.ts_font_size.get())
        ax2.grid(self.ts_show_grid.get())
        ax2.tick_params(labelsize=self.ts_font_size.get())

        plt.suptitle(f'Fluorescence at {distance}µm', fontsize=self.ts_font_size.get())
        plt.tight_layout()
        self.last_fig = fig
        plt.show()


    def plot_source_sink(self):
        if not self.time_groups:
            messagebox.showinfo("No Data", "No data loaded to plot")
            return

        times = sorted(self.time_groups.keys())
        sources = [np.mean([rep['source'] for rep in self.time_groups[t]]) for t in times]
        sinks = [np.mean([rep['sink'] for rep in self.time_groups[t]]) for t in times]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(times, sources, linestyle=self.ss_line_style.get(), color='blue', label='Source')
        ax.plot(times, sinks, linestyle=self.ss_line_style.get(), color='red', label='Sink')
        ax.set_xlabel('Time (hours)', fontsize=self.ss_font_size.get())
        ax.set_ylabel('Fluorescence (a.u.)', fontsize=self.ss_font_size.get())
        ax.set_title('Source and Sink Values Over Time', fontsize=self.ss_font_size.get())
        ax.grid(self.ss_show_grid.get())
        ax.legend(fontsize=self.ss_font_size.get())
        self.last_fig = fig
        plt.show()

    def export_plot_dialog(self):
        filetypes = [("SVG file", "*.svg"), ("Text file", "*.txt")]
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=filetypes)
        if not file_path:
            return

        if file_path.endswith('.svg'):
            if hasattr(self, 'last_fig') and self.last_fig:
                self.last_fig.savefig(file_path, format='svg', bbox_inches='tight')
                messagebox.showinfo("Export", f"Figure exported as SVG:\n{file_path}")
            else:
                messagebox.showwarning("Export", "No plot to export.")
        elif file_path.endswith('.txt'):
            self.export_last_data_as_txt(file_path)
        else:
            messagebox.showwarning("Export", "Unsupported file extension.")

    def export_last_data_as_txt(self, file_path):
        try:
            with open(file_path, 'w') as f:
                f.write("# Exported Fluorescence Data (Mean ± Std)\n")
                f.write("# Time(h)\tDistance(um)\tRawMean\tRawStd\tNormMean\tNormStd\n")
                for t in sorted(self.time_groups.keys()):
                    group = self.time_groups[t]
                    # Find all unique distances for this time point across all replicates
                    all_distances = sorted(set(d for rep in group for d in rep['distance']))
                    for d in all_distances:
                        raw_vals = []
                        norm_vals = []
                        for rep in group:
                            if d in rep['distance']:
                                idx = rep['distance'].index(d)
                                raw_vals.append(rep['raw'][idx])
                                norm_vals.append(rep['normalized'][idx])
                        if raw_vals and norm_vals:
                            m_r = np.mean(raw_vals)
                            s_r = np.std(raw_vals, ddof=1) if len(raw_vals) > 1 else 0
                            m_n = np.mean(norm_vals)
                            s_n = np.std(norm_vals, ddof=1) if len(norm_vals) > 1 else 0
                            f.write(f"{t:.2f}\t{d:.1f}\t{m_r:.6f}\t{s_r:.6f}\t{m_n:.6f}\t{s_n:.6f}\n")
            messagebox.showinfo("Export", f"Data exported as TXT:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))



if __name__ == "__main__":
    root = tk.Tk()
    app = FluorescenceAnalyzer(root)
    root.mainloop()
