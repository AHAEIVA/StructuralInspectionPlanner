# STL Generation and Processing Scripts

This directory contains Python scripts for generating and processing STL files, primarily for preparing 3D models for structural inspection planning.

## Scripts

### 1. `hollow_pipe_stl_generator.py`

Generates an STL file of a hollow horizontal pipe.

**Usage:**

```bash
python hollow_pipe_stl_generator.py <diameter> <length> <output_file.stl>
```

**Arguments:**

*   `diameter`: (float) The outer diameter of the pipe.
*   `length`: (float) The length of the pipe.
*   `output_file.stl`: (str) The path to the output STL file.

**Example:**

```bash
python hollow_pipe_stl_generator.py 1.0 5.0 pipe_output.stl
```
This command generates `pipe_output.stl` representing a pipe with an outer diameter of 1.0 unit and a length of 5.0 units. The inner diameter is hardcoded to be 80% of the outer diameter.

### 2. `pipe_with_stands.py`

Generates an STL file of a hollow horizontal pipe with supporting stands at both ends.

**Usage:**

```bash
python pipe_with_stands.py <diameter> <length> <output_file.stl> [--stand_height <height>]
```

**Arguments:**

*   `diameter`: (float) The outer diameter of the pipe.
*   `length`: (float) The length of the pipe.
*   `output_file.stl`: (str) The path to the output STL file.
*   `--stand_height <height>`: (float, optional) The height of the supporting plates below the pipe. Default is 0.2.

**Example:**

```bash
python pipe_with_stands.py 0.5 3.0 pipe_stands_output.stl --stand_height 0.3
```
This command generates `pipe_stands_output.stl` for a pipe with an outer diameter of 0.5, length of 3.0, and stand height of 0.3 units.

### 3. `refine_normals.py`

Processes an STL file (ASCII or Binary) to remove triangles whose normals are aligned with a specified axis (within a given tolerance). This is useful for removing unwanted faces, like the top and bottom surfaces of a flat model, or internal surfaces. The output is always an ASCII STL file.

**Usage:**

```bash
python refine_normals.py <input_file.stl> [-o <output_file.stl>] [--filter-axis {x,y,z}] [-a <angle>] [-r]
```

**Arguments:**

*   `input_file.stl`: (str) Input STL (ASCII or Binary) file path.
*   `-o <output_file.stl>` or `--output <output_file.stl>`: (str, optional) Output STL ASCII file path. If not provided, defaults to `[input_file_base]_filtered[input_file_ext]`.
*   `--filter-axis {x,y,z}`: (str, optional) Axis to filter normals against. Triangles whose normals are aligned (within `angle`) with either the positive or negative direction of this axis are removed. Default is `y`.
*   `-a <angle>` or `--angle <angle>`: (float, optional) Maximum angle (in degrees) from the specified axis (both positive and negative directions) for a normal to be considered "aligned". Triangles are kept if their normal's angle is greater than this value with respect to *both* the positive and negative axis directions. Default is `10`.
*   `-r` or `--recalculate-normals`: (flag, optional) Recalculate normals from vertices before filtering.

**Example:**

```bash
python refine_normals.py model.stl -o model_refined.stl --filter-axis z -a 15 --recalculate-normals
```
This command processes `model.stl`, recalculates its normals, removes triangles whose normals are within 15 degrees of either the positive or negative Z-axis, and saves the result to `model_refined.stl`.

### 4. `transform_stl_axes.py`

Transforms an STL file (ASCII or Binary) by swapping its Y and Z axes (coordinates `(x, y, z)` become `(x, z, y)`). It can also optionally center the mesh at the origin. The output is always an ASCII STL file.

**Usage:**

```bash
python transform_stl_axes.py <input_file.stl> <output_file.stl> [--center]
```

**Arguments:**

*   `input_file.stl`: (str) Input STL (ASCII or Binary) file path.
*   `output_file.stl`: (str) Output STL ASCII file path for the transformed model.
*   `--center`: (flag, optional) Center the mesh at the origin (0,0,0) after the axis transformation.

**Example:**

```bash
python transform_stl_axes.py raw_model.stl transformed_model.stl --center
```
This command reads `raw_model.stl`, swaps its Y and Z axes, centers the resulting mesh at the origin, and saves it as `transformed_model.stl`.

## Notes

*   Ensure you have Python 3 and NumPy installed (`pip install numpy`).
*   These scripts primarily output ASCII STL files, which are human-readable but can be larger than binary STL files.
*   The `refine_normals.py` and `transform_stl_axes.py` scripts can handle both ASCII and binary STL files as input, heuristically determining the format.
