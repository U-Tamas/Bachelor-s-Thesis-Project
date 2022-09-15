"""This is a poker reading application. It reads the information from a poker game currently being played on
the screen.
It utilises OpenCV for image processing, and PyTesseract for OCR. For the GUI it uses PySimpleGUI.
The application currently is only able to read games from the Pokerstars application.
You can find the instructions in the README file.
"""

import pytesseract

# my files:
import gui
import app_functions


if __name__ == '__main__':
    window = gui.create_main_window()

    # We have to exit the program if we cannot find tesseract's path. The program cannot function without it
    if (tess_path := app_functions.findtesseract()) is None:
        exit()

    # you need to change the 'tess_path' to your current pytesseract installation folder, where the tesseract.exe is
    # located
    pytesseract.pytesseract.tesseract_cmd = tess_path

    gui.read_loop(window)     # begins the reading loop


"""Made by Ujlaki Tamas - Student Informatica anul 3 la Universitatea Technica Cluj Napoca - Centrul Universitar
Baia Mare
"""