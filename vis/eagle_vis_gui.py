#!/usr/bin/env python3
import os
import sys
import threading
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER

# GUI Import modules
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Configuration Import module
try:
    import yaml
except ImportError:
    print("[ERROR] The 'pyyaml' package is required. Please install it using: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# =====================================================================
# 1. CORE VISUALIZER ENGINE
# =====================================================================
class WindFieldVisualizer:
    def __init__(self, nc_t, nc_u, nc_v):
        """Initializes the visualizer and verifies file integrity."""
        self.nc_t_path = nc_t
        self.nc_u_path = nc_u
        self.nc_v_path = nc_v

        self._validate_input_files()

        self.dt = None
        self.du = None
        self.dv = None

        self.longitude = None
        self.latitude = None
        self.x_coords = None
        self.y_coords = None

        self.temp = None
        self.u = None
        self.v = None
        self.wind_speed = None
        self.temp_units = "unknown"
        self.lcc_proj = None

    def _validate_input_files(self):
        """Checks if all required input NetCDF paths exist."""
        missing_files = []
        for file_label, file_path in [("Temperature", self.nc_t_path),
                                      ("U-Wind", self.nc_u_path),
                                      ("V-Wind", self.nc_v_path)]:
            if not file_path or not os.path.exists(file_path):
                missing_files.append(file_label)

        if missing_files:
            raise FileNotFoundError(f"Missing required datasets: {', '.join(missing_files)}")

    def load_and_process_data(self):
        """Opens datasets, extracts coordinate arrays, and calculates wind metrics."""
        self.dt = xr.open_dataset(self.nc_t_path)
        self.du = xr.open_dataset(self.nc_u_path)
        self.dv = xr.open_dataset(self.nc_v_path)

        self.temp = self.dt["t2m"].squeeze().values
        self.longitude = self.dt["longitude"].values
        self.latitude = self.dt["latitude"].values
        self.x_coords = self.dt["x"].values
        self.y_coords = self.dt["y"].values

        self.u = self.du["u10"].squeeze().values
        self.v = self.dv["v10"].squeeze().values

        self.wind_speed = np.sqrt(self.u**2 + self.v**2)
        self.temp_units = self.dt["t2m"].attrs.get("units", "unknown")

        self._setup_projection()

    def _setup_projection(self):
        """Parses CRS metadata map parameters to set up Lambert Conformal Conic."""
        crs_attrs = self.dt["CRS"].attrs
        lat_origin = crs_attrs["latitude_of_projection_origin"]
        lon_central = crs_attrs["longitude_of_central_meridian"]
        std_parallels = crs_attrs["standard_parallel"]

        self.lcc_proj = ccrs.LambertConformal(
            central_longitude=lon_central,
            central_latitude=lat_origin,
            standard_parallels=(std_parallels, std_parallels),
        )

    def _create_base_map(self):
        """Initializes figure canvas, map frame layers, and standard grid lines."""
        fig, ax = plt.subplots(figsize=(12, 9), subplot_kw={"projection": self.lcc_proj})

        ax.set_extent(
            [self.x_coords.min(), self.x_coords.max(), self.y_coords.min(), self.y_coords.max()],
            crs=self.lcc_proj,
        )

        ax.add_feature(cfeature.COASTLINE, edgecolor="black", linewidth=1.2)
        ax.add_feature(cfeature.BORDERS, edgecolor="black", linestyle=":")

        gl = ax.gridlines(draw_labels=True, linewidth=1, color="dimgray", alpha=0.4, linestyle="--")
        gl.top_labels = False
        gl.right_labels = False
        gl.xlocator = mticker.FixedLocator(range(-180, 180, 5))
        gl.ylocator = mticker.FixedLocator(range(-90, 90, 5))
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {"size": 10, "weight": "bold"}
        gl.ylabel_style = {"size": 10, "weight": "bold"}
        gl.xpadding = 10
        gl.edge_labels = False
        gl.x_inline = False
        gl.y_inline = False

        return fig, ax

    def _add_color_bar(self, fig, ax, mesh):
        """Appends color bar metadata underneath frame display box."""
        cbar = fig.colorbar(mesh, ax=ax, orientation="horizontal", pad=0.12, shrink=0.7, aspect=30)
        cbar.set_label(f"Temperature ({self.temp_units})", fontsize=11)

    def _finalize_and_save(self, fig, output_filename):
        """Saves canvas layout to file or brings window forward context-safely."""
        plt.tight_layout()
        if output_filename:
            fig.savefig(output_filename, dpi=150, bbox_inches='tight')
            plt.close(fig)
        else:
            plt.show()

    def plot_contour_only(self, output_filename, title="Temperature"):
        fig, ax = self._create_base_map()
        mesh = ax.pcolormesh(self.longitude, self.latitude, self.temp,
                             transform=ccrs.PlateCarree(), cmap="turbo", shading="auto")
        
        contour_levels = np.arange(5, self.wind_speed.max(), 5)
        if len(contour_levels) > 0:
            contours = ax.contour(self.longitude, self.latitude, self.wind_speed,
                                  levels=contour_levels, colors="white",
                                  linewidths=0.8, alpha=0.7, transform=ccrs.PlateCarree())
            ax.clabel(contours, inline=True, fmt="%d m/s", fontsize=8, colors="white")

        self._add_color_bar(fig, ax, mesh)
        plt.title(title, fontsize=14, pad=20)
        self._finalize_and_save(fig, output_filename)

    def plot_windbarb_only(self, output_filename):
        fig, ax = self._create_base_map()
        mesh = ax.pcolormesh(self.longitude, self.latitude, self.temp,
                             transform=ccrs.PlateCarree(), cmap="turbo", shading="auto")

        u_knots = self.u * 1.94384
        v_knots = self.v * 1.94384
        skip_barbs = 12
        ax.barbs(
            self.longitude[::skip_barbs, ::skip_barbs],
            self.latitude[::skip_barbs, ::skip_barbs],
            u_knots[::skip_barbs, ::skip_barbs],
            v_knots[::skip_barbs, ::skip_barbs],
            transform=ccrs.PlateCarree(),
            color="black", length=5.5, linewidth=0.8
        )

        self._add_color_bar(fig, ax, mesh)
        plt.title("Wind Barb Field (Velocity Vectors in Knots)", fontsize=14, pad=20)
        self._finalize_and_save(fig, output_filename)

    def plot_windbarb_overlay_contour(self, output_filename):
        fig, ax = self._create_base_map()
        mesh = ax.pcolormesh(self.longitude, self.latitude, self.temp,
                             transform=ccrs.PlateCarree(), cmap="turbo", shading="auto")

        contour_levels = np.arange(5, self.wind_speed.max(), 5)
        if len(contour_levels) > 0:
            contours = ax.contour(self.longitude, self.latitude, self.wind_speed,
                                  levels=contour_levels, colors="white",
                                  linewidths=0.8, alpha=0.7, transform=ccrs.PlateCarree())
            ax.clabel(contours, inline=True, fmt="%d m/s", fontsize=8, colors="white")

        u_knots = self.u * 1.94384
        v_knots = self.v * 1.94384
        skip_barbs = 12
        ax.barbs(
            self.longitude[::skip_barbs, ::skip_barbs],
            self.latitude[::skip_barbs, ::skip_barbs],
            u_knots[::skip_barbs, ::skip_barbs],
            v_knots[::skip_barbs, ::skip_barbs],
            transform=ccrs.PlateCarree(),
            color="black", length=5.5, linewidth=0.8
        )

        self._add_color_bar(fig, ax, mesh)
        plt.title("Wind Field Composition (Temperature, Contours & Barbs)", fontsize=14, pad=20)
        self._finalize_and_save(fig, output_filename)

# =====================================================================
# 2. THE GUI APPLICATION INTERFACE
# =====================================================================
class EagleVisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Eagle Visualizer Application Engine")
        self.root.geometry("620x450")
        self.root.minsize(550, 420)

        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Load YAML configuration settings
        config = self._load_yaml_config("config.yaml")
        print(f"config = {config}")
        defaults = config.get("default_paths", {})
        print(f"defaults = {defaults}")

        # Container Frame
        main_frame = ttk.Frame(root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- FILE INPUT SECTION ---
        file_lf = ttk.LabelFrame(main_frame, text=" Data Import Configuration (NetCDF) ", padding="10")
        file_lf.pack(fill=tk.X, pady=(0, 10))

        # Assign variables pulling defaults directly from config dictionary
        self.t_path = tk.StringVar(value=defaults.get("nc_2m_t", ""))
        self.u_path = tk.StringVar(value=defaults.get("nc_10m_u", ""))
        self.v_path = tk.StringVar(value=defaults.get("nc_10m_v", ""))

        self._create_file_row(file_lf, "Temperature Dataset (-t):", self.t_path, 0)
        self._create_file_row(file_lf, "U-Component Wind (-u):", self.u_path, 1)
        self._create_file_row(file_lf, "V-Component Wind (-v):", self.v_path, 2)

        # --- RENDER OPTIONS SECTION ---
        options_lf = ttk.LabelFrame(main_frame, text=" Plot Visualization Configuration ", padding="10")
        options_lf.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(options_lf, text="Map Render Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.plot_type = tk.StringVar(value="Composition Overlay (All)")
        plot_choices = ["Contour Only", "Wind Barbs Only", "Composition Overlay (All)"]
        self.plot_dropdown = ttk.Combobox(options_lf, textvariable=self.plot_type,
                                          values=plot_choices, state="readonly", width=30)

        self.plot_dropdown.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(options_lf, text="Output Context:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_mode = tk.StringVar(value="screen")
        ttk.Radiobutton(options_lf, text="Show Interactive On Screen", variable=self.output_mode, value="screen",
                        command=self._toggle_save_row).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(options_lf, text="Export Directly to Image File", variable=self.output_mode, value="file",
                        command=self._toggle_save_row).grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        # Dynamic Save Destination Row
        self.save_frame = ttk.Frame(options_lf)
        self.save_path = tk.StringVar(value=defaults.get("output_image", "output_plot.png"))
        ttk.Label(self.save_frame, text="Save Destination File:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(self.save_frame, textvariable=self.save_path, width=35).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(self.save_frame, text="Browse", command=self._browse_save_location).pack(side=tk.RIGHT)

        # --- STATUS & EXECUTION BAR ---
        self.progress_bar = ttk.Progressbar(main_frame, mode="indeterminate")
        self.run_button = ttk.Button(main_frame, text="⚡ Generate Map Visualization",
                                     command=self._start_processing_thread)
        self.run_button.pack(fill=tk.X, ipady=8, side=tk.BOTTOM)
        self.status_label = ttk.Label(main_frame,
                                      text="System Ready: Configuration loaded successfully.",
                                      font=("Arial", 9, "italic"), foreground="dimgray")
        self.status_label.pack(side=tk.BOTTOM, anchor=tk.W, pady=(10, 5))

    def _load_yaml_config(self, filepath):
        """Safely opens configuration YAML layout files, returning empty dict if missing."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                print(f"[WARNING] Failed parsing {filepath}: {e}. Loading blank setup instead.", file=sys.stderr)
        return {}

    def _create_file_row(self, parent, label_text, var_target, grid_row):
        ttk.Label(parent, text=label_text).grid(row=grid_row, column=0, sticky=tk.W, pady=3)
        ttk.Entry(parent, textvariable=var_target, width=45).grid(row=grid_row, column=1, sticky=tk.EW, padx=5, pady=3)
        ttk.Button(parent, text="Browse...", command=lambda: self._browse_nc_file(var_target)).grid(row=grid_row, column=2, padx=2, pady=3)
        parent.columnconfigure(1, weight=1)

    def _browse_nc_file(self, target_var):
        path = filedialog.askopenfilename(filetypes=[("NetCDF Files", ".nc"), ("All Files", ".*")])
        if path:
            target_var.set(path)

    def _browse_save_location(self):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", ".png"), ("PDF Document", ".pdf")])
        if path:
            self.save_path.set(path)

    def _toggle_save_row(self):
        if self.output_mode.get() == "file":
            self.save_frame.pack(fill=tk.X, columnspan=3, pady=5, anchor=tk.W)
        else:
            self.save_frame.pack_forget()

    def _start_processing_thread(self):
        self.run_button.config(state=tk.DISABLED)
        self.progress_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 5))
        self.progress_bar.start(10)
        self.status_label.config(text="Processing Map Vector Arrays... please wait.", foreground="blue")
        threading.Thread(target=self._execute_visualization_pipeline, daemon=True).start()
    def _execute_visualization_pipeline(self):
        try:
            t_file = self.t_path.get().strip()
            u_file = self.u_path.get().strip()
            v_file = self.v_path.get().strip()
            mode = self.output_mode.get()
            out_file = self.save_path.get().strip() if mode == "file" else None
            selected_plot = self.plot_type.get()
            engine = WindFieldVisualizer(t_file, u_file, v_file)
            engine.load_and_process_data()
            if selected_plot == "Contour Only":
                engine.plot_contour_only(out_file)
            elif selected_plot == "Wind Barbs Only":
                engine.plot_windbarb_only(out_file)
            else:
                engine.plot_windbarb_overlay_contour(out_file)
            self.root.after(0, lambda: self._handle_pipeline_success(mode, out_file))
        except Exception as err:
            self.root.after(0, lambda: self._handle_pipeline_failure(str(err)))

    def _handle_pipeline_success(self, mode, out_file):
        self._reset_ui_state()
        self.status_label.config(text="Map Render Completed Successfully.", foreground="green")
        if mode == "file":
            messagebox.showinfo("Success", f"Plot frame successfully written to destination:\n{out_file}")

    def _handle_pipeline_failure(self, error_message):
        self._reset_ui_state()
        self.status_label.config(text="Execution Terminated with Errors.", foreground="red")
        messagebox.showerror("Execution Matrix Error", f"An explicit runtime error halted data handling:\n\n{error_message}")

    def _reset_ui_state(self):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.run_button.config(state=tk.NORMAL)

## =====================================================================
## 3. RUNTIME INITIALIZATION
## =====================================================================
if __name__ == "__main__":
    plt.ioff()
    root = tk.Tk()
    app = EagleVisApp(root)
    root.mainloop()


#<FollowUp>
#If you want to allow the user to modify options within the interface, tell me if we should **add a "Save Configuration As Default" button** to the UI. This button would write whatever file paths the user currently has selected back out to the `config.yaml` file so they become the new defaults for the next launch.
#</FollowUp>


#[1] [https://community.sap.com](https://community.sap.com/t5/product-lifecycle-management-blog-posts-by-sap/sap-3d-visual-enterprise-generator-config-file-best-practice/ba-p/13523014)
#[2] [https://networkotaku.wordpress.com](https://networkotaku.wordpress.com/2017/06/06/network-automation-template-configurations-with-jinja2-and-yaml/)
#[3] [https://dev.to](https://dev.to/emekaofe/how-to-pass-environment-variables-to-a-yaml-file-in-a-nodejs-application-using-ejs-templating-engine-ib7)
#[4] [https://dev.to](https://dev.to/emekaofe/how-to-pass-environment-variables-to-a-yaml-file-in-a-nodejs-application-using-ejs-templating-engine-ib7)

