import os
import sys

from fcpxml_markers.cli import main

if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        os.environ["PATH"] = sys._MEIPASS + os.pathsep + os.environ["PATH"]

    main()
