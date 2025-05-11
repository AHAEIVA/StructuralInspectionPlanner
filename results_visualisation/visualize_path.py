import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection # For STL plotting
import csv
import shutil
import os
import numpy as np # Import numpy for trigonometric functions
from stl import mesh # For loading STL files

# Define paths
source_path_file = '../koptplanner/data/latestPath.csv'
destination_folder = '.'
destination_path_file = os.path.join(destination_folder, 'latestPath.csv')
stl_model_path = '../request/meshes/dfki_pipe.stl' # Path to the STL model

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
                    # Attempt to convert first four elements to float
                    # If any fail, assume it's a header
                    float(row[0])
                    float(row[1])
                    float(row[2])
                    float(row[3]) # Check yaw column
                except (ValueError, IndexError):
                    is_header = True
                
                if is_header:
                    print(f"Skipping header row: {row}")
                    continue
            try:
                # Assuming the first three columns are x, y, z and fourth is yaw
                x_all.append(float(row[0]))
                y_all.append(float(row[1]))
                z_all.append(float(row[2]))
                if len(row) > 3:
                    yaw_all.append(float(row[3]))
                else:
                    yaw_all.append(0.0) # Default yaw if not present
                    if i > 0 : # Don't warn for header if it was short
                         print(f"Warning: Row {i+1} has no yaw data, defaulting to 0.0. Row: {row}")

            except ValueError as e:
                print(f"Skipping row {i+1} due to data conversion error: {row} - {e}")
                continue
            except IndexError as e: # Should be caught by len(row) > 3 check mostly
                print(f"Skipping row {i+1} due to insufficient columns: {row} - {e}")
                yaw_all.append(0.0) # Default yaw if row is too short after passing header check
                continue
    
    if not x_all or not y_all or not z_all:
        print("No valid data points found to read.")
        return

    # Reduce resolution
    x = x_all[::point_reduction_step]
    y = y_all[::point_reduction_step]
    z = z_all[::point_reduction_step]
    yaw = yaw_all[::point_reduction_step]


    if not x or not y or not z:
        print("No valid data points found to plot after reduction.")
        return

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot the path with reduced resolution and transparency
    ax.plot(x, y, z, marker='.', linestyle='-', color='blue', label='Path', alpha=0.5) # Added alpha
    
    # Plot direction arrows (quivers) using yaw
    arrow_length_xy = 0.2 # Shorter arrows for XY plane projection based on yaw
    arrow_length_ratio_val = 0.4 # Adjust arrow head size

    if len(x) > 0: # Use reduced points for quivers
        for i in range(len(x)):
            # Calculate direction vector components from yaw for XY plane
            dx_yaw = np.cos(yaw[i])
            dy_yaw = np.sin(yaw[i])
            
            # For Z component of arrow, use change in Z from next point if available, else small vertical
            if i < len(x) -1:
                dz_path = z[i+1] - z[i] # Z component based on path direction
            else:
                dz_path = 0 # No next point, so arrow is horizontal in Z for the last point

            # Plot quiver using yaw for XY and path dz for Z.
            # If you want arrows to be purely horizontal based on yaw, set dz_path to 0 always.
            ax.quiver(x[i], y[i], z[i],  # Start point
                      dx_yaw, dy_yaw, dz_path,  # Direction vector
                      length=arrow_length_xy, # Control overall length
                      normalize=True, # Normalize the (dx,dy,dz) vector before applying length
                      color='red', 
                      arrow_length_ratio=arrow_length_ratio_val)

    # Label start and end points
    if x:
        ax.scatter(x[0], y[0], z[0], color='green', s=100, label='Start Point', depthshade=False)
        ax.text(x[0], y[0], z[0], 'Start', color='green')
        
        ax.scatter(x[-1], y[-1], z[-1], color='purple', s=100, label='End Point', depthshade=False)
        ax.text(x[-1], y[-1], z[-1], 'End', color='purple')
    
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Z Coordinate')
    ax.set_title('3D Inspection Path with Directions')
    ax.legend()
    
    # Load and plot the STL model
    try:
        if os.path.exists(stl_model_path):
            your_mesh = mesh.Mesh.from_file(stl_model_path)
            # Create a Poly3DCollection from the mesh
            # The mesh.vectors property provides the vertices of each triangle
            poly_collection = Poly3DCollection(your_mesh.vectors, alpha=0.3, facecolor='gray', edgecolor='k', linewidth=0.3)
            ax.add_collection3d(poly_collection)
            print(f"STL model '{stl_model_path}' loaded and added to plot.")
            
            # Get extents of the STL model to adjust plot limits
            stl_min = your_mesh.min_
            stl_max = your_mesh.max_
        else:
            print(f"Warning: STL model not found at {stl_model_path}")
            stl_min = np.array([np.inf]*3)
            stl_max = np.array([-np.inf]*3)
            
    except Exception as e:
        print(f"Error loading or processing STL model: {e}")
        stl_min = np.array([np.inf]*3)
        stl_max = np.array([-np.inf]*3)

    # Set equal aspect ratio considering both path and STL model
    # Combine all coordinates from path and STL for overall range calculation
    
    # Path coordinates
    path_coords_min = np.array([min(x_all) if x_all else np.inf, 
                                min(y_all) if y_all else np.inf, 
                                min(z_all) if z_all else np.inf])
    path_coords_max = np.array([max(x_all) if x_all else -np.inf, 
                                max(y_all) if y_all else -np.inf, 
                                max(z_all) if z_all else -np.inf])

    # Overall min and max including STL
    overall_min = np.minimum(path_coords_min, stl_min)
    overall_max = np.maximum(path_coords_max, stl_max)

    if not np.isinf(overall_min).any() and not np.isinf(overall_max).any():
        mid_x = (overall_max[0] + overall_min[0]) / 2.0
        mid_y = (overall_max[1] + overall_min[1]) / 2.0
        mid_z = (overall_max[2] + overall_min[2]) / 2.0

        plot_range_x = (overall_max[0] - overall_min[0])
        plot_range_y = (overall_max[1] - overall_min[1])
        plot_range_z = (overall_max[2] - overall_min[2])
        
        max_plot_range = max(plot_range_x, plot_range_y, plot_range_z) / 2.0
        max_plot_range = max(max_plot_range, 0.5) # Ensure a minimum range

        ax.set_xlim(mid_x - max_plot_range, mid_x + max_plot_range)
        ax.set_ylim(mid_y - max_plot_range, mid_y + max_plot_range)
        ax.set_zlim(mid_z - max_plot_range, mid_z + max_plot_range)
    else: # Fallback if no valid coordinates
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_zlim(-1, 1)

    plt.show()
    print("Note: If the STL model is not visible or the plot looks incorrect, you might need to install 'numpy-stl': pip install numpy-stl")

if __name__ == '__main__':
    if copy_trajectory_file():
        visualize_path()
