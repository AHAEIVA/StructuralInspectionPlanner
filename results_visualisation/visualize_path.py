import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import csv
import shutil
import os
import numpy as np
from stl import mesh

# Define paths
source_path_file = '../koptplanner/data/latestPath.csv'
destination_folder = '.'
destination_path_file = os.path.join(destination_folder, 'latestPath.csv')
stl_model_path = '../request/meshes/dfki_pipe2n.stl'

def copy_trajectory_file():
    """Copies the trajectory file to the current directory."""
    try:
        shutil.copy(source_path_file, destination_path_file)
        print(f"Trajectory file copied to {destination_path_file}")
    except FileNotFoundError:
        print(f"Error: Source file not found at {source_path_file}")
        return False
    except Exception as e:
        print(f"Error copying file: {e}")
        return False
    return True

def visualize_path():
    """Reads the trajectory data and visualizes it in 3D."""
    if not os.path.exists(destination_path_file):
        print(f"Error: Trajectory file not found at {destination_path_file}. Please copy it first.")
        return

    x_all, y_all, z_all, yaw_all = [], [], [], []
    point_reduction_step = 5  # Plot every 5th point

    with open(destination_path_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i == 0:  # Skip header row if present
                is_header = False
                try:
                    # Check if first few columns are numeric
                    float(row[0])
                    float(row[1])
                    float(row[2])
                    float(row[5])  # Check yaw column (6th column, index 5)
                except (ValueError, IndexError):
                    is_header = True
                
                if is_header:
                    print(f"Skipping header row: {row}")
                    continue
            
            try:
                x_all.append(float(row[0]))
                y_all.append(float(row[1]))
                z_all.append(float(row[2]))
                if len(row) > 5:  # Yaw is in 6th column (index 5)
                    yaw_all.append(float(row[5]))  # Yaw in radians
                else:
                    yaw_all.append(0.0)
                    if i > 0:
                        print(f"Warning: Row {i+1} has no yaw data, defaulting to 0.0. Row: {row}")
            except (ValueError, IndexError) as e:
                print(f"Skipping row {i+1} due to error: {row} - {e}")
                continue
    
    if not x_all or not y_all or not z_all:
        print("No valid data points found to read.")
        return

    # Reduce resolution
    x = x_all[::point_reduction_step]
    y = y_all[::point_reduction_step]
    z = z_all[::point_reduction_step]
    yaw = yaw_all[::point_reduction_step]

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot the path
    ax.plot(x, y, z, marker='.', linestyle='-', color='blue', label='Path', alpha=0.5)
    
    # Plot direction arrows using yaw angles
    arrow_length = 0.5  # Length of the arrow
    arrow_head_ratio = 0.3  # Size of the arrow head relative to length

    for i in range(len(x)):
        # Calculate direction vector from yaw (in radians)
        dx = np.cos(yaw[i]) * arrow_length
        dy = np.sin(yaw[i]) * arrow_length
        dz = 0  # Assuming yaw is only for XY plane
        
        ax.quiver(x[i], y[i], z[i], 
                  dx, dy, dz,
                  color='red', 
                  arrow_length_ratio=arrow_head_ratio,
                  normalize=False,
                  linewidth=1.5)

    # Label start and end points
    if x:
        ax.scatter(x[0], y[0], z[0], color='green', s=100, label='Start Point')
        ax.text(x[0], y[0], z[0], 'Start', color='green')
        ax.scatter(x[-1], y[-1], z[-1], color='purple', s=100, label='End Point')
        ax.text(x[-1], y[-1], z[-1], 'End', color='purple')
    
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Z Coordinate')
    ax.set_title('3D Inspection Path with Yaw Directions (6th column)')
    ax.legend()
    
    # Load and plot the STL model
    try:
        if os.path.exists(stl_model_path):
            your_mesh = mesh.Mesh.from_file(stl_model_path)
            poly_collection = Poly3DCollection(your_mesh.vectors, alpha=0.3, facecolor='gray', edgecolor='k', linewidth=0.3)
            ax.add_collection3d(poly_collection)
            print(f"STL model '{stl_model_path}' loaded and added to plot.")
            
            stl_min = your_mesh.min_
            stl_max = your_mesh.max_
        else:
            print(f"Warning: STL model not found at {stl_model_path}")
            stl_min = np.array([np.inf]*3)
            stl_max = np.array([-np.inf]*3)
    except Exception as e:
        print(f"Error loading STL model: {e}")
        stl_min = np.array([np.inf]*3)
        stl_max = np.array([-np.inf]*3)

    # Set plot limits
    path_coords_min = np.array([min(x_all), min(y_all), min(z_all)])
    path_coords_max = np.array([max(x_all), max(y_all), max(z_all)])

    overall_min = np.minimum(path_coords_min, stl_min)
    overall_max = np.maximum(path_coords_max, stl_max)

    if not np.isinf(overall_min).any() and not np.isinf(overall_max).any():
        mid_x = (overall_max[0] + overall_min[0]) / 2.0
        mid_y = (overall_max[1] + overall_min[1]) / 2.0
        mid_z = (overall_max[2] + overall_min[2]) / 2.0

        max_range = max(overall_max - overall_min) / 2.0
        max_range = max(max_range, 0.5)

        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)
    else:
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_zlim(-1, 1)

    plt.show()

if __name__ == '__main__':
    if copy_trajectory_file():
        visualize_path()