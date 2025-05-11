import math
import re
import os
import struct
import argparse

# --- Copied and adapted from refine_normals.py ---
def is_stl_binary(file_path):
    """
    Heuristically determine if an STL file is binary.
    ASCII STL files start with "solid".
    """
    try:
        with open(file_path, 'rb') as f:
            header_chunk = f.read(5)
        return not header_chunk.startswith(b'solid')
    except Exception:
        print(f"Warning: Could not reliably determine if {file_path} is binary. Assuming binary.")
        return True

def parse_stl_binary(file_path):
    """Parse a BINARY STL file and extract the triangles with their normals."""
    triangles = []
    solid_name = os.path.splitext(os.path.basename(file_path))[0] + "_transformed"

    with open(file_path, 'rb') as f:
        header = f.read(80)  # Skip 80-byte header
        num_triangles_bytes = f.read(4)
        if len(num_triangles_bytes) < 4:
            raise ValueError("Invalid binary STL file: too short to read number of triangles.")
        num_triangles = struct.unpack('<I', num_triangles_bytes)[0]

        for _ in range(num_triangles):
            data = f.read(50)
            if len(data) < 50:
                print(f"Warning: File ended prematurely after reading {len(triangles)} triangles. Expected {num_triangles}.")
                break
            parts = struct.unpack('<3f3f3f3fH', data[:4*3*4 + 2])
            normal = (parts[0], parts[1], parts[2])
            vertices = [
                (parts[3], parts[4], parts[5]),
                (parts[6], parts[7], parts[8]),
                (parts[9], parts[10], parts[11])
            ]
            triangles.append({'normal': normal, 'vertices': vertices})
    return solid_name, triangles

def parse_stl_ascii(file_path):
    """Parse an ASCII STL file and extract the triangles with their normals."""
    triangles = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            print(f"Warning: UTF-8 decoding failed for {file_path}. Trying latin-1.")
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            raise ValueError(f"Could not read file {file_path} as ASCII (tried UTF-8 and latin-1). Error: {e}")

    normal_pattern = r'facet normal\s+([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s+([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s+([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*'
    vertex_pattern = r'vertex\s+([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s+([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s+([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*'
    
    solid_match = re.search(r'solid\s+(.*)', content)
    solid_name = solid_match.group(1).strip() if solid_match else os.path.splitext(os.path.basename(file_path))[0]
    solid_name += "_transformed"

    facet_blocks = re.findall(r'facet normal.*?endfacet', content, re.DOTALL)
    for block in facet_blocks:
        normal_match = re.search(normal_pattern, block)
        if normal_match:
            normal = tuple(map(float, normal_match.groups()))
        else:
            normal = (0.0, 0.0, 0.0)
        
        vertices_match = re.findall(vertex_pattern, block)
        if len(vertices_match) == 3:
            vertices = [tuple(map(float, v)) for v in vertices_match]
            triangles.append({'normal': normal, 'vertices': vertices})
    return solid_name, triangles

def write_stl_ascii(file_path, solid_name, triangles):
    """Write triangles to a new ASCII STL file."""
    with open(file_path, 'w') as f:
        f.write(f"solid {solid_name}\n")
        for triangle in triangles:
            normal = triangle['normal']
            f.write(f"  facet normal {normal[0]:.6e} {normal[1]:.6e} {normal[2]:.6e}\n")
            f.write("    outer loop\n")
            for vertex in triangle['vertices']:
                f.write(f"      vertex {vertex[0]:.6e} {vertex[1]:.6e} {vertex[2]:.6e}\n")
            f.write("    endloop\n")
            f.write("  endfacet\n")
        f.write(f"endsolid {solid_name}\n")
# --- End of copied functions ---

def transform_y_to_z(coord_tuple):
    """Transforms (x, y, z) to (x, z, y)."""
    x, y, z = coord_tuple
    return (x, z, y)

def calculate_geometric_center(triangles):
    """Calculate the geometric center of all vertices in the mesh."""
    if not triangles:
        return (0.0, 0.0, 0.0)
    
    all_vertices = [vertex for tri in triangles for vertex in tri['vertices']]
    if not all_vertices:
        return (0.0, 0.0, 0.0)
        
    sum_x = sum(v[0] for v in all_vertices)
    sum_y = sum(v[1] for v in all_vertices)
    sum_z = sum(v[2] for v in all_vertices)
    
    num_vertices = len(all_vertices)
    return (sum_x / num_vertices, sum_y / num_vertices, sum_z / num_vertices)

def translate_vertex(vertex, translation_vector):
    """Translate a single vertex."""
    return (vertex[0] + translation_vector[0],
            vertex[1] + translation_vector[1],
            vertex[2] + translation_vector[2])

def main():
    parser = argparse.ArgumentParser(description='Transform an STL file by swapping Y and Z axes (Y becomes Z) and optionally center it.')
    parser.add_argument('input_file', help='Input STL (ASCII or Binary) file path.')
    parser.add_argument('output_file', help='Output STL ASCII file path for the transformed model.')
    parser.add_argument('--center', action='store_true', help='Center the mesh at the origin (0,0,0) after axis transformation.')
    
    args = parser.parse_args()
    
    print(f"Processing {args.input_file}...")
    
    if is_stl_binary(args.input_file):
        print(f"Detected binary STL: {args.input_file}")
        solid_name, triangles = parse_stl_binary(args.input_file)
    else:
        print(f"Detected ASCII STL: {args.input_file}")
        solid_name, triangles = parse_stl_ascii(args.input_file)
    
    # Perform axis transformation
    axis_transformed_triangles = []
    for triangle in triangles:
        transformed_normal = transform_y_to_z(triangle['normal'])
        transformed_vertices = [transform_y_to_z(v) for v in triangle['vertices']]
        axis_transformed_triangles.append({
            'normal': transformed_normal,
            'vertices': transformed_vertices
        })
    print(f"Transformed {len(axis_transformed_triangles)} triangles (Y-axis to Z-axis).")

    final_triangles = axis_transformed_triangles
    
    # Optionally center the mesh
    if args.center:
        if not final_triangles:
            print("No triangles to center.")
        else:
            center = calculate_geometric_center(final_triangles)
            print(f"Calculated geometric center: {center}")
            translation_vector = (-center[0], -center[1], -center[2])
            print(f"Applying translation vector: {translation_vector}")
            
            centered_triangles = []
            for triangle in final_triangles:
                # Normals are not affected by translation
                centered_vertices = [translate_vertex(v, translation_vector) for v in triangle['vertices']]
                centered_triangles.append({
                    'normal': triangle['normal'], # Keep original (axis-transformed) normal
                    'vertices': centered_vertices
                })
            final_triangles = centered_triangles
            solid_name += "_centered" # Append to solid name
            print(f"Centered {len(final_triangles)} triangles at the origin.")

    print(f"Writing final STL to {args.output_file}...")
    
    # Adjust solid name if it wasn't set by parser or if only centering was done
    if "_transformed" not in solid_name and "_centered" not in solid_name :
         solid_name_base = os.path.splitext(os.path.basename(args.output_file))[0]
         solid_name = solid_name_base
    elif "_transformed" not in solid_name and args.center: # if only centering was conceptually done (though here it's post-transform)
        solid_name = os.path.splitext(os.path.basename(args.input_file))[0] + "_centered"


    write_stl_ascii(args.output_file, solid_name, final_triangles)
    print("Done!")

if __name__ == "__main__":
    main()
