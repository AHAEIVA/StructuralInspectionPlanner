import math
import re
import numpy as np
import os
import struct
import argparse

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
        # In case of error reading, assume binary to be safe or handle error
        print(f"Warning: Could not reliably determine if {file_path} is binary. Assuming binary.")
        return True

def parse_stl_binary(file_path):
    """Parse a BINARY STL file and extract the triangles with their normals."""
    triangles = []
    solid_name = os.path.splitext(os.path.basename(file_path))[0] + "_binary_solid"

    with open(file_path, 'rb') as f:
        header = f.read(80)  # Skip 80-byte header
        num_triangles_bytes = f.read(4)
        if len(num_triangles_bytes) < 4:
            raise ValueError("Invalid binary STL file: too short to read number of triangles.")
        num_triangles = struct.unpack('<I', num_triangles_bytes)[0] # Little-endian unsigned int

        for _ in range(num_triangles):
            data = f.read(50) # Each triangle is 50 bytes
            if len(data) < 50:
                print(f"Warning: File ended prematurely after reading {len(triangles)} triangles. Expected {num_triangles}.")
                break
            
            # Normal (3 floats), Vertex1 (3 floats), Vertex2 (3 floats), Vertex3 (3 floats), Attribute byte count (2 bytes)
            # Each float is 4 bytes (single precision)
            parts = struct.unpack('<3f3f3f3fH', data[:4*3*4 + 2]) # 12 floats + 1 short int

            normal = (parts[0], parts[1], parts[2])
            vertices = [
                (parts[3], parts[4], parts[5]),
                (parts[6], parts[7], parts[8]),
                (parts[9], parts[10], parts[11])
            ]
            # attribute_byte_count = parts[12] # Ignored for now

            triangles.append({
                'normal': normal,
                'vertices': vertices
            })
            
    return solid_name, triangles

def parse_stl_ascii(file_path):
    """Parse an ASCII STL file and extract the triangles with their normals."""
    triangles = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f: # Specify encoding
            content = f.read()
    except UnicodeDecodeError:
        # This might happen if is_stl_binary heuristic failed and it's actually binary
        # or an ASCII file with a very unusual encoding not compatible with utf-8.
        # Try with latin-1 as a fallback for misidentified binary or other encodings.
        try:
            print(f"Warning: UTF-8 decoding failed for {file_path}. Trying latin-1.")
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            raise ValueError(f"Could not read file {file_path} as ASCII (tried UTF-8 and latin-1). Error: {e}")

    # Regular expressions to extract normal vectors and vertices
    normal_pattern = r'facet normal ([-+]?\d*\.\d+|\d+) ([-+]?\d*\.\d+|\d+) ([-+]?\d*\.\d+|\d+)'
    vertex_pattern = r'vertex ([-+]?\d*\.\d+|\d+) ([-+]?\d*\.\d+|\d+) ([-+]?\d*\.\d+|\d+)'
    
    # Extract solid name
    solid_match = re.search(r'solid (.*)', content)
    solid_name = solid_match.group(1) if solid_match else "filtered_solid"
    
    # Find all facets
    facet_blocks = re.findall(r'facet.*?endfacet', content, re.DOTALL)
    
    for block in facet_blocks:
        # Extract normal
        normal_match = re.search(normal_pattern, block)
        if normal_match:
            nx = float(normal_match.group(1))
            ny = float(normal_match.group(2))
            nz = float(normal_match.group(3))
            normal = (nx, ny, nz)
        else:
            normal = (0, 0, 0)  # Default if not found
        
        # Extract vertices
        vertices_match = re.findall(vertex_pattern, block)
        if len(vertices_match) == 3:  # A triangle should have 3 vertices
            vertices = []
            for vertex in vertices_match:
                x = float(vertex[0])
                y = float(vertex[1])
                z = float(vertex[2])
                vertices.append((x, y, z))
            
            triangles.append({
                'normal': normal,
                'vertices': vertices
            })
    
    return solid_name, triangles

def normalize_vector(vector):
    """Normalize a vector."""
    magnitude = math.sqrt(sum(x*x for x in vector))
    if magnitude == 0:
        return (0, 0, 0)
    return tuple(x/magnitude for x in vector)

def angle_between(v1, v2):
    """Calculate the angle in degrees between two vectors."""
    v1_normalized = normalize_vector(v1)
    v2_normalized = normalize_vector(v2)
    
    # Calculate dot product
    dot_product = sum(a*b for a, b in zip(v1_normalized, v2_normalized))
    
    # Ensure the dot product is in the valid range for arccos
    dot_product = max(min(dot_product, 1.0), -1.0)
    
    # Calculate angle in radians and convert to degrees
    angle_rad = math.acos(dot_product)
    angle_deg = math.degrees(angle_rad)
    
    return angle_deg

