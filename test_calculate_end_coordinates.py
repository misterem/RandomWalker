import pytest
import math
from Walker import Walker


def test_calculate_end_coordinates():
    walker = Walker(name="Wally", type=1, color="blue", graphic=True)

    # Test case: movement along x-axis
    x1, y1 = 0, 0
    angle = 0
    distance = 10
    expected_x, expected_y = 0, 10

    x2, y2 = walker.calculate_end_coordinates(x1, y1, angle, distance)
    assert math.isclose(expected_x, x2, abs_tol=0.00001) and math.isclose(expected_y, y2, abs_tol=0.00001)

    # Test case: movement along y-axis
    x1, y1 = 0, 0
    angle = 90
    distance = 10
    expected_x, expected_y = 10, 0

    x2, y2 = walker.calculate_end_coordinates(x1, y1, angle, distance)
    print(y2)
    assert math.isclose(expected_x, x2, abs_tol=0.00001) and math.isclose(expected_y, y2, abs_tol=0.00001)

    # Test case: movement along negative x-axis
    x1, y1 = 0, 0
    angle = 180
    distance = 10
    expected_x, expected_y = 0, -10

    x2, y2 = walker.calculate_end_coordinates(x1, y1, angle, distance)
    assert math.isclose(expected_x, x2, abs_tol=0.00001) and math.isclose(expected_y, y2, abs_tol=0.00001)

    # Test case: movement along negative y-axis
    x1, y1 = 0, 0
    angle = 270
    distance = 10
    expected_x, expected_y = -10, 0

    x2, y2 = walker.calculate_end_coordinates(x1, y1, angle, distance)
    assert math.isclose(expected_x, x2, abs_tol=0.00001) and math.isclose(expected_y, y2, abs_tol=0.00001)

    # Test case: movement at an arbitrary angle
    x1, y1 = 0, 0
    angle = 45
    distance = math.sqrt(2)
    expected_x, expected_y = 1, 1

    x2, y2 = walker.calculate_end_coordinates(x1, y1, angle, distance)
    assert math.isclose(expected_x, x2, abs_tol=0.00001) and math.isclose(expected_y, y2, abs_tol=0.00001)
