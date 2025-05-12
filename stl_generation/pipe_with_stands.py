#!/usr/bin/env python3

import argparse
import numpy as np

def generate_hollow_pipe_with_stands(diameter, length, stand_height, stand_gap, output_file, stand_thickness=None):
    """
    Generates an STL file of a hollow horizontal pipe with supporting stands at both ends.

    Args:
        diameter (float): The outer diameter of the pipe.
        length (float): The length of the pipe.
        stand_height (float): The height of the supporting plates below the pipe.
        stand_gap (float): The distance between the pipe and the stands.
        output_file (str): The path to the output STL file.
        stand_thickness (float, optional): The thickness of the supporting stands. 
                                          If None, defaults to 20% of stand_height.
    """
    inner_diameter = diameter * 0.8  # Inner diameter is 80% of outer diameter
    num_segments = 36  # Increased for better quality
    num_length_segments = max(5, int(length / diameter * 10))  # Adaptive based on length
    
    # Set default stand thickness if not provided
    if stand_thickness is None:
        stand_thickness = stand_height * 0.2
    
    vertices = []
    faces = []
    normals = []

    # Generate vertices for the outer circle of the pipe
    for j in range(num_length_segments + 1):
        z = length * j / num_length_segments
        for i in range(num_segments):
            angle = 2 * np.pi * i / num_segments
            x = diameter / 2 * np.cos(angle)
            y = diameter / 2 * np.sin(angle)
            vertices.append([x, y, z])

    # Generate vertices for the inner circle of the pipe
    for j in range(num_length_segments + 1):
        z = length * j / num_length_segments
        for i in range(num_segments):
            angle = 2 * np.pi * i / num_segments
            x = inner_diameter / 2 * np.cos(angle)
            y = inner_diameter / 2 * np.sin(angle)
            vertices.append([x, y, z])

    # Calculate the base index for later use
    base_pipe_vertices = len(vertices)

    # Generate faces for the outer surface of the pipe
    num_vertices_per_circle = num_segments
    for j in range(num_length_segments):
        for i in range(num_segments):
            i1 = i + j * num_vertices_per_circle
            i2 = (i + 1) % num_segments + j * num_vertices_per_circle
            i3 = i + (j + 1) * num_vertices_per_circle
            i4 = (i + 1) % num_segments + (j + 1) * num_vertices_per_circle

            faces.append([i1, i3, i2])
            faces.append([i3, i4, i2])

    # Generate faces for the inner surface of the pipe (reversed normals)
    offset = (num_length_segments + 1) * num_segments
    for j in range(num_length_segments):
        for i in range(num_segments):
            i1 = offset + i + j * num_vertices_per_circle
            i2 = offset + (i + 1) % num_segments + j * num_vertices_per_circle
            i3 = offset + i + (j + 1) * num_vertices_per_circle
            i4 = offset + (i + 1) % num_segments + (j + 1) * num_vertices_per_circle

            faces.append([i2, i3, i1])
            faces.append([i2, i4, i3])

    # ----- Add supporting stands -----
    
    # Stand parameters
    stand_width = diameter * 0.6  # Width of the stand base
    stand_base_length = diameter * 0.8  # Length along pipe axis
    
    # Front stand (at z=0)
    front_stand_start = len(vertices)
    
    # Bottom vertices of front stand (shifted down by stand_gap)
    y_offset = -diameter/2 - stand_gap - stand_height
    vertices.append([-stand_width/2, y_offset, -stand_thickness/2])  # 0: front-left-bottom
    vertices.append([stand_width/2, y_offset, -stand_thickness/2])   # 1: front-right-bottom
    vertices.append([stand_width/2, y_offset, stand_thickness/2])    # 2: back-right-bottom
    vertices.append([-stand_width/2, y_offset, stand_thickness/2])   # 3: back-left-bottom
    
    # Top vertices of front stand (connecting to pipe)
    top_y = -diameter/2 - stand_gap
    vertices.append([-stand_width/2, top_y, -stand_thickness/2])     # 4: front-left-top
    vertices.append([stand_width/2, top_y, -stand_thickness/2])      # 5: front-right-top
    vertices.append([stand_width/2, top_y, stand_thickness/2])       # 6: back-right-top
    vertices.append([-stand_width/2, top_y, stand_thickness/2])      # 7: back-left-top
    
    # Connection to pipe vertices (front)
    pipe_connection_start = len(vertices)
    for i in range(num_segments):
        angle = 2 * np.pi * i / num_segments
        if np.sin(angle) < -0.5:  # Only bottom part of pipe
            x = diameter / 2 * np.cos(angle)
            y = diameter / 2 * np.sin(angle)
            vertices.append([x, y, -stand_thickness/2])  # front
            vertices.append([x, y, stand_thickness/2])   # back

    # Create faces for front stand
    # Bottom face
    faces.append([front_stand_start, front_stand_start+1, front_stand_start+2])
    faces.append([front_stand_start, front_stand_start+2, front_stand_start+3])
    
    # Top face
    faces.append([front_stand_start+7, front_stand_start+6, front_stand_start+5])
    faces.append([front_stand_start+7, front_stand_start+5, front_stand_start+4])
    
    # Front face
    faces.append([front_stand_start, front_stand_start+4, front_stand_start+5])
    faces.append([front_stand_start, front_stand_start+5, front_stand_start+1])
    
    # Back face
    faces.append([front_stand_start+3, front_stand_start+2, front_stand_start+6])
    faces.append([front_stand_start+3, front_stand_start+6, front_stand_start+7])
    
    # Left face
    faces.append([front_stand_start, front_stand_start+3, front_stand_start+7])
    faces.append([front_stand_start, front_stand_start+7, front_stand_start+4])
    
    # Right face
    faces.append([front_stand_start+1, front_stand_start+5, front_stand_start+6])
    faces.append([front_stand_start+1, front_stand_start+6, front_stand_start+2])
    
    # Connect stand to pipe
    pipe_bottom_indices = [i for i in range(num_segments) if np.sin(2*np.pi*i/num_segments) < -0.5]
    for i in range(len(pipe_bottom_indices)):
        pipe_front = pipe_bottom_indices[i]
        pipe_back = offset + pipe_bottom_indices[i]
        
        # Front connection
        if i < len(pipe_bottom_indices)-1:
            next_pipe_front = pipe_bottom_indices[i+1]
        else:
            next_pipe_front = pipe_bottom_indices[0]
        
        stand_vertex_front = pipe_connection_start + 2*i
        stand_vertex_back = pipe_connection_start + 2*i + 1
        
        faces.append([pipe_front, stand_vertex_front, next_pipe_front])
        faces.append([pipe_back, next_pipe_front, stand_vertex_back])
        
        # Connect to stand top
        if i == 0:
            faces.append([stand_vertex_front, front_stand_start+4, next_pipe_front])
            faces.append([stand_vertex_back, next_pipe_front, front_stand_start+7])
        elif i == len(pipe_bottom_indices)-1:
            faces.append([stand_vertex_front, next_pipe_front, front_stand_start+5])
            faces.append([stand_vertex_back, front_stand_start+6, next_pipe_front])

    # Back stand (at z=length)
    back_stand_start = len(vertices)
    
    # Bottom vertices of back stand
    vertices.append([-stand_width/2, y_offset, length-stand_thickness/2])  # 0: front-left-bottom
    vertices.append([stand_width/2, y_offset, length-stand_thickness/2])  # 1: front-right-bottom
    vertices.append([stand_width/2, y_offset, length+stand_thickness/2])  # 2: back-right-bottom
    vertices.append([-stand_width/2, y_offset, length+stand_thickness/2]) # 3: back-left-bottom
    
    # Top vertices of back stand
    vertices.append([-stand_width/2, top_y, length-stand_thickness/2])    # 4: front-left-top
    vertices.append([stand_width/2, top_y, length-stand_thickness/2])     # 5: front-right-top
    vertices.append([stand_width/2, top_y, length+stand_thickness/2])     # 6: back-right-top
    vertices.append([-stand_width/2, top_y, length+stand_thickness/2])    # 7: back-left-top
    
    # Connection to pipe vertices (back)
    pipe_connection_start_back = len(vertices)
    for i in range(num_segments):
        angle = 2 * np.pi * i / num_segments
        if np.sin(angle) < -0.5:  # Only bottom part of pipe
            x = diameter / 2 * np.cos(angle)
            y = diameter / 2 * np.sin(angle)
            vertices.append([x, y, length-stand_thickness/2])  # front
            vertices.append([x, y, length+stand_thickness/2])    # back

    # Create faces for back stand (similar to front stand but mirrored in z)
    # Bottom face
    faces.append([back_stand_start+2, back_stand_start+1, back_stand_start])
    faces.append([back_stand_start+3, back_stand_start+2, back_stand_start])
    
    # Top face
    faces.append([back_stand_start+4, back_stand_start+5, back_stand_start+6])
    faces.append([back_stand_start+4, back_stand_start+6, back_stand_start+7])
    
    # Front face
    faces.append([back_stand_start+1, back_stand_start+5, back_stand_start+4])
    faces.append([back_stand_start+1, back_stand_start+4, back_stand_start])
    
    # Back face
    faces.append([back_stand_start+6, back_stand_start+2, back_stand_start+3])
    faces.append([back_stand_start+7, back_stand_start+6, back_stand_start+3])
    
    # Left face
    faces.append([back_stand_start+7, back_stand_start+3, back_stand_start])
    faces.append([back_stand_start+4, back_stand_start+7, back_stand_start])
    
    # Right face
    faces.append([back_stand_start+6, back_stand_start+5, back_stand_start+1])
    faces.append([back_stand_start+2, back_stand_start+6, back_stand_start+1])
    
    # Connect back stand to pipe
    for i in range(len(pipe_bottom_indices)):
        pipe_front = pipe_bottom_indices[i] + num_segments * num_length_segments
        pipe_back = offset + pipe_bottom_indices[i] + num_segments * num_length_segments
        
        if i < len(pipe_bottom_indices)-1:
            next_pipe_front = pipe_bottom_indices[i+1] + num_segments * num_length_segments
        else:
            next_pipe_front = pipe_bottom_indices[0] + num_segments * num_length_segments
        
        stand_vertex_front = pipe_connection_start_back + 2*i
        stand_vertex_back = pipe_connection_start_back + 2*i + 1
        
        faces.append([next_pipe_front, stand_vertex_front, pipe_front])
        faces.append([stand_vertex_back, next_pipe_front, pipe_back])
        
        # Connect to stand top
        if i == 0:
            faces.append([next_pipe_front, back_stand_start+4, stand_vertex_front])
            faces.append([next_pipe_front, stand_vertex_back, back_stand_start+7])
        elif i == len(pipe_bottom_indices)-1:
            faces.append([next_pipe_front, stand_vertex_front, back_stand_start+5])
            faces.append([back_stand_start+6, stand_vertex_back, next_pipe_front])

    # Calculate normals for each face
    for face in faces:
        v1 = np.array(vertices[face[0]])
        v2 = np.array(vertices[face[1]])
        v3 = np.array(vertices[face[2]])
        normal = np.cross(v2 - v1, v3 - v1)
        normal = normal / np.linalg.norm(normal)
        normals.append(normal)

    # Write STL file
    with open(output_file, 'w') as f:
        f.write('solid hollow_pipe_with_stands\n')
        for i, face in enumerate(faces):
            normal = normals[i]
            f.write('  facet normal {} {} {}\n'.format(normal[0], normal[1], normal[2]))
            f.write('    outer loop\n')
            for vertex_index in face:
                vertex = vertices[vertex_index]
                f.write('      vertex {} {} {}\n'.format(vertex[0], vertex[1], vertex[2]))
            f.write('    endloop\n')
            f.write('  endfacet\n')
        f.write('endsolid hollow_pipe_with_stands\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a hollow pipe STL file with supporting stands.")
    parser.add_argument("diameter", type=float, help="The outer diameter of the pipe.")
    parser.add_argument("length", type=float, help="The length of the pipe.")
    parser.add_argument("stand_height", type=float, help="The height of the supporting stands below the pipe.")
    parser.add_argument("stand_gap", type=float, help="The distance between the pipe and the stands.")
    parser.add_argument("output_file", type=str, help="The path to the output STL file.")
    parser.add_argument("--stand_thickness", type=float, default=None, 
                       help="The thickness of the supporting stands. Defaults to 20%% of stand_height.")
    
    args = parser.parse_args()

    generate_hollow_pipe_with_stands(
        args.diameter, 
        args.length, 
        args.stand_height, 
        args.stand_gap, 
        args.output_file,
        args.stand_thickness
    )