# Diffusion Analysis Pipeline

A flexible, reproducible workflow for analyzing diffusion processes from microscopy images, exported, processed, and visualized with open-source tools.

---

## Table of Contents

- [Overview](#overview)
- [Workflow](#workflow)
  - [1. Image Acquisition](#1-image-acquisition)
  - [2. Data Export & Organization](#2-data-export--organization)
  - [3. Data Analysis (Python)](#3-data-analysis-python)
  - [4. Data Processing](#4-data-processing)
  - [5. Normalization](#5-normalization)
  - [6. Visualization & Output](#6-visualization--output)
- [Priority Features & Roadmap](#priority-features--roadmap)
- [Setup & Requirements](#setup--requirements)
- [Citation](#citation)
- [License](#license)

---

## Overview

This repository provides a complete toolkit for extracting, normalizing, and visualizing diffusion profiles from microscopy-based time series images. The workflow is designed to be modular, open, and compatible with downstream figure editing.

---

## Workflow

### 1. Image Acquisition

- Produce raw images with your microscope and save them as `.czi` files.

### 2. Data Export & Organization

- Export `.czi` images to `.tiff` using your microscope software (e.g., Zeiss Zen).
- Organize images **by chip**, so each chip has its own folder:
  - Typically: `1_brightfield.tiff` (reference image)
  - ~37 grayscale images over time, one per timepoint

### 3. Data Analysis (Python)

> **No MATLAB or Excel required!**
> Place your analysis script in the same directory as the image folders.

**Typical workflow:**

1. **Configure the script**:
   - Set the correct folder/chip name and desired output file name.
   - Defaults:
     ```
     CHIP_FOLDER = "Chip_01"
     OUTPUT_NAME = "experiment_01.txt"
     DATA_POINTS = 200
     ```

2. **Define ROI (Region of Interest):**
   - The script loads the first image (brightfield) for you to draw a line in your region of interest.
   - The software will divide this line into *N* (default 200) data points.

3. **Intensity Extraction:**
   - For each timepoint image, the script extracts intensity values along the ROI.
   - Results are saved to a `.txt` file:
     - Each line = one image/timepoint
     - Each value = intensity at a position along the line

### 4. Data Processing

- Import the `.txt` file (e.g., pandas, Excel, or Origin).
- Transpose if needed: **columns = time, rows = position along the line**
- **Source**: For each timepoint in each chip, calculate the average of the first five data points.
- **Sink**: For each timepoint in each chip, calculate the average of the last five data points.

### 5. Normalization

- Set 100% as the *maximum* source value, and 0% as the *minimum* sink value.
- For each data point:
    $$
    \text{normalized value} = \frac{\text{value} - \text{Sink}_{min}}{\text{Source}_{max} - \text{Sink}_{min}} \times 100
    $$

- The step size for normalization is:
    $$
    \frac{(max - min)}{100}
    $$

### 6. Visualization & Output

#### Plotting

- Graphs can be generated via Python (`matplotlib`) or imported into Origin.
- Save graphs as `.svg` for high-quality, editable vector graphics (perfect for Adobe Illustrator).
- Example:
    ```
    plt.plot(time_axis, normalized.mean(axis=0))
    plt.savefig("diffusion_plot.svg", format='svg', dpi=300)
    ```

#### Diffusion Distance (Advanced)

- The analysis includes calculating diffusion distances at user-defined thresholds (for example, where the normalized value crosses 50%).
- Output is compatible with further vector editing.

---

## Priority Features & Roadmap

1. **[X]** Import `.txt`, output normalized values (Python first).
2. **[X]** Calculate diffusion distances based on user-defined thresholds.
3. **[ ]** Export graphics in `.svg` format (Adobe Illustrator compatible).
4. **[ ]** Option to fully analyze with Python for all steps.

---

## Setup & Requirements

- **Python ≥3.8**
- **Packages:**
- `numpy`
- `pandas`
- `scikit-image`
- `matplotlib`
- `tifffile`
- For plotting/editing: OriginLab (optional), Adobe Illustrator (optional)

### Installation (recommended)
To install the required packages:
```
pip install --upgrade -r requirements.txt
```
To update the required packages while under development:
```
pip freeze | sed 's/==/>=/' > requirements.txt
```

---

## Citation

If you use this pipeline, please cite this repository and credit the original authors.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

#### Legacy MATLAB and Excel templates are available in `/archive` for reference.
