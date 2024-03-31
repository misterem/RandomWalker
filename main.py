import sys
import Gui
from typing import *

def main() -> None:
    """
    This is the main method for running the Random Walker application.

    :return: None
    """
    try:
        if sys.argv[1] == "--help":
            print("To run Random Walker, type 'python main.py' \n")
            print("Useful shortcuts:")
            print(" Space: make all walkers take a step")
            print(" Shift + drag: enable screen to be moved")
            print(" Mouse scroll: zoom in/out")
    except IndexError:
        app = Gui.Gui()
        app.after(100, app.get_canvas_center)
        # app.after(100, app.create_axis)
        app.make_walker_man('Example Walker', 1, 'blue', True)
        app.mainloop()


if __name__ == "__main__":
    main()
