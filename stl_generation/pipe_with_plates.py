#!/usr/bin/env python3

import argparse
import numpy as np

def generate_hollow_pipe_stl(diameter, length, output_file):
    """
    Generates an STL file of a hollow horizontal pipe with thick end plates.

    Args:
        diameter (float): The outer diameter of the pipe.
        length (float): The length of the pipe.
        output_file (str): The path to the output STL file.
    """
    inner_diameter = diameter * 0.8  # Inner diameter is 80% of outer diameter
    num_segments = 18  # Number of segments to approximate the circle
    num_length_segments = 5 # Number of segments along the length of the pipe body
    
    # --- IMPORTANT: For debugging, try a much larger thickness first ---
    # plate_thickness = diameter * 0.05  # Original thickness
    plate_thickness = diameter * 0.25 # TRY THIS: Significantly thicker plate for visibility

    vertices = []
    faces = []

    # --- Vertex Generation ---

    # 1. Generate vertices for the outer pipe wall (from z=0 to z=length)
    for j in range(num_length_segments + 1):
        z = length * j / num_length_segments
        for i in range(num_segments):
            angle = 2 * np.pi * i / num_segments
            x = diameter / 2 * np.cos(angle)
            y = diameter / 2 * np.sin(angle)
            vertices.append([x, y, z])

    inner_vertex_start_offset = len(vertices) 

    # 2. Generate vertices for the inner pipe wall (from z=0 to z=length)
    for j in range(num_length_segments + 1):
        z = length * j / num_length_segments
        for i in range(num_segments):
            angle = 2 * np.pi * i / num_segments
            x = inner_diameter / 2 * np.cos(angle)
            y = inner_diameter / 2 * np.sin(angle)
            vertices.append([x, y, z])

    # 3. Generate vertices for the "back" face of the START plate
    start_plate_back_outer_verts_idx = len(vertices)
    for i in range(num_segments):
        angle = 2 * np.pi * i / num_segments
        x = diameter / 2 * np.cos(angle)
        y = diameter / 2 * np.sin(angle)
        vertices.append([x, y, -plate_thickness])

    start_plate_back_inner_verts_idx = len(vertices)
    for i in range(num_segments):
        angle = 2 * np.pi * i / num_segments
        x = inner_diameter / 2 * np.cos(angle)
        y = inner_diameter / 2 * np.sin(angle)
        vertices.append([x, y, -plate_thickness])

    # 4. Generate vertices for the "back" face of the END plate
    end_plate_back_outer_verts_idx = len(vertices)
    for i in range(num_segments):
        angle = 2 * np.pi * i / num_segments
        x = diameter / 2 * np.cos(angle)
        y = diameter / 2 * np.sin(angle)
        vertices.append([x, y, length + plate_thickness])

    end_plate_back_inner_verts_idx = len(vertices)
    for i in range(num_segments):
        angle = 2 * np.pi * i / num_segments
        x = inner_diameter / 2 * np.cos(angle)
        y = inner_diameter / 2 * np.sin(angle)
        vertices.append([x, y, length + plate_thickness])

    # --- Face Generation ---

    # A. Outer pipe surface
    num_vertices_per_circle = num_segments
    for j in range(num_length_segments):
        for i in range(num_segments):
            i1 = i + j * num_vertices_per_circle
            i2 = (i + 1) % num_segments + j * num_vertices_per_circle
            i3 = i + (j + 1) * num_vertices_per_circle
            i4 = (i + 1) % num_segments + (j + 1) * num_vertices_per_circle
            faces.append([i1, i3, i2])
            faces.append([i3, i4, i2])

    # B. Inner pipe surface
    for j in range(num_length_segments):
        for i in range(num_segments):
            idx1_inner = inner_vertex_start_offset + i + j * num_vertices_per_circle
            idx2_inner = inner_vertex_start_offset + (i + 1) % num_segments + j * num_vertices_per_circle
            idx3_inner = inner_vertex_start_offset + i + (j + 1) * num_vertices_per_circle
            idx4_inner = inner_vertex_start_offset + (i + 1) % num_segments + (j + 1) * num_vertices_per_circle
            faces.append([idx2_inner, idx3_inner, idx1_inner])
            faces.append([idx2_inner, idx4_inner, idx3_inner])

    # C. THICK START PLATE
    for i in range(num_segments):
        idx_o_curr_z0 = i
        idx_o_next_z0 = (i + 1) % num_segments
        idx_i_curr_z0 = inner_vertex_start_offset + i
        idx_i_next_z0 = inner_vertex_start_offset + (i + 1) % num_segments

        idx_bo_curr = start_plate_back_outer_verts_idx + i
        idx_bo_next = start_plate_back_outer_verts_idx + (i + 1) % num_segments
        idx_bi_curr = start_plate_back_inner_verts_idx + i
        idx_bi_next = start_plate_back_inner_verts_idx + (i + 1) % num_segments

        faces.append([idx_o_curr_z0, idx_i_curr_z0, idx_i_next_z0])
        faces.append([idx_o_curr_z0, idx_i_next_z0, idx_o_next_z0])
        faces.append([idx_bo_curr, idx_bi_next, idx_bi_curr])
        faces.append([idx_bo_curr, idx_bo_next, idx_bi_next])
        faces.append([idx_o_curr_z0, idx_bo_curr, idx_bo_next])
        faces.append([idx_o_curr_z0, idx_bo_next, idx_o_next_z0])
        faces.append([idx_i_curr_z0, idx_bi_next, idx_bi_curr])
        faces.append([idx_i_curr_z0, idx_i_next_z0, idx_bi_next])

    # D. THICK END PLATE
    front_plate_outer_start_idx_zL = num_length_segments * num_vertices_per_circle
    front_plate_inner_start_idx_zL = inner_vertex_start_offset + (num_length_segments * num_vertices_per_circle)

    for i in range(num_segments):
        idx_o_curr_zL = front_plate_outer_start_idx_zL + i
        idx_o_next_zL = front_plate_outer_start_idx_zL + (i + 1) % num_segments
        idx_i_curr_zL = front_plate_inner_start_idx_zL + i
        idx_i_next_zL = front_plate_inner_start_idx_zL + (i + 1) % num_segments

        idx_ebo_curr = end_plate_back_outer_verts_idx + i
        idx_ebo_next = end_plate_back_outer_verts_idx + (i + 1) % num_segments
        idx_ebi_curr = end_plate_back_inner_verts_idx + i
        idx_ebi_next = end_plate_back_inner_verts_idx + (i + 1) % num_segments

        faces.append([idx_o_curr_zL, idx_i_next_zL, idx_i_curr_zL])
        faces.append([idx_o_curr_zL, idx_o_next_zL, idx_i_next_zL])
        faces.append([idx_ebo_curr, idx_ebi_curr, idx_ebi_next])
        faces.append([idx_ebo_curr, idx_ebi_next, idx_ebo_next])
        faces.append([idx_o_curr_zL, idx_ebo_curr, idx_ebo_next])
        faces.append([idx_o_curr_zL, idx_ebo_next, idx_o_next_zL])
        faces.append([idx_i_curr_zL, idx_ebi_next, idx_ebi_curr])
        faces.append([idx_i_curr_zL, idx_i_next_zL, idx_ebi_next])

    # --- Calculate normals and Write STL file ---
    calculated_normals = [] 
    for face_v_indices in faces:
        v1 = np.array(vertices[face_v_indices[0]])
        v2 = np.array(vertices[face_v_indices[1]])
        v3 = np.array(vertices[face_v_indices[2]])
        
        normal_vec = np.cross(v2 - v1, v3 - v1)
        norm_magnitude = np.linalg.norm(normal_vec)
        
        if norm_magnitude < 1e-9: # Check for very small magnitude
            # print(f"Warning: Degenerate triangle with indices {face_v_indices}. Vertices: {v1}, {v2}, {v3}. Using fallback normal.")
            unit_normal = np.array([0.0, 0.0, 1.0]) 
        else:
            unit_normal = normal_vec / norm_magnitude
        calculated_normals.append(unit_normal)

    with open(output_file, 'w') as f:
        f.write('solid hollow_pipe_thick_ends\n')
        for i, face_v_indices in enumerate(faces):
            normal_output = calculated_normals[i]
            f.write('  facet normal {:.6e} {:.6e} {:.6e}\n'.format(normal_output[0], normal_output[1], normal_output[2]))
            f.write('    outer loop\n')
            for vertex_index in face_v_indices:
                vertex = vertices[vertex_index]
                f.write('      vertex {:.6e} {:.6e} {:.6e}\n'.format(vertex[0], vertex[1], vertex[2]))
            f.write('    endloop\n')
            f.write('  endfacet\n')
        f.write('endsolid hollow_pipe_thick_ends\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a hollow pipe STL file with thick end plates.")
    parser.add_argument("diameter", type=float, help="The outer diameter of the pipe.")
    parser.add_argument("length", type=float, help="The length of the pipe.")
    parser.add_argument("output_file", type=str, help="The path to the output STL file.")
    args = parser.parse_args()

    generate_hollow_pipe_stl(args.diameter, args.length, args.output_file)