import os
import random
import tkinter as tk
import typing
from tkinter import colorchooser, ttk, messagebox, filedialog

import typing_extensions
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import numpy as np
import Walker
from typing import *

# global active_walker
class Gui(tk.Tk):
    """
    A class representing the GUI for the Random Walker simulation.

    Attributes:
    - walker_names: a list of names of the walkers in the simulation
    - walkers: a list of Walker objects in the simulation
    - walls: a list of wall coordinates in the simulation
    - portals: a dictionary mapping portal names to portal coordinates in the simulation
    - color: the default color of the walkers in the simulation
    - portal_color: the default color of the portals in the simulation
    - zoomed: the zoom level of the canvas in the simulation
    - iterating: a boolean indicating whether the simulation is currently iterating
    - moving: a boolean indicating whether the simulation is currently moving
    - seed: the seed for the random number generator in the simulation
    - spinval: the spin value for the Type 4 walker in the simulation
    """
    def __init__(self) -> None:
        super().__init__()
        self.spinval = tk.IntVar()
        self.walker_names: List[str] = []
        self.walkers: List[Walker.Walker] = []
        self.walls: List[int] = []
        self.portals: Dict[int, int] = {}
        self.color: Optional[str] = 'red'
        self.portal_color: Optional[str] = 'gold'
        self.zoomed = 1.0
        self.iterating = False
        self.moving = False
        self.seed: Union[str, int] = random.randint(1, 99999999)
        random.seed(str(self.seed))

        self.minsize(750, 500)
        self.title("The Random Walker")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.button_frame = tk.Frame(self, width=100, bg='red') # creates the frame for the buttons
        self.button_frame.grid(row=0, column=0)
        self.button_frame.grid(row=0, column=1)

        self._create_buttons()
        self.name1.focus_set()

        self.canvas = tk.Canvas(self, bg='white') # creates the canvas
        self.canvas.grid(row=0, column=2, sticky='nswe')
        self.center = (0, 0)
        self._xshifted = 0
        self._yshifted = 0
        self.click_position = (0.0, 0.0)
        self.wall = 0
        self.oval = 0
        self.add_wall_active = False
        self.add_portal_stage = 0

        # bindings
        self.bind('<B1-Motion>', self._drag)
        self.bind('<Shift-ButtonPress-1>', self._pre_drag)
        self.bind('<ButtonRelease-1>', self._pre_drag)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_move)
        self.bind("<MouseWheel>", self._zoom)
        self.bind("<Button-4>", self._zoom)
        self.bind("<Button-5>", self._zoom)
        self.canvas.bind("<space>", self.move_all_walkers)

    def create_axis(self) -> None:
        """
        Create the coordinate axes on the canvas.
        :return: None
        """
        mid_x = self.center[0]
        mid_y = self.center[1]
        self.canvas.create_line(0, 0, 0, -100, fill='black', arrow='last')
        self.canvas.create_line(0, 0, 100, 0, fill='black', arrow='last')
        self.canvas.scan_dragto(mid_x, mid_y, gain=1)
        self._xshifted = mid_x
        self._yshifted = mid_y

    def _create_buttons(self) -> None:
        """
        This method is used to create buttons and other UI elements for the app interface.
        :return: None
        """
        self.button_frame.grid_columnconfigure(0, weight=0)
        self.button_frame.grid_columnconfigure(1, weight=0)

        self.type = tk.IntVar()
        self.name = tk.StringVar()
        self.active_walker = tk.StringVar()
        label1_text = tk.StringVar()
        label2_text = tk.StringVar()
        label3_text = tk.StringVar()
        label1_text.set('Name Your Walker:')
        label2_text.set('Walker Type:')
        label3_text.set('Choose Walker:')

        self.button5 = tk.Button(self.button_frame, text='Get Seed', command=self.get_seed)
        self.button5.grid(row=1, column=0, sticky='ew', columnspan=1)
        self.button6 = tk.Button(self.button_frame, text='Set Seed', command=self.set_seed)
        self.button6.grid(row=1, column=1, sticky='ew', columnspan=1)
        self.label1 = tk.Label(self.button_frame, textvariable=label1_text, font="Helvetica")
        self.label1.grid(row=2, column=0, sticky='ew', columnspan=2)
        self.name1 = tk.Entry(self.button_frame, textvariable=self.name)
        self.name1.grid(row=3, column=0, sticky='ew', columnspan=2)
        self.label2 = tk.Label(self.button_frame, textvariable=label2_text, font="Helvetica")
        self.label2.grid(row=4, column=0, sticky='ew', columnspan=2)
        self.type1 = tk.Radiobutton(self.button_frame, text="Type 1", variable=self.type, value=1,
                                    background="light blue", fg="black")
        self.type1.grid(row=5, column=0, sticky='ew', columnspan=2)
        self.type2 = tk.Radiobutton(self.button_frame, text="Type 2", variable=self.type, value=2,
                                    background="light blue", fg="black")
        self.type2.grid(row=6, column=0, sticky='ew', columnspan=2)
        self.type3 = tk.Radiobutton(self.button_frame, text="Type 3", variable=self.type, value=3,
                                    background="light blue", fg="black")
        self.type3.grid(row=7, column=0, sticky='ew', columnspan=2)
        self.type4 = tk.Radiobutton(self.button_frame, text="Type 4", variable=self.type, value=4,
                                    background="light blue", fg="black")
        self.type4.grid(row=8, column=0, sticky='ew', columnspan=2)
        self.color1 = tk.Button(self.button_frame, text="Select Walker Color", command=self.choose_color)
        self.color1.grid(row=9, column=0, sticky='ew', columnspan=2)
        self.s = ttk.Style()
        self.s.configure('color.TFrame', background=self.color)
        ttk.Frame(self.button_frame, width=200, height=20, style='color.TFrame').grid(row=10, column=0, sticky='ew',
                                                                                      columnspan=2)
        self.button1 = tk.Button(self.button_frame, text='Create Walker', command=self.make_walker)
        self.button1.grid(row=11, column=0, sticky='ew', columnspan=2)
        self.label3 = tk.Label(self.button_frame, textvariable=label3_text, font="Helvetica")
        self.label3.grid(row=12, column=0, sticky='ew', columnspan=2)
        self.select_walker = ttk.Combobox(self.button_frame, values=self.walker_names, textvariable=self.active_walker)
        self.select_walker.grid(row=13, column=0, sticky='ew', columnspan=2)
        self.select_walker.set("Select Walker")
        self.iterations = tk.Scale(self.button_frame, orient="horizontal", length=200, from_=1.0, to=1000.0)
        self.iterations.grid(row=14, column=0, sticky='ew', columnspan=2)
        self.button2 = tk.Button(self.button_frame, text='Take Steps', command=self.iterate_walker)
        self.button2.grid(row=15, column=0, sticky='ew', columnspan=2)
        ttk.LabelFrame(self.button_frame, height=5).grid(row=16, column=0, sticky='ew', columnspan=2)
        self.button3 = tk.Button(self.button_frame, text='Add Wall', command=self.add_wall)
        self.button3.grid(row=17, column=0, sticky='ew', columnspan=2)
        self.button4 = tk.Button(self.button_frame, text='Add Portal', command=self.add_portal)
        self.button4.grid(row=18, column=0, sticky='ew', columnspan=2)
        ttk.LabelFrame(self.button_frame, height=5).grid(row=19, column=0, sticky='ew', columnspan=2)
        self.button5 = tk.Button(self.button_frame, text='Open Stats Window', command=self.stats_window)
        self.button5.grid(row=20, column=0, sticky='ew', columnspan=2)

    def get_canvas_center(self) -> Tuple[float, float]:
        """
        Return the coordinates of the center of the canvas.
        :return: Tuple containing the x and y coordinates of the center of the canvas.
        """
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        center_x = width // 2
        center_y = height // 2

        self.center = (center_x, center_y)
        return center_x, center_y

    def make_walker(self) -> None:
        """
        Make a new walker.
        """
        if self.name.get() == '':  # no name entered
            messagebox.showinfo("Error", "Please enter a name")
            return
        for walker in self.walkers:  # check if walker with the same name exists
            if self.name.get() == walker.name:
                messagebox.showinfo("Error", "Walker with this name already exists!")
                return
        if self.type.get() == 4:
            self._type_4_window()
        else: # creates the walker and adds it to walker lists
            walker1 = Walker.Walker(self.name.get(), self.type.get(), self.color, True, self)
            self.walker_names.append(walker1.get_name())
            self.walkers.append(walker1)
            self.select_walker['values'] = self.walker_names

    def make_walker_man(self, name: str, type: int, color, graphic=True) -> None:
        """
        Allows creation of a walker from the code as opposed to the GUI
        """
        walker1 = Walker.Walker(name, type, color, graphic, self)
        self.walker_names.append(walker1.get_name())
        self.walkers.append(walker1)
        self.select_walker['values'] = self.walker_names

    def choose_color(self) -> None:
        """
        Open a color chooser dialog to let the user select a color for the Walker.
        """
        color_code = colorchooser.askcolor(title="Choose Walker Color")
        self.color = color_code[1]
        if color_code[1]:
            self.s.configure('color.TFrame', background=self.color)

    def iterate_walker(self) -> None:
        """
        Iterates over the walkers, performing steps at regular intervals.
        """
        # resets the canvas zoom to avoid scale issues
        self.zoomed = 1 / self.zoomed
        self.canvas.scale('all', 0, 0, self.zoomed, self.zoomed)
        self.zoomed = 1

        def step(walker, delay, i=0):
            if i < iterations:
                walker.step()
                self.after(delay, step, walker, delay, i + 1)
            if i == iterations - 1:
                self.iterating = False

        name = self.select_walker.get()
        iterations = self.iterations.get()
        delay = int(5000 / iterations)  # make the walker iterate quickly
        delay = min(delay, 10)
        for walker in self.walkers:
            if name == walker.get_name():
                self.iterating = True
                step(walker, delay)

    def move_all_walkers(self, event) -> None:
        """
        Move all walkers by calling their step() method.
        """
        for walker in self.walkers:
            walker.step()

    def _pre_drag(self, event) -> None:
        """
        :param event: The event object containing information about the drag event.

        This method is called when a drag event is initiated. It focuses the widget receiving the event
        and performs various actions depending on the state of the application.
        """
        event.widget.focus_set()
        if not self.add_wall_active and self.add_portal_stage == 0:
            if (et := event.type.name) == 'ButtonPress' and str(self.focus_get()) == str(self.canvas):
                self.moving = True
                self._recent_drag_point_x = event.x
                self._recent_drag_point_y = event.y
                self.canvas.scan_mark(event.x, event.y)
                self.configure(cursor='fleur')
            elif et == 'ButtonRelease':
                self.configure(cursor='')
                self._recent_drag_point_x = None
                self._recent_drag_point_y = None
                self.moving = False

    def _drag(self, event) -> None:
        """
        This method is called when the user drags the canvas. It updates the canvas position
        based on the dragged distance and keeps track of the recent drag point.
        """
        if not self.add_wall_active and self.add_portal_stage == 0:
            if str(self.focus_get()) == str(self.canvas) and self.moving:
                self._xshifted += event.x - self._recent_drag_point_x
                self._yshifted += event.y - self._recent_drag_point_y
                self.canvas.scan_dragto(event.x, event.y, gain=1)
                self._recent_drag_point_x = event.x
                self._recent_drag_point_y = event.y
                self.canvas.scan_mark(event.x, event.y)

    def _zoom(self, event) -> None:
        """
        This method is used to perform zooming functionality on the canvas.
        It scales all the elements on the canvas based on the mouse wheel event.
        """
        if not self.iterating:
            if str(self.focus_get()) == str(self.canvas):
                multiplier = 1.01  # how fast to zoom
                factor = multiplier ** event.delta
                self.zoomed *= factor
                self.canvas.scale('all', 0, 0, factor, factor)

    def on_canvas_click(self, event) -> None:
        """
        The event handler for creating walls and portals
        """
        r = 5
        if self.add_wall_active or self.add_portal_stage == 1:
            if self.click_position == (0.0, 0.0):
                self.click_position = event.x, event.y
                fill = 'black' if self.add_wall_active else str(self.portal_color)
                self.wall = self.canvas.create_line(self.click_position[0] - self._xshifted,
                                                    self.click_position[1] - self._yshifted,
                                                    self.click_position[0] - self._xshifted,
                                                    self.click_position[1] - self._yshifted, width=3, fill=fill)
            else:
                self.canvas.coords(self.wall, self.click_position[0] - self._xshifted,
                                   self.click_position[1] - self._yshifted,
                                   event.x - self._xshifted, event.y - self._yshifted)
                if self.add_wall_active:
                    self.walls.append(self.wall)
                    self.click_position = (0.0, 0.0)
                    self.wall = 0
                self.add_wall_active = False
                if self.add_portal_stage == 1:
                    self.add_portal_stage = 2
                if self.add_portal_stage == 2:
                    if self.click_position != (0.0, 0.0):
                        self.oval = self.canvas.create_oval(self.click_position[0] - self._xshifted - r,
                                                            self.click_position[1] - self._yshifted - r,
                                                            self.click_position[0] - self._xshifted + r,
                                                            self.click_position[1] - self._yshifted + r,
                                                            fill=str(self.portal_color))
        elif self.add_portal_stage == 2:
            self.canvas.coords(self.oval, event.x - self._xshifted - r, event.y - self._yshifted - r,
                               event.x - self._xshifted + r, event.y - self._yshifted + r)
            self.portals.update({self.wall: self.oval})
            self.click_position = (0.0, 0.0)
            self.add_portal_stage = 0
            self.oval = 0
            self.wall = 0

    def on_canvas_move(self, event) -> None:
        """
        Extends the wall or portal on the canvas based on the event.
        """
        if self.click_position != (0.0, 0.0):
            if self.add_wall_active or self.add_portal_stage == 1:
                self.canvas.coords(self.wall, self.click_position[0] - self._xshifted,
                                   self.click_position[1] - self._yshifted,
                                   event.x - self._xshifted, event.y - self._yshifted)
            elif self.add_portal_stage == 2:
                r = 5
                self.canvas.coords(self.oval, event.x - self._xshifted - r, event.y - self._yshifted - r,
                                   event.x - self._xshifted + r,
                                   event.y - self._yshifted + r)

    def add_wall(self) -> None:
        """
        Called when clicking create wall button
        """
        if self.add_portal_stage == 0:
            self.add_wall_active = True

    def add_portal(self) -> None:
        """
        Called when clicking create portal button
        """
        if self.add_portal_stage == 0 and not self.add_wall_active:
            self.portal_color = colorchooser.askcolor(title="Choose Portal Color")[1]
            self.add_portal_stage = 1

    def get_seed(self) -> None:
        """
        Return the current seed value and display it in a messagebox.
        """
        self.clipboard_clear()
        self.clipboard_append(str(self.seed))
        messagebox.showinfo("", "Current Seed is <{}>".format(self.seed))

    def set_seed(self) -> None:
        """
        Set the seed value for the random number generator.
        This method opens a new window where the user can enter a seed value.
        """
        def put_seed() -> None:
            try:
                random.seed(str(seed.get()))
                self.seed = str(seed.get())
                new_window.destroy()
            except:
                messagebox.showinfo("Invalid seed", "Seed Not Set")
                new_window.destroy()

        new_window = tk.Toplevel(self)
        new_window.grab_set()
        new_window.title("Set Seed")
        new_window.geometry("300x80")
        new_window.resizable(False, False)
        tk.Label(new_window, text="Paste Seed:").place(x=10, y=10)
        seed = tk.StringVar()
        tk.Entry(new_window, textvariable=seed).place(x=100, y=10)
        tk.Button(new_window, text='Set Seed', command=put_seed, width=27).place(x=10, y=40)

    def _type_4_window(self) -> None:
        """
        Opens a new window to configure the probability of going in different directions for a Walker (type 4).
        """
        def update_scales(scale_to_ignore: int) -> None:
            """
            This method updates the scales in the GUI based on the given scale to ignore. It calculates the total value
            of all scales and adjusts the scales accordingly to ensure that the total value is not greater than 100.
            If the total value becomes less than or equal to 100 after adjustments, the method stops updating the scales.

            The method iterates through all the scales except the scale to ignore.
            If the total value exceeds 100, it subtracts the excess value from the scales proportionally.
            The proportion is determined by dividing the excess value by 5 and multiplying it by 5.

            After adjusting the scales, the method goes through all the scales again and sets any scale with a value
            greater than 0 to 0 if the total value is still greater than 100.
            """
            total = self.scale1.get() + self.scale2.get() + self.scale3.get() + self.scale4.get() + self.scale5.get()
            for scale in [scale for scale in [1, 2, 3, 4, 5] if scale != scale_to_ignore]:
                if total <= 100:
                    break
                adj_scale = eval('self.scale{}'.format(scale))
                diff = total - 100
                if diff < adj_scale.get():
                    adj_scale.set(adj_scale.get() - (diff // 5 * 5))
                    total = total - diff
            for scale in [scale for scale in [1, 2, 3, 4, 5] if scale != scale_to_ignore]:
                adj_scale = eval('self.scale{}'.format(scale))
                if adj_scale.get() > 0 and total > 100:
                    adj_scale.set(0)
                    total = total - adj_scale.get()

        def make_walker_4() -> None:
            chances = [self.scale1.get(), self.scale2.get(), self.scale3.get(), self.scale4.get(), self.scale5.get()]
            if sum(chances) != 100:
                messagebox.showinfo("Error", "Values must sum to 100")
            else:
                chances = [p / 100.0 for p in chances]
                # create the walker with given chances
                walker1 = Walker.Walker(self.name.get(), self.type.get(), self.color, True, self, chances)
                self.walker_names.append(walker1.get_name())
                self.walkers.append(walker1)
                self.select_walker['values'] = self.walker_names
                new_window.destroy()

        # GUI
        new_window = tk.Toplevel(self)
        new_window.grab_set()
        new_window.title("Configure Probability")
        new_window.geometry("205x350")
        tk.Label(new_window, text="Probability of going: ").place(x=30, y=10)
        tk.Label(new_window, text="Up:                                         %").place(x=10, y=50)
        tk.Label(new_window, text="Down:                                    %").place(x=10, y=100)
        tk.Label(new_window, text="Left:                                       %").place(x=10, y=150)
        tk.Label(new_window, text="Right:                                     %").place(x=10, y=200)
        tk.Label(new_window, text="To (0,0):                                %").place(x=10, y=250)
        self.scale1 = tk.Scale(new_window, from_=0, to=100, orient='horizontal', command=lambda _: update_scales(1),
                               resolution=5)
        self.scale2 = tk.Scale(new_window, from_=0, to=100, orient='horizontal', command=lambda _: update_scales(2),
                               resolution=5)
        self.scale3 = tk.Scale(new_window, from_=0, to=100, orient='horizontal', command=lambda _: update_scales(3),
                               resolution=5)
        self.scale4 = tk.Scale(new_window, from_=0, to=100, orient='horizontal', command=lambda _: update_scales(4),
                               resolution=5)
        self.scale5 = tk.Scale(new_window, from_=0, to=100, orient='horizontal', command=lambda _: update_scales(5),
                               resolution=5)
        tk.Button(new_window, text='Create Walker', command=make_walker_4).place(x=40, y=290)
        self.scale1.set(20)
        self.scale2.set(20)
        self.scale3.set(20)
        self.scale4.set(20)
        self.scale5.set(20)
        self.scale1.place(x=70, y=40)
        self.scale2.place(x=70, y=90)
        self.scale3.place(x=70, y=140)
        self.scale4.place(x=70, y=190)
        self.scale5.place(x=70, y=240)

    def stats_window(self) -> None:
        """
        Open a window displaying statistics and graphs for a selected walker.
        """
        selected_walker = tk.StringVar()
        active_walker = self.walkers[0]

        def rounded(list: List[float]) -> List[float]:
            """
            Receives a list of numbers and rounds them to the nearest 2 decimal places
            """
            return [round(val, 2) for val in list]

        def export_graphs() -> None:
            """
            Export images of the graphs for a selected walker and save them to a created folder
            """
            if selected_walker.get():
                filepath = filedialog.askdirectory()
                if filepath:
                    folder_name = "Graphs For {}".format(select_walker2.get())
                    new_folder_path = os.path.join(filepath, folder_name)
                    os.makedirs(new_folder_path, exist_ok=True)
                    fig1.savefig(os.path.join(new_folder_path, 'Graph1.png'))
                    fig2.savefig(os.path.join(new_folder_path, 'Graph2.png'))
                    fig3.savefig(os.path.join(new_folder_path, 'Graph3.png'))
                    fig4.savefig(os.path.join(new_folder_path, 'Graph4.png'))
            else:
                messagebox.showinfo("Error", "Please select a walker to export")

        def stats_to_text() -> None:
            """
            Creates a text file displaying statistics for a selected walker and saves it to a chosen location
            """
            if selected_walker.get():
                filepath = filedialog.askdirectory()
                if filepath:
                    with open(os.path.join(filepath, 'Stats For {}.txt'.format(select_walker2.get())), 'w') as f:
                        f.write('Statistics for {}'.format(select_walker2.get()))
                        f.write("\n")
                        if self.spinval.get() > 1:
                            f.write('Average of {} Walkers'.format(self.spinval.get()))
                        else:
                            f.write('Average of 1 Walker')
                        f.write("\n\n")
                        f.write("Average Distance From Center Per Step:")
                        f.write("\n")
                        f.write(str(rounded(active_walker.averages.av_distance_from_center[self.spinval.get() - 1])))
                        f.write("\n\n")
                        f.write("Average Distance From Axis Per Step:")
                        f.write("\n")
                        f.write("X axis: ")
                        f.write(str(rounded(active_walker.averages.av_distance_from_x[self.spinval.get() - 1])))
                        f.write("\n")
                        f.write("Y axis: ")
                        f.write(str(rounded(active_walker.averages.av_distance_from_y[self.spinval.get() - 1])))
                        f.write("\n\n")
                        f.write("Average Radius Crossed At Each Step:")
                        f.write("\n")
                        f.write(str(rounded(active_walker.averages.av_radius_steps[self.spinval.get() - 1])))
                        f.write("\n\n")
                        f.write("Average # of Times To Cross Axis Per Step:")
                        f.write("\n")
                        f.write("X axis: ")
                        f.write(str(rounded(active_walker.averages.av_times_crossed_x[self.spinval.get() - 1])))
                        f.write("\n")
                        f.write("Y axis: ")
                        f.write(str(rounded(active_walker.averages.av_times_crossed_y[self.spinval.get() - 1])))
            else:
                messagebox.showinfo("Error", "Please select a walker to export")

        def on_closing() -> None:
            """
            Protocol for closing the window
            """
            # reset averages of all walkers and deletes sub-walkers
            for walker in self.walkers:
                walker.subwalkers.clear()
                walker.averages.clear()
                walker.copies = 1
            new_window.grab_release()
            new_window.destroy()

        def update_plots(event=None) -> None:
            """
            Refresh and update all plots
            """
            fig1.tight_layout()
            fig2.tight_layout()
            fig3.tight_layout()
            fig4.tight_layout()
            canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            canvas3.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            canvas4.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            name = select_walker2.get()

            if not name:
                active_walker = self.walkers[0]
            for walker in self.walkers:
                if name == walker.get_name():
                    active_walker = walker

            if not select_walker2.get():
                selected_walker.set(self.walkers[0].get_name())

            active_walker.copy(self.spinval.get())

            # graph 1
            y = np.array(active_walker.averages.av_distance_from_center[self.spinval.get() - 1])
            plot1.clear()
            plot1.set(xlabel='steps', ylabel='distance from (0,0)', title='Average Distance From Center')
            plot1.plot(y)
            canvas1.draw()

            # graph 2
            y1 = np.array(active_walker.averages.av_distance_from_x[self.spinval.get() - 1])
            y2 = np.array(active_walker.averages.av_distance_from_y[self.spinval.get() - 1])
            plot2.clear()
            plot2.set(xlabel='steps', ylabel='distance', title='Average Distance From Axis')
            plot2.plot(y1, label='X axis')
            plot2.plot(y2, label='Y axis')
            plot2.legend()
            canvas2.draw()

            # graph 3
            x = np.array([i for i in range(active_walker.stats.iterations + 1)])
            y = np.array(active_walker.averages.av_radius_steps[self.spinval.get() - 1])
            plot3.clear()
            plot3.set(xlabel='steps', ylabel='radius', title='Average # of Steps To Exit Radius')
            plot3.plot(x, y)
            canvas3.draw()

            # graph 4
            y1 = np.array(active_walker.averages.av_times_crossed_x[self.spinval.get() - 1])
            y2 = np.array(active_walker.averages.av_times_crossed_y[self.spinval.get() - 1])
            plot4.clear()
            plot4.set(xlabel='steps', ylabel='times crossed', title='Average # of Times To Cross Axis')
            plot4.plot(y1, label='X axis')
            plot4.plot(y2, label='Y axis')
            plot4.legend()
            canvas4.draw()

        def create_figure_and_toolbar(master, xlabel: str, ylabel: str, title: str):
            fig = Figure(figsize=(5, 4), dpi=100)
            plot = fig.add_subplot(111)
            plot.set(xlabel=xlabel, ylabel=ylabel, title=title)

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=master)

            toolbar = NavigationToolbar2Tk(canvas, master)
            toolbar.update()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            return fig, canvas, toolbar, plot

        # GUI
        new_window = tk.Toplevel(self)
        new_window.grab_set()
        new_window.title("Statistics")
        new_window.geometry("500x600")
        new_window.resizable(False, False)
        n = ttk.Notebook(new_window)
        f1 = ttk.Frame(n, style='Danger.TFrame')
        f2 = ttk.Frame(n, style='Danger.TFrame')
        f3 = ttk.Frame(n, style='Danger.TFrame')
        f4 = ttk.Frame(n, style='Danger.TFrame')
        n.add(f1, text='Graph 1')
        n.add(f2, text='Graph 2')
        n.add(f3, text='Graph 3')
        n.add(f4, text='Graph 4')
        n.place(x=0, y=10, width=500, height=500)
        select_walker2 = ttk.Combobox(new_window, values=self.walker_names, textvariable=selected_walker)
        select_walker2.place(x=10, y=510)
        tk.Label(new_window, text="Average of                        walkers").place(x=10, y=540)
        self.spinval = tk.IntVar()
        s = ttk.Spinbox(new_window, from_=1.0, to=1000.0, textvariable=self.spinval, command=update_plots)
        s.place(x=85, y=540, width=75)
        s.set(1)
        tk.Button(new_window, text='Export All Graphs', command=export_graphs).place(x=250, y=505, width=200)
        tk.Button(new_window, text='Export Stats To Text', command=stats_to_text).place(x=250, y=540, width=200)

        fig1, canvas1, toolbar1, plot1 = create_figure_and_toolbar(f1, 'steps', 'distance from (0,0)',
                                                                   'Average Distance From Center')
        fig2, canvas2, toolbar2, plot2 = create_figure_and_toolbar(f2, 'steps', 'distance',
                                                                   'Average Distance From Axis')
        fig3, canvas3, toolbar3, plot3 = create_figure_and_toolbar(f3, 'steps', 'radius',
                                                                   'Average # of Steps To Exit Radius')
        fig4, canvas4, toolbar4, plot4 = create_figure_and_toolbar(f4, 'steps', 'times crossed',
                                                                   'Average # of Times To Cross Axis')

        # bindings
        new_window.bind('<<ComboboxSelected>>', update_plots)
        new_window.protocol("WM_DELETE_WINDOW", on_closing)
