# Progress

## What Works:

*   **`stl_generation/refine_normals.py`:**
    *   Successfully parses both ASCII and Binary STL files.
    *   Filters triangles based on their normal's angle to a user-specified axis (X, Y, or Z via `--filter-axis` argument). Triangles are removed if their normal is aligned (within `max_angle`) with *either the positive or negative* direction of the specified axis.
    *   Can recalculate normals from vertices.
    *   Outputs a filtered ASCII STL file.
*   **`stl_generation/transform_stl_axes.py`:**
    *   Successfully parses both ASCII and Binary STL files.
    *   Transforms coordinates by swapping Y and Z axes (X->X, Y->Z, Z->Y).
    *   Optionally centers the mesh at the origin (0,0,0) using the `--center` flag.
    *   Outputs a transformed (and optionally centered) ASCII STL file.
*   **`results_visualisation/visualize_path.py`:**
    *   Copies `koptplanner/data/latestPath.csv` to the `results_visualisation` directory.
    *   Visualizes the 3D path from the copied CSV file using `matplotlib`.
    *   Loads and displays the `dfki_pipe.stl` model from `request/meshes/` using `numpy-stl`.
    *   Adjusts plot limits to encompass both the path and the STL model.
    *   Features include reduced point resolution, direction arrows (quivers) derived from yaw angle (X/Y) and Z-difference (Z), path transparency (alpha=0.5), shorter arrows (length=0.2), and labels for start/end points.
*   Initial project structure seems to be in place with various modules (`koptplanner`, `optec`, `stl_generation`, `utils`, `request`).
*   Build system (CMake, Make) is present.
*   Some example/test cases or parameter files exist (e.g., `koptplanner/bigBenParam.yaml`, `request/src/bigBen.cpp`).
*   Utility scripts for exporting paths to different formats exist.
*   Trajectory output path identified: `koptplanner/data/latestPath.csv`.

## What's Left to Build / Current Tasks:

*   **Broader Goals (from `projectbrief.md`):**
    *   Robust STL file parsing (ASCII and Binary) - *Partially addressed by `refine_normals.py` improvements.*
    *   Accurate normal vector calculation and refinement - *`refine_normals.py` includes functionality for this.*
    *   Implementation and testing of core path planning algorithms.
    *   Integration of different modules (preprocessing, planning, output, visualization).
    *   Development/refinement of visualization tools.
    *   Testing with a variety of complex 3D models and inspection scenarios.
    *   User interface development (if planned).
    *   Comprehensive documentation.

## Current Status:

*   **Overall:** Project is in a developmental stage. Core components for planning and 3D model handling are being built.
*   **Memory Bank:** Initialized with core files (`projectbrief.md`, `productContext.md`, `activeContext.md`, `systemPatterns.md`, `techContext.md`, this file `progress.md`).
*   **`refine_normals.py` script:** Functional. Successfully processes ASCII and binary STL files and allows filtering along X, Y, or Z axes, considering both positive and negative directions.
*   **`transform_stl_axes.py` script:** Functional. Transforms STL coordinates by swapping Y and Z axes and can optionally center the mesh.
*   **`results_visualisation/visualize_path.py` script:** Created and enhanced with improved plotting features.

## Known Issues:

*   **RESOLVED:** `UnicodeDecodeError` in `refine_normals.py`.
    *   **Fix:** The script was updated to detect and parse both ASCII and binary STL file formats correctly. This was further enhanced to allow axis-specific filtering.
*   *(Other issues will be added here as they are discovered.)*
