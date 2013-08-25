import numpy as np
from math import sin, cos, acos, atan, pi

#This module provides some utility functions that are likely to be common across leap presets.
################################################################################
# **** IMPORTANT NOTE ****  **** IMPORTANT NOTE ****  **** IMPORTANT NOTE **** #
#                                                                              #
# The leap controller MUST BE POSITIONED PRECISELY CORRECT for the positional  #
# inference to work. The wire coming out of the leap should be to the left     #
# when facing the door of the dome.                                            #
#                                                                              #
# **** IMPORTANT NOTE ****  **** IMPORTANT NOTE ****  **** IMPORTANT NOTE **** #
################################################################################


def getPointerLocation(pointable):
    """Given a Pointable object, attempts to guess where the user is pointing
    This version does NOT take into account the user's hand position, which
    will introduce some error if the hand is particularly far from the sensor"""
    return projectSphereToScene(DirectionToSphere(pointable.direction))


def projectSphereToScene(spherical_coordinates):
    """Given phi (angle off of z-axis) and theta (where is it radially?),
    returns a rough estimate of the position in screen-space coordinates"""
    spherespace_radius = 450 ##the rough radius of the pentagon
    phi = spherical_coordinates['phi']
    theta = spherical_coordinates['theta']
    dot_product = sin(phi)
    screenspace_radius = spherespace_radius * dot_product
    screenspace_coordinates = screenspace_radius * \
        np.array([sin(theta), -cos(theta)])
    return screenspace_coordinates + 500


def DirectionToSphere(direction):
    """The Z-axis points away from the door. The Y-axis points up. The x-axis
    ponts to the right if looking at the door. E.g. standard OpenGL
    Zero phi is straight up; zero theta is pointing at the door"""
    normalized = direction.normalized
    x, y, z = normalized.x, normalized.y, normalized.z
    sphere = {}
    if(z == 0.0):
        theta = pi/2 + (pi if x < 0 else 0)
    else:
        theta = atan(x/-z)
    if(z > 0):
        theta += pi
    sphere['theta'] = theta
    sphere['phi'] = acos(y)
    return sphere
