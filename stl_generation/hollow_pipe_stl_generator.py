#!/usr/bin/env python3

import argparse
import numpy as np

def generate_hollow_pipe_stl(diameter, length, output_file):
    """
    Generates an STL file of a hollow horizontal pipe.

    Args:
        diameter (float): The outer diameter of the pipe.
        length (float): The length of the pipe.
        output_file (str): The path to the output STL file.
    """
    inner_diameter = diameter * 0.8  # Example: Inner diameter is 80% of outer diameter
    num_segments = 18  # Number of segments to approximate the circle
    num_length_segments = 5

    vertices = []
    faces = []
    normals = []

    # Generate vertices for the outer circle
    for j in range(num_length_segments + 1):
        z = length * j / num_length_segments
        for i in range(num_segments):
            angle = 2 * np.pi * i / num_segments
            x = diameter / 2 * np.cos(angle)
            y = diameter / 2 * np.sin(angle)
            vertices.append([x, y, z])

    # Generate vertices for the inner circle
    for j in range(num_length_segments + 1):
        z = length * j / num_length_segments
        for i in range(num_segments):
            angle = 2 * np.pi * i / num_segments
            x = inner_diameter / 2 * np.cos(angle)
            y = inner_diameter / 2 * np.sin(angle)
            vertices.append([x, y, z])

    # Generate faces for the outer surface
    num_vertices_per_circle = num_segments
    for j in range(num_length_segments):
        for i in range(num_segments):
            # Indices for the vertices of the quad
            i1 = i + j * num_vertices_per_circle  # First vertex
            i2 = (i + 1) % num_segments + j * num_vertices_per_circle  # Second vertex
            i3 = i + (j + 1) * num_vertices_per_circle  # Third vertex
            i4 = (i + 1) % num_segments + (j + 1) * num_vertices_per_circle  # Fourth vertex

            # Create two triangles for the quad
            faces.append([i1, i3, i2])
            faces.append([i3, i4, i2])

    # Generate faces for the inner surface (reversed normals)
    offset = (num_length_segments + 1) * num_segments
    for j in range(num_length_segments):
        for i in range(num_segments):
            # Indices for the vertices of the quad
            i1 = offset + i + j * num_vertices_per_circle  # First vertex
            i2 = offset + (i + 1) % num_segments + j * num_vertices_per_circle  # Second vertex
            i3 = offset + i + (j + 1) * num_vertices_per_circle  # Third vertex
            i4 = offset + (i + 1) % num_segments + (j + 1) * num_vertices_per_circle  # Fourth vertex

            # Create two triangles for the quad
            faces.append([i2, i3, i1])
            faces.append([i2, i4, i3])

    # Calculate normals
    for face in faces:
        v1 = np.array(vertices[face[0]])
        v2 = np.array(vertices[face[1]])
        v3 = np.array(vertices[face[2]])
        normal = np.cross(v2 - v1, v3 - v1)
        normal = normal / np.linalg.norm(normal)
        normals.append(normal)

    # Write STL file
    with open(output_file, 'w') as f:
        f.write('solid hollow_pipe\n')
        for i, face in enumerate(faces):
            normal = normals[i]
            f.write('  facet normal {} {} {}\n'.format(normal[0], normal[1], normal[2]))
            f.write('    outer loop\n')
            for vertex_index in face:
                vertex = vertices[vertex_index]
                f.write('      vertex {} {} {}\n'.format(vertex[0], vertex[1], vertex[2]))
            f.write('    endloop\n')
            f.write('  endfacet\n')
        f.write('endsolid hollow_pipe\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a hollow pipe STL file.")
    parser.add_argument("diameter", type=float, help="The diameter of the pipe.")
    parser.add_argument("length", type=float, help="The length of the pipe.")
    parser.add_argument("output_file", type=str, help="The path to the output STL file.")
    args = parser.parse_args()

    generate_hollow_pipe_stl(args.diameter, args.length, args.output_file)
