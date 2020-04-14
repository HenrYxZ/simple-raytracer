import numpy as np
# Local Modules
from object import Plane, Sphere, Tetrahedron, Triangle


class Ray:
    """
    Ray object that is used for raytracing. It has an intersect function to get
    the intersection of the ray and a given object.

    Attr:
        pr: Origin point of the Ray
        nr: Director vector for the ray
    """

    def __init__(self, pr, nr):
        self.pr = pr
        self.nr = nr

    def at(self, t):
        """
        Get the point in the ray at position t.

        Args:
            t(float): The scalar that multiplies the director vector in the ray

        Returns:
            np.array: The point in 3D that represent the ray at position t
        """
        return self.pr + t * self.nr

    def intersect_plane(self, plane):
        # Dot product of ray director and plane normal,
        # if zero no intersection
        dot_normals = np.dot(self.nr, plane.n)
        if dot_normals == 0:
            if np.dot((plane.position - self.pr), plane.n) == 0:
                return 0
            else:
                return -1
        t = np.dot((plane.position - self.pr), plane.n) / dot_normals
        if t < 0:
            return -1
        return t

    def intersect_sphere(self, sphere):
        """
        Find t of intersection to a sphere, -1 means no intersection
        """
        # Sphere center point
        pc = sphere.position
        dif = self.pr - pc
        b = np.dot(self.nr, dif)
        c = np.dot(dif, dif) - sphere.radius ** 2
        discriminant = b ** 2 - c
        if b > 0 or discriminant < 0:
            return -1
        t = -1 * b - np.sqrt(discriminant)
        return t

    def intersect_triangle(self, triangle):
        ray_t = self.intersect_plane(triangle)
        p_in_plane = self.at(ray_t)
        s, t = triangle.get_barycentric_coord(p_in_plane)
        if not 0 <= s <= 1 or not 0 <= t <= 1 or not 0 <= s + t <= 1:
            return -1
        return ray_t

    def intersect_tetrahedron(self, tetrahedron):
        triangles = tetrahedron.get_triangles()
        min_t = np.inf
        for tr in triangles:
            t = self.intersect_triangle(tr)
            if 0 < t < min_t:
                min_t = t
        if min_t == np.inf:
            return -1
        return min_t

    def intersect(self, obj):
        """
        Find t of intersection, -1 value means no intersection.
        """
        if isinstance(obj, Sphere):
            return self.intersect_sphere(obj)
        elif isinstance(obj, Plane):
            return self.intersect_plane(obj)
        elif isinstance(obj, Tetrahedron):
            return self.intersect_tetrahedron(obj)
        elif isinstance(obj, Triangle):
            return self.intersect_triangle(obj)
        else:
            return -1
