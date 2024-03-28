import pytest
import math
from Walker import Walker


# Test that the calculate_angle_to_center function returns correct results
def test_calculate_angle_to_center():
    walker = Walker("Test Walker", "type", "color", "graphic")

    # Case when x=0 and y=0
    result = walker.calculate_angle_to_center(0, 0)
    assert math.isclose(result, 180, rel_tol=1e-5), "The angle for point (0, 0) should be 180 but got {}".format(result)

    # Case when x=1 and y=0
    result = walker.calculate_angle_to_center(1, 0)
    assert math.isclose(result, 270, rel_tol=1e-5), "The angle for point (1, 0) should be 270 but got {}".format(result)

    # Case when x=0 and y=1
    result = walker.calculate_angle_to_center(0, 1)
    assert math.isclose(result, 180, rel_tol=1e-5), "The angle for point (0, 1) should be 0 but got {}".format(result)

    # Case when x=1 and y=1
    result = walker.calculate_angle_to_center(1, 1)
    assert math.isclose(result, 225, rel_tol=1e-5), "The angle for point (1, 1) should be 225 but got {}".format(result)

    # Case when x=-1 and y=-1
    result = walker.calculate_angle_to_center(-1, -1)
    assert math.isclose(result, 45, rel_tol=1e-5), "The angle for point (-1, -1) should be 45 but got {}".format(result)

    # Case when x is positive and y is negative
    result = walker.calculate_angle_to_center(1, -1)
    assert math.isclose(result, 315, rel_tol=1e-5), "The angle for point (1, -1) should be 315 but got {}".format(
        result)

    # Case when x is negative and y is positive
    result = walker.calculate_angle_to_center(-1, 1)
    assert math.isclose(result, 135, rel_tol=1e-5), "The angle for point (-1, 1) should be 135 but got {}".format(
        result)
