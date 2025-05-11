# Tech Context

## Technologies Used:

*   **Primary Languages:**
    *   C++ (dominant in `koptplanner`, `optec`, `request/src`)
    *   Python (in `stl_generation`, `utils`)
    *   MATLAB (in `request/visualization`, `koptplanner/data/tourlength.m`)
*   **Frameworks/Libraries (Inferred):**
    *   **ROS (Robot Operating System):** Indicated by `catkin_ws_repos`, `package.xml`, `.launch` files, `rviz_sip.rviz`. This is a major architectural component.
    *   **LKH-2.0.7:** A solver for the Traveling Salesperson Problem, included in `koptplanner/include/`.
    *   **Optec:** Appears to be a numerical optimization library, with its own source and examples.
    *   **Eigen (Possibly):** Common for C++ matrix/vector math in robotics; to be confirmed by inspecting C++ code.
    *   **PCL (Point Cloud Library) (Possibly):** Often used with ROS for 3D data processing; to be confirmed.
    *   **NumPy/SciPy (Python):** Likely used in Python scripts for numerical operations.
*   **Build System:**
    *   CMake (`CMakeLists.txt` files present in multiple directories).
    *   Make (`Makefile`, `make_*.mk` files).
*   **Version Control:** Git (assumed, standard practice).
*   **Operating System (Development/Deployment):** Linux (indicated by `make_linux.mk`, `/bin/bash` shell, typical for ROS development). Windows and macOS might also be supported to some extent (`make_windows.mk`, `make_osx.mk`).

## Development Setup (Assumed):

*   A Linux environment with ROS installed.
*   C++ compiler (e.g., GCC).
*   Python 3 interpreter (Python 3.8 identified in the traceback).
*   CMake and Make build tools.
*   MATLAB for running visualization scripts.
*   Standard development tools (text editor/IDE like VS Code).

## Technical Constraints:

*   **Real-time Performance:** Path planning for robotics often has soft or hard real-time constraints, though this depends on whether planning is done online or offline.
*   **Computational Resources:** Algorithms must be efficient enough to run on available hardware (onboard computer for online planning, desktop for offline).
*   **STL File Limitations:** STL files can be large and sometimes contain errors (e.g., non-manifold geometry, incorrect normals). Robust parsing and handling are necessary. Binary STL is more compact but less human-readable than ASCII STL. The current error points to issues handling these formats.
*   **ROS Middleware:** Adherence to ROS message types, topics, services, and nodes if components are to interoperate within a ROS ecosystem.

## Dependencies:

*   **External Libraries:** LKH, Optec (if used as a pre-built library rather than compiled from source within the project).
*   **ROS Packages:** Standard ROS packages (e.g., `roscpp`, `rospy`, `tf`, `sensor_msgs`, `geometry_msgs`) and potentially custom messages/services defined in `koptplanner/srv/inspection.srv`.
*   **System Libraries:** Standard C++ libraries, Python libraries.
