import numpy as np
from scipy.spatial import distance
from copy import deepcopy, copy
import itertools as it


def generate_points(n_points, radius, circle_centre=[0.0, 0.0]):
    h, k = circle_centre
    angles = np.random.uniform(0, 2 * np.pi, n_points)  # Random angles
    r = np.sqrt(np.random.uniform(0, 1, n_points)) * radius  # Random radius with correct distribution
    x = r * np.cos(angles) + h
    y = r * np.sin(angles) + k
    return np.column_stack((x, y))  # Return as Nx2 array


def fill_stuff(key, value, amount):
    if key == "noise":
        return np.random.uniform(0.0, 360.0, amount)
    else:
        return np.repeat(value, amount)


def move_points(radius, points, angles, distances, circle_centre=[0.0, 0.0]):
    # Convert angle to radians
    angles += 0.0001
    angles_rad = np.radians(angles)
    
    # Calculate the movement vector components
    dxs = distances * np.cos(angles_rad)
    dys = distances * np.sin(angles_rad)

    # Create a movement vector for all points
    displacement_vectors = np.array([dxs, dys]).T

    # Displace the points
    displaced_points = points + displacement_vectors

    displaced_points = np.vstack([outside_circle_displacement(radius, points[i], displaced_points[i]) for i in range(points.shape[0])])
    
    return displaced_points

def inside_circle(radius, points, circle_centre=[0.0, 0.0]):
    points = np.array(points)
    h, k = circle_centre
    x, y = np.hsplit(points, 2)
    
    # Calculate the squared distance from the point to the circle center
    dist_squared = (x - h) ** 2 + (y - k) ** 2
    radius_squared = radius ** 2

    # Check if the point is inside or on the circle
    result = dist_squared <= radius_squared
    return result.flatten()

def circle_line_intersection(radius, point1, point2, circle_centre=[0.0, 0.0]):
    h, k = circle_centre
    x1, y1 = point1
    x2, y2 = point2

    # Calculate slope (m) and intercept (b) of the line
    if x2 - x1 == 0:  # vertical line case
        return []  # A vertical line will not intersect unless it's also at the circle's horizontal level

    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1

    # Coefficients of the quadratic equation Ax^2 + Bx + C = 0
    A = 1 + m**2
    B = 2 * (m * (b - k) - h)
    C = (h**2 + (b - k)**2 - radius**2)

    # Calculate the discriminant
    D = B**2 - 4 * A * C

    intersection_points = []

    if D >= 0:  # There are intersections
        # Two possible intersection points if D > 0, one if D = 0
        sqrt_D = np.sqrt(D)

        # Compute both x-coordinates
        x_intersect1 = (-B + sqrt_D) / (2 * A)
        y_intersect1 = m * x_intersect1 + b
        intersection_points.append((x_intersect1, y_intersect1))

        if D > 0:  # Only compute the second intersection point if D > 0
            x_intersect2 = (-B - sqrt_D) / (2 * A)
            y_intersect2 = m * x_intersect2 + b
            intersection_points.append((x_intersect2, y_intersect2))

    return np.array(intersection_points).astype(np.double)


def vector_points(point1, point2):
    x1, y1 = point1
    x2, y2 = point2

    # Calculate the vector components
    dx = x2 - x1
    dy = y2 - y1

    return np.array([dx, dy]).astype(np.double)


def outside_circle_displacement(radius, point_1, point_2, circle_centre=[0.0, 0.0]):
    point_2_outside = ~inside_circle(radius, point_2)
    if point_2_outside:
        cli_array = circle_line_intersection(radius, point_1, point_2)
        cli = np.split(cli_array, 2, axis=0)
        cli = [i.flatten() for i in cli]
        cli_distance = [distance.euclidean(i, point_2) for i in cli]
        new_orig = cli[np.argmax(cli_distance)]
        left_disp_orig = cli[np.argmin(cli_distance)]
        left_disp_vec = vector_points(left_disp_orig, point_2)
        point_3 = new_orig + left_disp_vec
        return point_3
    else:
        return point_2


def generate_trial(n_points, radius, dot_life, n_frames, settings, dot_lifes=None):
    points = generate_points(n_points, radius)
    if not isinstance(dot_lifes, np.ndarray):
        dot_lifes = np.random.randint(dot_life, size=n_points)
    dots_per_cond = [int(n_points * settings[k][0]) for k in settings.keys()]
    dots_per_cond[-1] = n_points - sum(dots_per_cond[:-1])
    dots_per_cond = {k: dots_per_cond[i] for i, k in enumerate(settings.keys())}
    angles = np.hstack([fill_stuff(k, settings[k][1], dots_per_cond[k]) for k in settings.keys()])
    distances = np.hstack([fill_stuff("", settings[k][2], dots_per_cond[k]) for k in settings.keys()])
    copy_points = copy(points)
    positions = []
    for i in range(n_frames):
        dot_lifes += 1
        dot_life_map = dot_lifes >= dot_life
        dot_lifes[dot_life_map] = 0
        copy_points = move_points(radius, copy_points, angles, distances)
        copy_points[dot_life_map] = generate_points(np.sum(dot_life_map), radius)
        positions.append(copy_points)
    return np.array(positions)


def consecutive(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)


def shuffle_array(array, n_row=3):
    while True:
        np.random.shuffle(array)

