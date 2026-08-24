"""
Water Jug Problem Simulator
Entry point — launches the Tkinter application window.
"""
import sys
import os

# Ensure the project root is on the path so all sub-packages resolve cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import WaterJugApp


def main():
    app = WaterJugApp()
    app.mainloop()


if __name__ == "__main__":
    main()