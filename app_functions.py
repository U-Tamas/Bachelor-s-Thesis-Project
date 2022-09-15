import PySimpleGUI as sg
import time
import os
import string


def findtesseract():
    # when we start up our application, it creates a small window which will close automatically when the Pytesseract
    # installation is found, else it tells you to either install Pytesseract, or put in manually the installation folder

    # here we create the small window
    sg.theme('DarkRed1')
    layout = [[sg.Text('', pad=(5, 15), key='TEXT')],
              [sg.Button('OK', key='OK', visible=False)]]
    tess_window = sg.Window('Find Tesseract', layout, font=('Bahnschrift', 13), keep_on_top=True,
                            element_justification='center', modal=True, no_titlebar=True, margins=(40, 30),
                            finalize=True)

    # here we start looking for the pytesseract installation
    available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]

    for drive in available_drives:
        first_dirs = os.listdir(f"{drive}/")
        if 'Tesseract-OCR' in first_dirs:
            tess_window.close()
            del tess_window
            return f"{drive}/Tesseract-OCR/tesseract"
        else:
            for fdir in first_dirs:
                try:
                    second_dirs = os.listdir(f"{drive}/{fdir}")
                    if 'Tesseract-OCR' in second_dirs:
                        tess_window.close()
                        del tess_window
                        return f"{drive}/{fdir}/Tesseract-OCR/tesseract"
                    else:
                        for sdir in second_dirs:
                            try:
                                third_dirs = os.listdir(f"{drive}/{fdir}/{sdir}")
                                if 'Tesseract-OCR' in third_dirs:
                                    tess_window.close()
                                    del tess_window
                                    return f"{drive}/{fdir}/{sdir}/Tesseract-OCR/tesseract"
                            except:
                                pass
                except:
                    pass

    tess_window['TEXT'].update('Tesseract was not found on your computer.'
                               "\nIf it's not installed, please do it from the link in the README file!"
                               '\nIf it has been installed, please edit the "main.py" to include the'
                               '\nTesseract installation folder!'
                               '\n Edit : main.py -> line:23')

    tess_window['OK'].update(visible=True)
    event, values = tess_window.read()
    if event in 'OK':
        tess_window.close()
        del tess_window
        return None


class Player:
    # every player in our hand will be a class like this
    def __init__(self, p_id, coords, name, money):
        self.id = p_id  # id = 0 will be the small blind
        self.coords = coords
        self.name = name
        self.role = ''  # button, small blind, big blind
        self.money = money
        self.status = True  # true/fale = active/folded in current hand

    def set_id(self, p_id):
        self.id = p_id

    def set_role(self, role):
        self.role = role

    def set_name(self, name):
        self.name = name

    def set_money(self, money):
        self.money = money

    def set_status(self, status):
        self.status = status


class Action:
    # every action by a player will be an instance of this class
    def __init__(self, p_id, name, action, value):
        self.id = p_id  # player's id
        self.name = name  # player name
        self.action = action  # 'f'=fold, 'ck'=check, 'cl'=call, 'r'=raise
        self.value = value  # money value for the action


def create_hand_stats_dictionary(game_pic, my_cards, table_cards, actions, pot, max_raise, players_objects):
    # will be created for every hand
    HandStats = {
        'game_pic': game_pic,
        'prev_pic': game_pic,
        'my_cards': my_cards,
        'table_cards': table_cards,
        'players_objects': players_objects,
        'actions': actions,
        'players_to_check': [],
        'pot': pot,
        'max_raise': max_raise,
        'last_who_raised': 1,   # id of the last player who raised
        'bar_check': [],        # players who can have the green bar in a given moment
        'activity_check': [],   # players whose activity we will check in a given moment
        'active_player_nb': len(players_objects),
        'action_player_id': 0,
        'prev_table_cards_nb': len(table_cards)
    }
    return HandStats
