from typing import *
import Walker


class WalkerStats:
    def __init__(self) -> None:
        """
        Initialize an instance of the class creating initial statistic lists for self (a walker).
        """
        self.iterations = 0
        self.steps_locations = [(0, 0)]
        self.distance_from_center = [0]
        self.distance_from_x = [0]
        self.distance_from_y = [0]
        self.radius_steps = [0]
        self.times_crossed_x = [0]
        self.times_crossed_y = [0]

    def update(self, position: tuple[int, int]) -> None:
        """
        Updates the statistic lists with the new given position.

        :param position: The new position to update the stats with.
        :type position: tuple
        :return: None
        """
        self.iterations += 1
        self.steps_locations.append(position)

        self.distance_from_center.append(self.calculate_distance(position, (0, 0)))

        self.distance_from_x.append(abs(position[0]))
        self.distance_from_y.append(abs(position[1]))

        i = 0
        while self.distance_from_center[-1] > i:
            i += 1
        self.radius_steps.append(self.radius_steps[-1] + i)

        if round(self.steps_locations[self.iterations - 1][1] * position[1], 3) < 0:
            self.times_crossed_x.append(self.times_crossed_x[-1] + 1)
        elif round(self.steps_locations[self.iterations - 1][1] * position[1], 3) == 0:
            i = 1
            while round(self.steps_locations[self.iterations - i][1] * position[1], 3) == 0 and i < len(self.steps_locations) - 1:
                i += 1
            if round(self.steps_locations[self.iterations - i][1] * position[1], 3) < 0:
                self.times_crossed_x.append(self.times_crossed_x[-1] + 1)
            else:
                self.times_crossed_x.append(self.times_crossed_x[-1])
        else:
            self.times_crossed_x.append(self.times_crossed_x[-1])

        if round(self.steps_locations[self.iterations - 1][0] * position[0], 3) < 0:
            self.times_crossed_y.append(self.times_crossed_y[-1] + 1)
        elif round(self.steps_locations[self.iterations - 1][0] * position[0], 3) == 0:
            i = 1
            while round(self.steps_locations[self.iterations - i][0] * position[0], 3) == 0 and i < len(self.steps_locations) - 1:
                i += 1
            if round(self.steps_locations[self.iterations - i][0] * position[0], 3) < 0:
                self.times_crossed_y.append(self.times_crossed_y[-1] + 1)
            else:
                self.times_crossed_y.append(self.times_crossed_y[-1])
        else:
            self.times_crossed_y.append(self.times_crossed_y[-1])

    def calculate_distance(self, current_position: tuple[float, float], other_position: tuple[float, float]) -> int:
        """
        Calculate the Euclidean distance between two positions.

        :param current_position: A tuple representing the current position (x, y).
        :param other_position: A tuple representing the other position (x, y).
        :return: The Euclidean distance between the two positions.
        """
        return ((current_position[0] - other_position[0]) ** 2 + (
                    current_position[1] - other_position[1]) ** 2) ** 0.5

class AverageStats:
    """
    This class is responsible for calculating and updating average statistics of a walker.

    Attributes:
        walker (Walker): The walker object from which the statistics are calculated.
        av_distance_from_x (list): A list of average distance from x-axis over time.
        av_distance_from_y (list): A list of average distance from y-axis over time.
        av_distance_from_center (list): A list of average distance from the center over time.
        av_radius_steps (list): A list of average steps taken to reach the radius over time.
        av_times_crossed_x (list): A list of average times crossed the x-axis over time.
        av_times_crossed_y (list): A list of average times crossed the y-axis over time.

    Methods:
        __init__(self, walker):
            Initializes a new instance of the AverageStats class.

            Args:
                walker (Walker): The walker object from which the statistics are calculated.

        update(self, sub_walker, copies):
            Updates the average statistics based on a new sub_walker object.

            Args:
                sub_walker (Walker): The sub_walker object containing the statistics.
                copies (int): The number of copies of sub_walker in the current update cycle.

        clear(self):
            Clears the average statistics, resetting them to the initial walker statistics.
    """
    def __init__(self, walker) -> None:
        self.walker = walker
        self.walker_stats = walker.stats
        self.av_distance_from_x = [self.walker_stats.distance_from_x]
        self.av_distance_from_y = [self.walker_stats.distance_from_y]
        self.av_distance_from_center = [self.walker_stats.distance_from_center]
        self.av_radius_steps = [self.walker_stats.radius_steps]
        self.av_times_crossed_x = [self.walker_stats.times_crossed_x]
        self.av_times_crossed_y = [self.walker_stats.times_crossed_y]

    def update(self, sub_walker, copies: int) -> None:
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        list5 = []
        list6 = []
        sub_walker_stats = sub_walker.stats
        for i in range(len(sub_walker_stats.distance_from_center)):
            list1.append(round((sub_walker_stats.distance_from_center[i] + (self.av_distance_from_center[-1][i] * copies)) / (copies + 1), 4))
            list2.append(round((sub_walker_stats.distance_from_x[i] + (self.av_distance_from_x[-1][i] * copies)) / (copies + 1), 4))
            list3.append(round((sub_walker_stats.distance_from_y[i] + (self.av_distance_from_y[-1][i] * copies)) / (copies + 1), 4))
            list4.append(round((sub_walker_stats.times_crossed_x[i] + (self.av_times_crossed_x[-1][i] * copies)) / (copies + 1), 4))
            list5.append(round((sub_walker_stats.times_crossed_y[i] + (self.av_times_crossed_y[-1][i] * copies)) / (copies + 1), 4))
            list6.append(round((sub_walker_stats.radius_steps[i] + (self.av_radius_steps[-1][i] * copies)) / (copies + 1), 4))
        self.av_distance_from_center.append(list1)
        self.av_distance_from_x.append(list2)
        self.av_distance_from_y.append(list3)
        self.av_times_crossed_x.append(list4)
        self.av_times_crossed_y.append(list5)
        self.av_radius_steps.append(list6)

    def clear(self) -> None:
        self.av_distance_from_x = [self.walker_stats.distance_from_x]
        self.av_distance_from_y = [self.walker_stats.distance_from_y]
        self.av_distance_from_center = [self.walker_stats.distance_from_center]
        self.av_radius_steps = [self.walker_stats.radius_steps]
        self.av_times_crossed_x = [self.walker_stats.times_crossed_x]
        self.av_times_crossed_y = [self.walker_stats.times_crossed_y]
