import numpy as np
from scipy.spatial import Delaunay
import meshio
import pyvista as pv

# Define the dimensions of the board
length =10 # Length of each side
width = 10   # Width of the board
num_points_per_side = 10  # Number of points per side for the regular part

# Generate regular points on the regular part of the board
x = np.linspace(0, length, num_points_per_side)
y = np.linspace(0, width, num_points_per_side)
regular_points = np.array([(xi, yi, 0) for xi in x for yi in y])

# Generate random elevation for the irregular top face
num_irregular_points = 10  # Adjust as needed
irregular_points = np.random.rand(num_irregular_points, 3) * length
irregular_points[:, 2] = np.random.rand(num_irregular_points) * 0.2  # Add irregularity to the Z-coordinate

# Combine regular and irregular points
points = np.vstack((regular_points, irregular_points))

# Combine regular and irregular points
points = np.vstack((regular_points, irregular_points))
# Perform 3D Delaunay triangulation
tri = Delaunay(points)

# Extract the vertices and tetrahedra
vertices = points
tetrahedra = tri.simplices

# Extract the triangular facets from the tetrahedra
triangles = []
for tetra in tetrahedra:
    tetra_facets = [
        (tetra[0], tetra[1], tetra[2]),
        (tetra[0], tetra[1], tetra[3]),
        (tetra[0], tetra[2], tetra[3]),
        (tetra[1], tetra[2], tetra[3]),
    ]
    triangles.extend(tetra_facets)

# Create a meshio mesh object
mesh = meshio.Mesh(vertices, {"triangle": np.array(triangles)})

# Save the mesh to a file (replace 'output_mesh.obj' with your desired file format)
meshio.write("output_mesh.obj", mesh)

# Visualize the mesh (optional)
plotter = pv.Plotter()
plotter.add_mesh(mesh, color="lightblue")
plotter.show()

def get_z_coordinate(mesh, x, y):
    # Find the tetrahedron containing the (x, y) point
    tetrahedron_index = None
    for i, cell_type in enumerate(mesh.cells):
        print('hellp')
        if cell_type.type == "triangle":
            tetrahedron = mesh.cells[i].data
            vertices = mesh.points[tetrahedron]
            print(tetrahedron)
            
            # Calculate the barycentric coordinates
            detT = (vertices[1, 0] - vertices[0, 0]) * (vertices[2, 1] - vertices[0, 1]) - (vertices[2, 0] - vertices[0, 0]) * (vertices[1, 1] - vertices[0, 1])
            alpha = ((vertices[2, 1] - vertices[0, 1]) * (x - vertices[0, 0]) - (vertices[2, 0] - vertices[0, 0]) * (y - vertices[0, 1])) / detT
            beta = ((vertices[0, 1] - vertices[1, 1]) * (x - vertices[0, 0]) - (vertices[0, 0] - vertices[1, 0]) * (y - vertices[0, 1])) / detT
            gamma = 1 - alpha - beta
            # print(detT)
            # print(alpha)
            # print(beta)
            # print(gamma)

            # Check if the point is inside the triangle
            if all(0 <= alpha) and all(alpha <= 1) and all(0 <= beta) and all(beta <= 1) and all(0 <= gamma) and all(gamma <= 1):
                # Calculate the Z-coordinate
                z = alpha * vertices[0, 2] + beta * vertices[1, 2] + gamma * vertices[2, 2]
                return z
        else:
            print(cell_type)
    # Handle the case where the point is not found within the tetrahedron
    return None

# Example usage:
# z = get_z_coordinate(mesh, x, y)

import meshio

def find_mesh_x_y_range(mesh):
    # Initialize min and max values for x and y
    min_x, max_x, min_y, max_y = float("inf"), -float("inf"), float("inf"), -float("inf")

    # Iterate through mesh points to find the range
    for point in mesh.points:
        x, y, _ = point  # Assuming the point is in (x, y, z) format

        # Update min and max values for x and y
        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)

    return (min_x, max_x), (min_y, max_y)

# Example usage:
# x_range, y_range = find_mesh_x_y_range(mesh)
# x_min, x_max = x_range
# y_min, y_max = y_range


# Loop through all the vertices in the mesh
def get_z(mesh,target_x,target_y):
    # Initialize a variable to store the maximum Z value
    max_z = float("-inf")
    for point_idx, point in enumerate(mesh.points):
        x, y, z = point  # Extract (X, Y, Z) coordinates of the current vertex

        # Check if the (X, Y) coordinates match the target point
        if x == target_x and y == target_y:
            # Update the maximum Z value if the current Z value is greater
            max_z = max(max_z, z)

    # Check if a valid maximum Z value was found
    if max_z != float("-inf"):
        print(f"Maximum Z value for ({target_x}, {target_y}): {max_z}")
    else:
        print(f"No matching point found for ({target_x}, {target_y}) in the mesh.")

def aprox_z(mesh,target_x,target_y):
    # Extract the vertex coordinates and Z values from the mesh data
    vertices = mesh.points
    z_values = vertices[:, 2]  # Assuming Z coordinates are in the third column

    # Find the nearest vertices to the target point (X, Y)
    distances = np.sqrt((vertices[:, 0] - target_x)**2 + (vertices[:, 1] - target_y)**2)
    nearest_vertex_indices = np.argsort(distances)[:2]  # Find the indices of the two nearest vertices

    # Extract the Z values of the nearest vertices
    z_nearest = z_values[nearest_vertex_indices]

    # Perform linear interpolation to approximate the Z value at the target point
    x0, y0 = vertices[nearest_vertex_indices[0]][:2]
    x1, y1 = vertices[nearest_vertex_indices[1]][:2]
    z0, z1 = z_nearest
    
    print(x0)
    print(x1)
    print(x1-x0)
    print(y0)
    print(y1)
    print(y1-y0)

    if x0 == x1 and y0 == y1:
        # Handle the case where the target point coincides with a vertex
        approximated_z = z0
    else:
        # Perform linear interpolation
        t = (target_x - x0) / (x1 - x0)
        approximated_z = z0 + t * (z1 - z0)

    print(f"Approximated Z value at ({target_x}, {target_y}): {approximated_z}")
