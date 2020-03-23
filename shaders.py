import numpy as np


TYPE_DIFFUSE_LIGHT = "diffuse_light"
TYPE_DIFFUSE_COLORS = "diffuse_colors"
TYPE_DIFF_SPECULAR = "diffuse_with_specular"
TYPE_DIFF_SPEC_BORDER = "diffuse_specular_border"
COLOR_FOR_LIGHT = np.array([255, 255, 255], dtype=float)
COLOR_FOR_BORDER = np.array([185, 185, 185], dtype=float)
DEFAULT_KS = 0.8
DEFAULT_THICKNESS = 0.7


def diffuse_light(n, l):
    """
    Shader calculation for a normal and a light vector.
    Args:
        n(numpy.array): Unit normal vector
        l(numpy.array): Unit vector in the direction to the light
    Returns:
        numpy.array: The calculated color (grayscale 0-255)
    """
    diffuse_coef = np.dot(n, l)
    color = np.maximum(0, diffuse_coef)
    return color


def diffuse_colors(n, l, dark, light):
    """
    Shader calculation for a normal and a light vector and light and dark
    colors.
    Args:
        n(numpy.array): Unit normal vector
        l(numpy.array): Unit vector in the direction to the light
        dark(numpy.array): RGB dark color
        light(numpy.array): RGB light color
    Returns:
        numpy.array: The calculated color (RGB)
    """
    # This formula changes the value [-1 - 1] to [0 - 1]
    diffuse_coef = np.dot(n, l)
    t = np.maximum(0, diffuse_coef)
    color = light * t + dark * (1 - t)
    return color


def diffuse_with_specular(n, l, eye, dark, light, ks=DEFAULT_KS):
    """
    Shader calculation for normal and light vectors, dark and light colors and
    specular size ks.
    Args:
        n(numpy.array): Unit normal vector
        l(numpy.array): Unit vector in the direction to the light
        eye(numpy.array): Unit vector in the direction of the viewer
        dark(numpy.array): RGB dark color
        light(numpy.array): RGB light color
        ks(float): size of specularity (this can be changed by the user)
    Returns:
        numpy.array: The calculated color (RGB)
    """
    n_dot_l = np.dot(n, l)
    t = np.maximum(0, n_dot_l)
    color = light * t + dark * (1 - t)
    # --------------- Adding specular
    # Get the reflection of light vector
    r = -1 * l + 2 * n_dot_l * n
    s = np.dot(eye, r)
    s = np.maximum(0, s)
    # try smooth step
    step_min = 0.73
    step_max = 1
    s = (s - step_min) / (step_max - step_min)
    if s < 0:
        s = 0
    elif s > 1:
        s = 1
    s = -2 * (s ** 3) + 3 * (s ** 2)
    color = color * (1 - s * ks) + s * ks * COLOR_FOR_LIGHT
    return color


def diffuse_specular_border(
        n, l, eye, dark, light, ks=DEFAULT_KS, thickness=DEFAULT_THICKNESS
):
    """
    Shader calculation for normal and light vectors, dark and light colors,
    and ks specular size and thickness of border parameters.
    Args:
        n(numpy.array): Unit normal vector
        l(numpy.array): Unit vector in the direction to the light
        eye(numpy.array): Unit vector in the direction of the viewer
        dark(numpy.array): RGB dark color
        light(numpy.array): RGB light color
        ks(float): size of specularity (this can be changed by the user)
        thickness(float): thickness parameter for the border defined by user
    Returns:
        numpy.array: The calculated color (RGB)
    """
    b = np.maximum(0, 1 - np.dot(eye, n))
    step_min = thickness
    step_max = 1
    b = (b - step_min) / (step_max - step_min)
    if b < 0:
        b = 0
    elif b > 1:
        b = 1
    color = diffuse_with_specular(n, l, eye, dark, light, ks)
    color = color * (1 - b) + b * COLOR_FOR_BORDER
    return color