def filter_axis_facing_triangles(triangles, axis_vector, max_angle=50):
    """
    Filter out triangles whose normals are pointing along EITHER the positive OR negative direction
    of the specified axis, or close to it.
    axis_vector: The positive direction of the axis to compare against (e.g., (1,0,0) for X).
    max_angle: maximum angle (in degrees) from EITHER the positive OR negative axis direction
               for a normal to be considered "aligned". Triangles are KEPT if their normal
               is NOT aligned with EITHER positive or negative axis directions.
    """
    filtered_triangles = []
    negative_axis_vector = tuple(-c for c in axis_vector)
    
    for triangle in triangles:
        normal = triangle['normal']
        
        angle_positive = angle_between(normal, axis_vector)
        angle_negative = angle_between(normal, negative_axis_vector)
        
        # Keep the triangle if its normal is NOT aligned with the positive direction
        # AND NOT aligned with the negative direction of the axis.
        # "Not aligned" means the angle is greater than max_angle.
        if angle_positive > max_angle and angle_negative > max_angle:
            filtered_triangles.append(triangle)
            
    return filtered_triangles

def recalculate_normals(triangle):
    """Recalculate the normal vector of a triangle from its vertices."""
    v1, v2, v3 = triangle['vertices']
    
    # Calculate two edges of the triangle
    edge1 = (v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2])
    edge2 = (v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2])
    
    # Calculate the cross product to get the normal
    normal = (
        edge1[1] * edge2[2] - edge1[2] * edge2[1],
        edge1[2] * edge2[0] - edge1[0] * edge2[2],
        edge1[0] * edge2[1] - edge1[1] * edge2[0]
    )
    
    # Normalize the normal vector
    return normalize_vector(normal)

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

def main():
    parser = argparse.ArgumentParser(description='Process an STL (ASCII or Binary) file to remove triangles with normals pointing along a specified axis.')
    parser.add_argument('input_file', help='Input STL (ASCII or Binary) file path')
    parser.add_argument('--output', '-o', help='Output STL ASCII file path (output is always ASCII)')
    parser.add_argument('--filter-axis', choices=['x', 'y', 'z'], default='y', help='Axis to filter normals against (default: z)')
    parser.add_argument('--angle', '-a', type=float, default=10, help='Maximum angle (in degrees) from the specified axis for a normal to be considered "aligned" with it (triangles with normals forming an angle greater than this with the axis are kept) (default: 50)')
    parser.add_argument('--recalculate-normals', '-r', action='store_true', help='Recalculate normals from vertices')
    
    args = parser.parse_args()
    
    # Set default output path if not provided
    if not args.output:
        base, ext = os.path.splitext(args.input_file)
        args.output = f"{base}_filtered{ext}"
    
    print(f"Processing {args.input_file}...")
    
    if is_stl_binary(args.input_file):
        print(f"Detected binary STL: {args.input_file}")
        solid_name, triangles = parse_stl_binary(args.input_file)
    else:
        print(f"Detected ASCII STL: {args.input_file}")
        solid_name, triangles = parse_stl_ascii(args.input_file)
    
    # Recalculate normals if requested
    if args.recalculate_normals:
        print("Recalculating normals from vertices...")
        for triangle in triangles:
            triangle['normal'] = recalculate_normals(triangle)
            
    # Determine filter axis vector
    if args.filter_axis == 'x':
        axis_vector_to_filter = (1, 0, 0)
        axis_name = "X-axis"
    elif args.filter_axis == 'y':
        axis_vector_to_filter = (0, 1, 0)
        axis_name = "Y-axis"
    else: # 'z'
        axis_vector_to_filter = (0, 0, 1)
        axis_name = "Z-axis"

    print(f"Filtering triangles with normals aligned (within {args.angle} degrees) with either the positive or negative {axis_name}...")
    initial_count = len(triangles)
    filtered_triangles = filter_axis_facing_triangles(triangles, axis_vector_to_filter, args.angle)
    removed_count = initial_count - len(filtered_triangles)
    
    if initial_count > 0:
        percentage_removed = (removed_count / initial_count) * 100
        print(f"Removed {removed_count} triangles out of {initial_count} ({percentage_removed:.2f}%) whose normals were aligned with either the positive or negative {axis_name}.")
    else:
        print("No triangles to process.")
        
    print(f"Writing filtered STL to {args.output}...")
    
    write_stl_ascii(args.output, solid_name, filtered_triangles)
    print("Done!")

if __name__ == "__main__":
    main()
