import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from matplotlib.animation import FuncAnimation
from stl import mesh
import csv
import os

# Configuration
trajectory_file = 'latestPath.csv'
stl_model_path = '../request/meshes/dfki_pipe2n.stl'
point_reduction_step = 5  # Reduce points for smoother animation
animation_speed = 20  # Frames per second
marker_size = 20  # Size of the robot marker

def load_trajectory():
    """Load trajectory data from CSV file."""
    x, y, z, yaw = [], [], [], []
    
    if not os.path.exists(trajectory_file):
        raise FileNotFoundError(f"Trajectory file not found at {trajectory_file}")
    
    with open(trajectory_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i == 0:  # Skip header if present
                try:
                    float(row[0])
                    float(row[1])
                    float(row[2])
                except (ValueError, IndexError):
                    continue
            try:
                x.append(float(row[0]))
                y.append(float(row[1]))
                z.append(float(row[2]))
                yaw.append(float(row[3]) if len(row) > 3 else 0.0)
            except (ValueError, IndexError) as e:
                print(f"Skipping row {i+1}: {e}")
                continue
    
    return np.array(x), np.array(y), np.array(z), np.array(yaw)

def load_stl_model():
    """Load STL model if available."""
    stl_mesh = None
    stl_min = np.array([np.inf]*3)
    stl_max = np.array([-np.inf]*3)
    
    if os.path.exists(stl_model_path):
        try:
            stl_mesh = mesh.Mesh.from_file(stl_model_path)
            stl_min = stl_mesh.min_
            stl_max = stl_mesh.max_
        except Exception as e:
            print(f"Error loading STL: {e}")
    
    return stl_mesh, stl_min, stl_max

def setup_plot(stl_mesh=None):
    """Set up the 3D plot with optional STL model."""
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot STL model if available
    if stl_mesh is not None:
        poly_collection = Poly3DCollection(
            stl_mesh.vectors, 
            alpha=0.2, 
            facecolor='lightgray', 
            edgecolor='gray', 
            linewidth=0.3
        )
        ax.add_collection3d(poly_collection)
    
    # Set labels and title
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Z Coordinate')
    ax.set_title('Robot Trajectory Animation')
    
    return fig, ax

def calculate_plot_limits(x, y, z, stl_min, stl_max):
    """Calculate appropriate plot limits."""
    path_min = np.array([np.min(x), np.min(y), np.min(z)])
    path_max = np.array([np.max(x), np.max(y), np.max(z)])
    
    overall_min = np.minimum(path_min, stl_min)
    overall_max = np.maximum(path_max, stl_max)
    
    if not np.isinf(overall_min).any() and not np.isinf(overall_max).any():
        mid = (overall_max + overall_min) / 2.0
        plot_range = np.max(overall_max - overall_min) / 2.0
        plot_range = max(plot_range, 0.5)  # Minimum range
        
        limits = {
            'x': (mid[0] - plot_range, mid[0] + plot_range),
            'y': (mid[1] - plot_range, mid[1] + plot_range),
            'z': (mid[2] - plot_range, mid[2] + plot_range)
        }
    else:
        limits = {
            'x': (-1, 1),
            'y': (-1, 1),
            'z': (-1, 1)
        }
    
    return limits

def animate_trajectory():
    """Create and run the trajectory animation."""
    # Load data
    x, y, z, yaw = load_trajectory()
    stl_mesh, stl_min, stl_max = load_stl_model()
    
    # Reduce points for smoother animation
    x = x[::point_reduction_step]
    y = y[::point_reduction_step]
    z = z[::point_reduction_step]
    yaw = yaw[::point_reduction_step]
    
    # Setup plot
    fig, ax = setup_plot(stl_mesh)
    limits = calculate_plot_limits(x, y, z, stl_min, stl_max)
    
    # Set plot limits
    ax.set_xlim(*limits['x'])
    ax.set_ylim(*limits['y'])
    ax.set_zlim(*limits['z'])
    
    # Initialize robot marker and path line
    robot_marker, = ax.plot([], [], [], 'ro', markersize=marker_size, label='Robot')
    path_line, = ax.plot([], [], [], 'b-', alpha=0.3, linewidth=1, label='Path')
    
    # Add start and end markers
    ax.plot(x[0], y[0], z[0], 'go', markersize=marker_size, label='Start')
    ax.plot(x[-1], y[-1], z[-1], 'mo', markersize=marker_size, label='End')
    
    # Add legend
    ax.legend()
    
    def update(frame):
        """Update function for animation."""
        # Update robot position
        robot_marker.set_data([x[frame]], [y[frame]])
        robot_marker.set_3d_properties([z[frame]])
        
        # Update path line (show path up to current position)
        path_line.set_data(x[:frame+1], y[:frame+1])
        path_line.set_3d_properties(z[:frame+1])
        
        # Add orientation indicator (quiver arrow)
        if frame % 5 == 0:  # Update orientation arrow every 5 frames
            # Remove previous quiver if it exists
            for artist in ax.collections:
                if hasattr(artist, '_quiver_props'):
                    artist.remove()
            
            # Add new quiver
            dx = np.cos(yaw[frame]) * 0.2
            dy = np.sin(yaw[frame]) * 0.2
            dz = 0 if frame == len(x)-1 else (z[frame+1] - z[frame]) * 0.2
            
            ax.quiver(
                x[frame], y[frame], z[frame],
                dx, dy, dz,
                color='red', arrow_length_ratio=0.3,
                length=0.3, normalize=True
            )
        
        return robot_marker, path_line
    
    # Create animation
    ani = FuncAnimation(
        fig, update, frames=len(x),
        interval=1000/animation_speed, blit=False,
        repeat_delay=2000, repeat=True
    )
    
    plt.tight_layout()
    plt.show()
    
    return ani

if __name__ == '__main__':
    try:
        ani = animate_trajectory()
    except Exception as e:
        print(f"Error: {e}")