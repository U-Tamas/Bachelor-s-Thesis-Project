import os

project_dir = os.getcwd()   # gets the current directory where this application's files are located

# these are the files and directories needed for our application to be able to read a poker game
screenshotpath = f'{project_dir}/screenshot/screenshot.jpg'
cards_path = f'{project_dir}/images/cards'
icon_path = f'{project_dir}/images/pokerstars/app_icon.jpg'
suits_path = f'{project_dir}/images/pokerstars/suits'
ranks_path = f'{project_dir}/images/pokerstars/ranks'
enemy_path = f'{project_dir}/images/pokerstars/enemy.jpg'
button_path = f'{project_dir}/images/pokerstars/button.jpg'

# folder where it stores error images
errors_path = f'{project_dir}/images/errors'

# the text needed for our error logs; it will be updated constantly
error_text = ''

# this interface will be initialized once, and is needed for the readings of the game's elements
# once the game's window is resized, the values will be changed
interface = {
    'app_bar_pic': 0,
    'app_bar_coords': (0, 0),
    'app_bar_width': 0,
    'app_bar_height': 0,
    'chat_coords': (0, 0),
    'chat_width': 0,
    'chat_height': 0,
    'my_card_width': 0,
    'my_card_height': 0,
    'button_width': 0,
    'button_height': 0,
    'enemy_width': 0,
    'enemy_height': 0,
}
