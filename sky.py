import numpy as np

# Local Modules
from object import HollowSphere, Sphere
from ray import Ray
import utils


EARTH_RADIUS = 6378 * 1000
DEFAULT_CENTER = np.array([0, -EARTH_RADIUS, 0])
DEFAULT_ATMOSPHERE_HEIGHT = EARTH_RADIUS * 0.025
DEFAULT_SUN_DIRECTION = utils.normalize(np.array([0, 0.15, 1]))
DEFAULT_AVG_DENSITY_HEIGHT = 0.25 * DEFAULT_ATMOSPHERE_HEIGHT
IN_SCATTER_SAMPLES = 10
OPTICAL_DEPTH_SAMPLES = 10
COLOR_CHANNELS = 3
WAVE_LENGTHS = np.array([650, 510, 445])
SCATTERING_SCALE = 1
SCATTERING_COEFFICIENTS = (1 / np.power(WAVE_LENGTHS, 4)) * SCATTERING_SCALE
DENSITY_FALLOFF = 4
SUN_COLOR = np.array([1289, 1395, 1234])


class SkyDome:
    """
    A sky dome that will simulate an atmosphere and a planet.

    Attributes:
        center(ndarray): The position for the center of the planet
        radius(float): The radius of the planet
        sun_direction(ndarray): The direction vector pointing towards the
            sun
        atmosphere_height(float): The altitude on which the atmosphere ends
        avg_density_height(float): The altitude on which the average
            density of the atmosphere is
    """
    def __init__(
        self,
        center=DEFAULT_CENTER,
        radius=EARTH_RADIUS,
        sun_direction=DEFAULT_SUN_DIRECTION,
        atmosphere_height=DEFAULT_ATMOSPHERE_HEIGHT,
        avg_density_height=DEFAULT_AVG_DENSITY_HEIGHT
    ):
        self.center = center
        self.radius = radius
        self.sun_direction = sun_direction
        self.atmosphere_height = atmosphere_height
        self.avg_density_height = avg_density_height
        self.planet_obj = Sphere(center, None, None, radius)
        self.atmosphere_obj = HollowSphere(
            center, None, None, radius + atmosphere_height
        )

    @staticmethod
    def phase_function(v1, v2):
        return (3 / 4) * (1 + np.dot(v1, v2) ** 2)

    def density_at_point(self, p):
        height = utils.distance(p, self.center) - self.radius
        normalized_height = height / self.atmosphere_height
        density = np.exp(-normalized_height * DENSITY_FALLOFF) * (
                1 - normalized_height
        )
        # density = np.exp(-height / self.avg_density_height)
        return density

    def optical_depth(
        self, p, direction, distance, num_samples=OPTICAL_DEPTH_SAMPLES
    ):
        optical_depth = 0
        randoms = np.random.random_sample(num_samples)
        for i in range(num_samples):
            current_distance = (i + randoms[i]) * (distance / num_samples)
            sample_point = p + direction * current_distance
            sample_density = self.density_at_point(sample_point)
            optical_depth += sample_density * current_distance
        return optical_depth

    def out_scattering(
        self, p, direction, distance, num_samples=OPTICAL_DEPTH_SAMPLES
    ):
        optical_depth = self.optical_depth(p, direction, distance, num_samples)
        out_scattering = 4 * np.pi * SCATTERING_COEFFICIENTS * optical_depth
        return out_scattering

    def in_scattering(self, r, view_samples=IN_SCATTER_SAMPLES):
        randoms = np.random.random_sample(view_samples)
        dist_to_atmosphere = r.intersect(self.atmosphere_obj)
        transmittance = 0
        for i in range(view_samples):
            distance = (dist_to_atmosphere / view_samples) * (i + randoms[i])
            sample_point = r.at(distance)
            sun_ray = Ray(sample_point, self.sun_direction)
            t_to_atmosphere = sun_ray.intersect(self.atmosphere_obj)
            t_to_planet = sun_ray.intersect(self.planet_obj)
            if 0 < t_to_planet < t_to_atmosphere:
                continue
            out_sun = self.out_scattering(
                sun_ray.pr, sun_ray.nr, t_to_atmosphere
            )
            out_view = self.out_scattering(
                sample_point, -r.nr, distance
            )
            current_density = self.density_at_point(sample_point)
            transmittance += (
                current_density * np.exp(-(out_sun + out_view)) * distance
            ) * self.phase_function(sun_ray.nr, -r.nr)
        light = SUN_COLOR * SCATTERING_COEFFICIENTS * transmittance
        return light

    def light_at_ray(self, r, view_samples=IN_SCATTER_SAMPLES):
        # make samples along the ray
        # get contribution of each sample
        # Create one random number between 0 and 1 for each sample point
        light = np.zeros(COLOR_CHANNELS)
        randoms = np.random.random_sample(view_samples)
        dist_to_atmosphere = r.intersect(self.atmosphere_obj)
        for i in range(view_samples):
            distance = (dist_to_atmosphere / view_samples) * (i + randoms[i])
            sample_point = r.at(distance)
            sun_ray = Ray(sample_point, self.sun_direction)
            t_to_atmosphere = sun_ray.intersect(self.atmosphere_obj)
            t_to_planet = sun_ray.intersect(self.planet_obj)
            if 0 < t_to_planet < t_to_atmosphere:
                continue
            sun_ray_optical_depth = self.optical_depth(
                sun_ray.pr, sun_ray.nr, t_to_atmosphere
            )
            view_ray_optical_depth = self.optical_depth(
                sample_point, -r.nr, distance
            )
            transmittance = np.exp(
                -(sun_ray_optical_depth + view_ray_optical_depth)
                * SCATTERING_COEFFICIENTS
            )
            # Size for the segment of this function to be used for integration
            segment_size = (dist_to_atmosphere / view_samples) * randoms[i]
            sample_density = self.density_at_point(sample_point)
            light += sample_density * segment_size * transmittance
        light *= SCATTERING_COEFFICIENTS
        light /= self.radius
        light = np.clip(light, 0, 1)
        return light
