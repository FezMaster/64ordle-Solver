# 64ordle-Solver
Program that automatically solves 64 wordles at once, puzzles taken from https://64ordle.au

This program is built in Python 3.10 and so in order to run this program, the user is required to have Python v3.10 or later installed.
Secondly, this program relies heavily on the python Selenium module, version 4.1.3 and so this too (or a later version) is required. Use `pip install selenium` to install the module.

This program requires the user to have downloaded the driver for the browser they wish to use.
Browser drivers can be found here: https://www.selenium.dev/selenium/docs/api/py/index.html#drivers
The user must edit the code as it appears in the .py file, to change the name of the browser to be used and change the path to the browser driver.

The way this program works is by copying the html/js source code from https://64ordle.au,
and modifying the javascript to add in some extra functionality that makes accessing information easier.
Namely, a function which returns the present state of every cell on the whole game board. This modified source code is saved as an html file in the temp directory.
Then, selenium runs this html file in the user's browser of choice.
