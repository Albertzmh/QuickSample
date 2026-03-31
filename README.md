# QuickSample — QGIS Plugin

A lightweight QGIS plugin to quickly sample and preview features from any vector layer, with CSV and GeoPackage export.

---

## Features

| Sampling Method | Description |
|---|---|
| **First N** | Returns the first N features in the layer |
| **Last N** | Returns the last N features |
| **Random N** | Randomly selects N features |
| **Percentage** | Randomly selects X% of all features |

### Export Options
- **Export to CSV** — saves attribute data (no geometry) to a `.csv` file
- **Save as New Layer** — saves the sample (with geometry) to a `.gpkg` file and loads it into QGIS
- **Select on Map** — highlights sampled features in the map canvas and opens the attribute table

---

## Installation

1. Download or clone this repository
2. Copy the `quicksample/` folder into your QGIS plugins directory:
   - **Windows:** `C:\Users\<you>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - **macOS:** `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
   - **Linux:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
3. Restart QGIS
4. Go to **Plugins → Manage and Install Plugins** and enable **QuickSample**

---

## Usage

1. Select a vector layer in the Layers panel
2. Click the **QuickSample** toolbar button (or go to **Vector → QuickSample**)
3. Choose a sampling method and set N or percentage
4. Click **Run Sampling** to preview the results
5. Optionally export or highlight the sampled features

---

## File Structure

```
quicksample/
├── __init__.py       # QGIS plugin entry point
├── metadata.txt      # Plugin metadata
├── plugin.py         # Plugin class (toolbar/menu registration)
├── dialog.py         # Main UI dialog
├── sampler.py        # Core sampling logic
├── exporter.py       # CSV and GeoPackage export
├── icon.png          # Toolbar icon
└── README.md
```

---

## Requirements

- QGIS 3.0+
- No additional Python packages required

---

## License

GPL v2
