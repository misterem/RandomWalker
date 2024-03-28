import math
import random
from Stats import WalkerStats, AverageStats
from typing import *

class Walker:
    def __init__(self, name: str, type: int, color, graphic: bool, app=None, chances=None, is_sub=False) -> None:
        """
        :param name: The name of the walker
        :param type: The type of the walker
        :param color: The color of the walker
        :param graphic: The graphic representation of the walker
        :param app: The application object (optional)
        :param chances: The list of chances (optional)
        :param is_sub: Flag indicating if the object is a subwalker (default False)

        This method initializes the object with the given parameters. If the `chances` parameter is not provided, an empty list will be used.
        The `name`, `type`, `color`, `graphic`, and `app` attributes will be set to the corresponding parameter values.
        If the `app` parameter is not None, the `myCanvas` attribute will be set to `app.canvas`.
        The `lastx`, `lasty`, `intersection`, `stats`, `copies`, and `subwalkers` attributes are initialized with default values.
        If `is_sub` is set to False, the `averages` attribute is initialized with an instance of the `AverageStats` class.
        """
        if chances is None:
            chances = []
        self.name = name
        self.type = type
        self.color = color
        self.app = app
        self.chances = chances
        self.graphic = graphic
        if app is not None:
            self.myCanvas = app.canvas
        self.lastx = 0.0
        self.lasty = 0.0
        self.intersection = False
        self.stats = WalkerStats()
        self.copies = 1
        self.subwalkers: List[Walker] = []
        if not is_sub:
            self.averages = AverageStats(self)

    def get_name(self) -> str:
        """
        :return: The name of the walker
        """
        return self.name

    def step(self) -> None:
        """
        This method performs a step in the simulation. It calculates the end coordinates based on the current position, direction, and distance. It checks for intersections with walls and portals
        * and adjusts the distance if needed. It then updates the last coordinates and the statistics.

        :param self: The instance of the class.
        :return: None
        """
        self.intersection = False
        direction = 0.0
        distance = 10.0
        if self.type == 1 or self.type == 2 or self.type == 3:
            if self.type == 2:
                distance *= random.uniform(0.5, 1.5)
            if self.type == 3:
                direction = random.randrange(0, 360, 90)
            else:  # type == 1
                direction = random.randint(0, 360)
        elif self.type == 4:
            # We create a list with the difference between each element being the chance percentage
            cum_percentages = [sum(self.chances[:i + 1]) for i in range(len(self.chances))]
            # get a random number between 0.00 and 1.00
            rand_num = random.random()
            if rand_num < cum_percentages[0]:
                direction = 180
            elif rand_num < cum_percentages[1]:
                direction = 0
            elif rand_num < cum_percentages[2]:
                direction = 270
            elif rand_num < cum_percentages[3]:
                direction = 90
            else:
                direction = self.calculate_angle_to_center(self.lastx, self.lasty)
        end_x, end_y = self.calculate_end_coordinates(self.lastx, self.lasty, direction, distance)
        line_coords = ((self.lastx, self.lasty), (end_x, end_y))
        # check if we will hit a wall in this step
        if self.obstacle_intersection('wall', line_coords) is None:
            portal = self.obstacle_intersection('portal', line_coords)
            # check if we will hit a portal in this step
            if portal is not None:
                obstacle_coords = self.app.canvas.coords(portal)
                obstacle_coords = ((obstacle_coords[0], obstacle_coords[1]), (obstacle_coords[2], obstacle_coords[3]))
                intersects = True
                while intersects and distance > 0:  # shortens the line until it doesn't intersect the portal
                    distance -= 0.01
                    end_x, end_y = self.calculate_end_coordinates(self.lastx, self.lasty, direction, distance)
                    line_coords = ((self.lastx, self.lasty), (end_x, end_y))
                    intersects = self.intersects(obstacle_coords, line_coords)
                if self.graphic:
                    self.myCanvas.create_line(line_coords, fill=self.color)
                # transport the line
                circle_coords = self.app.canvas.coords(self.app.portals[portal])
                center_x = (circle_coords[0] + circle_coords[2]) / 2
                center_y = (circle_coords[1] + circle_coords[3]) / 2
                end_x, end_y = self.calculate_end_coordinates(center_x, center_y, direction, distance)
            if self.graphic:
                self.myCanvas.create_line(line_coords, fill=self.color)
            self.lastx = end_x
            self.lasty = end_y
            self.stats.update((int(end_x), int(end_y)))
        else:
            self.step()

    def obstacle_intersection(self, obstacle: str, line_coords: tuple[tuple[float, float], tuple[float, float]]) -> Union[str, None]:
        """
        :param obstacle: The type of obstacle to check for intersection. Can be either 'wall' or 'portal'.
        :param line_coords: The coordinates of the line to check for intersection, in the format ((x1, y1), (x2, y2)).
        :return: The obstacle that intersects with the line, or None if no intersection is found.
        """
        list = self.app.walls if obstacle == 'wall' else self.app.portals
        for obstacle in list:
            obstacle_coords = self.app.canvas.coords(obstacle)
            obstacle_coords = ((obstacle_coords[0], obstacle_coords[1]), (obstacle_coords[2], obstacle_coords[3]))
            if self.intersects(obstacle_coords, line_coords):
                return obstacle
        return None

    def intersects(self, line1: tuple[tuple[float, float], tuple[float, float]], line2: tuple[tuple[float, float], tuple[float, float]]) -> bool:
        """
        :param line1: A tuple representing the coordinates of the first line segment in the format (x1, y1), (x2, y2)
        :param line2: A tuple representing the coordinates of the second line segment in the format (x1, y1), (x2, y2)
        :return: A boolean indicating whether the two line segments intersect or not

        This method determines whether two line segments intersect or not. The line segments are defined by the given coordinates.
        The method uses the orientation of points and whether a point lies on a line segment to make the determination.

        The method first extracts the coordinates of the two line segments from the given parameters.

        Next, it defines a nested function called orientation that computes the orientation of three points.
        The orientation is determined by calculating the cross product of the vectors formed by the points.
        If the cross product is positive, the points have a clockwise orientation.
        If the cross product is negative, the points have a counterclockwise orientation.
        And if the cross product is zero, the points are collinear.

        Another nested function called on_segment checks if a given point lies on a line segment.
        It does this by comparing the x and y coordinates of the point with the x and y coordinates of the line segment's endpoints.

        The method then calculates the orientations between the line segments' endpoints and the other line segment endpoints.
        There are four possible orientations: p1q1p2, p1q1q2, p2q2p1, and p2q2q1.

        If any of the four orientations are different, it means the line segments intersect.
        In this case, the method returns True.

        If any of the four orientations are collinear (equal to 0) and the corresponding point lies on the other line segment,
        it also means the line segments intersect.
        In this case, the method returns True.

        If none of the above conditions are met, it means the line segments do not intersect.
        In this case, the method returns False.
        """
        p1, q1 = line1[0], line1[1]
        p2, q2 = line2[0], line2[1]

        def orientation(p, q, r):
            val = (float(q[1] - p[1]) * (r[0] - q[0])) - (float(q[0] - p[0]) * (r[1] - q[1]))
            if val > 0:
                # Clockwise orientation
                return 1
            elif val < 0:
                # Counterclockwise orientation
                return 2
            else:
                # Collinear orientation
                return 0

        def on_segment(p, q, r):
            if (max(p[0], r[0]) >= q[0] >= min(p[0], r[0]) and
                    max(p[1], r[1]) >= q[1] >= min(p[1], r[1])):
                return True
            return False

        o1 = orientation(p1, q1, p2)
        o2 = orientation(p1, q1, q2)
        o3 = orientation(p2, q2, p1)
        o4 = orientation(p2, q2, q1)

        # General case
        if o1 != o2 and o3 != o4:
            return True

        # Special Cases (handles the case of collinear points)
        if o1 == 0 and on_segment(p1, p2, q1):
            return True
        if o2 == 0 and on_segment(p1, q2, q1):
            return True
        if o3 == 0 and on_segment(p2, p1, q2):
            return True
        if o4 == 0 and on_segment(p2, q1, q2):
            return True

        return False

    def calculate_end_coordinates(self, x: float, y: float, angle_degrees: float, distance: float) -> Tuple[float, float]:
        """
        Calculates the end coordinates based on the initial coordinates, angle, and distance.

        :param x: The initial x-coordinate.
        :param y: The initial y-coordinate.
        :param angle_degrees: The angle in degrees.
        :param distance: The distance to travel.
        :return: The end x and y coordinates.
        """
        # Convert angle from degrees to radians
        angle_radians = math.radians(angle_degrees)

        # Calculate the change in x and y coordinates
        delta_x = distance * math.sin(angle_radians)
        delta_y = distance * math.cos(angle_radians)

        # Calculate the end coordinates
        end_x = x + delta_x
        end_y = y + delta_y

        return end_x, end_y

    def calculate_angle_to_center(self, x: float, y: float) -> float:
        """
        :param x: X-coordinate of the point
        :param y: Y-coordinate of the point
        :return: Angle in degrees between the given point and the center of the coordinate system
        """
        angle_radians = math.atan2(x, y)
        angle_degrees = math.degrees(angle_radians)
        return angle_degrees + 180

    def copy(self, copies: int) -> None:
        """
        Create additional copies of the walker.

        :param copies: The number of copies to create.
        :type copies: int
        :return: None
        """
        for i in range(copies - self.copies):
            sub_walker = Walker(self.name, self.type, self.color, False, self.app, self.chances)
            self.subwalkers.append(sub_walker)
            for j in range(self.stats.iterations):
                sub_walker.step()
            self.averages.update(sub_walker, self.copies)
            self.copies += 1
