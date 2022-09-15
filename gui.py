import PySimpleGUI as sg
from pyautogui import screenshot
import cv2 as cv
from datetime import datetime
import os
import time
# my files:
import globals
import reading_logic
import image_processing

# the files that we need for our user interface
_icon_ = f'{globals.project_dir}/images/ui/icon.ico'
_menuimage_ = f'{globals.project_dir}/images/ui/image2.png'
_actionbutton_ = f'{globals.project_dir}/images/ui/button1.png'
_cardimage_ = f'{globals.project_dir}/images/cards/unknown_card.png'
_changebutton_ = f'{globals.project_dir}/images/ui/change1.png'


def set_windowlocation():
    # returns the (display_width/2, 0) as coordinates to know where to place our window on the screen
    screenshot(globals.screenshotpath)
    pic = cv.imread(globals.screenshotpath)

    return pic.shape[1]//2, 0


def create_main_window():
    # creates and returns my application window
    # our application will have 2 different ui: for the menu, for the reading
    sg.theme('DarkBlack1')
    transparent = sg.theme_background_color()

    description = 'Această aplicație citește cărți dintr-un joc de poker care se desfășoară într-o altă ' \
                  'aplicație de pe ecran'

    # gets the coordinates to know where to put the window
    # it will place it in the upper right half of our display
    w_location = set_windowlocation()

    # the layout for the menu
    menu = sg.pin(sg.Column([
        [sg.Text(description, size=(70, 3), key='DESCRIPTION')],
        [sg.Column([[sg.Image(_menuimage_, key='IMAGE')]], justification='center')],
        [sg.Column([[sg.Button('Start Reading', key='START', image_filename=_actionbutton_, button_color=transparent,
                               border_width=0),
                     sg.Button('Exit', key='EXIT', image_filename=_actionbutton_, button_color=transparent,
                               border_width=0)]], justification='center')]
    ], key='MENU', justification='center'), shrink=True)

    # the layout for the game: gamecol1+gamecol2
    textbcgk = 'gray24'
    gamecol1 = sg.pin(sg.Column([
        [sg.Text('Status:    '), sg.Text('', key='STATUS')],
        [sg.Text('Read time: '), sg.Text('0.000 s', key='READ_TIME')],
        [sg.HorizontalSeparator(pad=(5, 15))],
        [sg.Text('Pot: '), sg.Text('0000', key='POT'),
         sg.Button('', key='MODIFYPOT', image_filename=_changebutton_, button_color=transparent, border_width=0)],
        [sg.Text('  ', size=(3, 1), background_color='maroon'),
         sg.Text('-Name-', size=(15, 1), background_color='maroon'),
         sg.Text('-Money-', size=(10, 1), background_color='maroon')],

        [sg.Text('', size=(3, 1), key='ROLE0', background_color=textbcgk),
         sg.Text('', size=(15, 1), key='NAME0', background_color=textbcgk),
         sg.Text('', size=(10, 1), key='MONEY0', background_color=textbcgk),
         sg.Button('', key='MODIFYPLAYER0', visible=True, image_filename=_changebutton_, button_color=transparent,
                   border_width=0)],
        [sg.Text('', size=(3, 1), key='ROLE1'), sg.Text('', size=(15, 1), key='NAME1'),
         sg.Text('', size=(10, 1), key='MONEY1'),
         sg.Button('', key='MODIFYPLAYER1', visible=True, image_filename=_changebutton_, button_color=transparent,
                   border_width=0)],
        [sg.Text('', size=(3, 1), key='ROLE2', background_color=textbcgk),
         sg.Text('', size=(15, 1), key='NAME2', background_color=textbcgk),
         sg.Text('', size=(10, 1), key='MONEY2', background_color=textbcgk),
         sg.Button('', key='MODIFYPLAYER2', visible=True, image_filename=_changebutton_, button_color=transparent,
                   border_width=0)],
        [sg.Text('', size=(3, 1), key='ROLE3'), sg.Text('', size=(15, 1), key='NAME3'),
         sg.Text('', size=(10, 1), key='MONEY3'),
         sg.Button('', key='MODIFYPLAYER3', visible=True, image_filename=_changebutton_, button_color=transparent,
                   border_width=0)],
        [sg.Text('', size=(3, 1), key='ROLE4', background_color=textbcgk),
         sg.Text('', size=(15, 1), key='NAME4', background_color=textbcgk),
         sg.Text('', size=(10, 1), key='MONEY4', background_color=textbcgk),
         sg.Button('', key='MODIFYPLAYER4', visible=True, image_filename=_changebutton_, button_color=transparent,
                   border_width=0)],
        [sg.Text('', size=(3, 1), key='ROLE5'), sg.Text('', size=(15, 1), key='NAME5'),
         sg.Text('', size=(10, 1), key='MONEY5'),
         sg.Button('', key='MODIFYPLAYER5', visible=True, image_filename=_changebutton_, button_color=transparent,
                   border_width=0)],

        [sg.HorizontalSeparator(pad=(5, 15))],
        [sg.Output(size=(35, 6), key='PLAYERS_ACTIONS')],
        [sg.Button('Error Logs', key='ERRORS', image_filename=_actionbutton_, button_color=transparent,
                   border_width=0)],
    ], key='GAMECOL1', visible=False), shrink=True)

    gamecol2 = sg.pin(sg.Column([
        [sg.Text('Your Cards: ')],
        [sg.Image(_cardimage_, subsample=5, key='MYCARD0'), sg.Image(_cardimage_, subsample=5, key='MYCARD1'),
         sg.Button('', key='MODIFYMYCARDS', image_filename=_changebutton_, button_color=transparent,
                   border_width=0)],
        [sg.HorizontalSeparator(pad=(5, 15))],
        [sg.Text('Table Cards:')],
        [sg.Image(_cardimage_, subsample=7, key='TABLECARD0'), sg.Image(_cardimage_, subsample=7, key='TABLECARD1'),
         sg.Image(_cardimage_, subsample=7, key='TABLECARD2'),
         sg.Image(_cardimage_, subsample=7, key='TABLECARD3'), sg.Image(_cardimage_, subsample=7, key='TABLECARD4'),
         sg.Button('', key='MODIFYTABLECARDS', image_filename=_changebutton_, button_color=transparent,
                   border_width=0)],
        [sg.Output(size=(48, 6), key='CHAT')],
        [sg.Column([[sg.Button('Stop Reading', key='STOP', image_filename=_actionbutton_, button_color=transparent,
                               border_width=0)]], justification='center')]
    ], key='GAMECOL2', visible=False), shrink=True)

    # little error log tab which we can open while in the reading process
    errors = sg.pin(sg.Column([
        [sg.Output(size=(80, 15), key='ERRORTEXT')],
    ], key='ERRORLOGS', visible=False), shrink=True)

    layout = [[menu], [gamecol1, sg.VSeparator(pad=(5, 15)), gamecol2], [errors]]

    # this crates the window
    window = sg.Window('Poker reader', layout, icon=_icon_, font='Bahnschrift', location=w_location, finalize=True)
    sg.Window.refresh(window)  # we need to call this, because if not then the window won't appear instantly
    return window


def read_loop(window):
    # our application runs until you either close it's window or press on the exit button in the menu
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'EXIT':
            break
        # it changes the ui when switching between the menu and the reading process
        # it changes by hiding and making appear certain elements
        if event == 'START':
            window['MENU'].update(visible=False)
            window['GAMECOL1'].update(visible=True)
            window['GAMECOL2'].update(visible=True)
            # window['ERRORLOGS'].update(visible=True)
            sg.Window.refresh(window)
            reading_logic.read(window)
            window['MENU'].update(visible=True)
            window['ERRORLOGS'].update(visible=False)
            window['GAMECOL1'].update(visible=False)
            window['GAMECOL2'].update(visible=False)

    window.close()
    del window


def output_status(window, status):
    # outputs to the ui our application's status
    window['STATUS'].update(status)


def output_chat(window, chat):
    # outputs to the ui the game's chat
    window['CHAT'].update(chat)


def output_players_cards_actions_time(window, HandStats, start_time, new_hand):
    # this function gets the poker hands' information and writes it in our ui
    cardspath = globals.cards_path
    my_cards = HandStats['my_cards']
    table_cards = HandStats['table_cards']
    players_objects = HandStats['players_objects']

    if new_hand:
        # updates the visibility of the buttons with which we modify the players
        for i in range(len(players_objects)):
            window[f'MODIFYPLAYER{i}'].update(visible=True)

    # outputs every player's information
    for player in players_objects:
        if player.status == False:
            window[f'ROLE{player.id}'].update(text_color='gray58')
            window[f'NAME{player.id}'].update(text_color='gray58')
            window[f'MONEY{player.id}'].update(text_color='gray58')
        window[f'ROLE{player.id}'].update(player.role)
        window[f'NAME{player.id}'].update(player.name)
        window[f'MONEY{player.id}'].update(player.money)

    # outputs your cards
    for i in range(len(my_cards)):
        window[f'MYCARD{i}'].update(f'{cardspath}/{my_cards[i]}.png', subsample=5)

    # outputs the table cards
    for i in range(len(table_cards)):
        window[f'TABLECARD{i}'].update(f'{cardspath}/{table_cards[i]}.png', subsample=7)

    window['POT'].update(HandStats['pot'])

    # this makes a text about the actions which have been observed, and outputs them
    text = ''
    for action in HandStats['actions']:
        if action.action == 'sb':
            if action.value == 0:
                value = ''
            else:
                value = action.value
            text += f"{players_objects[action.id].name} posted the small blind {value}\n"

        if action.action == 'bb':
            if action.value == 0:
                value = ''
            else:
                value = action.value
            text += f"{players_objects[action.id].name} posted the big blind {value}\n"

        if action.action == 'f':
            text += f"{players_objects[action.id].name} folded\n"

        if action.action == 'ck':
            text += f"{players_objects[action.id].name} checked\n"

        if action.action == 'cl':
            text += f"{players_objects[action.id].name} called {action.value}\n"

        if action.action == 'r':
            text += f"{players_objects[action.id].name} bet {action.value}\n"

    window['PLAYERS_ACTIONS'].update(text)

    # outputs our loop iteration's current reading time
    read_time = str(time.time() - start_time)[:5] + ' s'
    window['READ_TIME'].update(read_time)


def modify_player(bkg_window, event, HandStats):
    # makes a little window which has a players informations, and lets us edit them
    # while this window is present, the main window is not being updated

    # first of all, it does a reading of the respective player's money and name, so that it has the chance to correct
    # itself without our input
    # however, if these informations are still inaccurate then we can change them manually
    name = image_processing.read_name_at_coord(HandStats['game_pic'],
                                               HandStats['players_objects'][int(event[-1])].coords, bkg_window)
    HandStats['players_objects'][int(event[-1])].set_name(name)

    money = image_processing.read_money_at_coord(HandStats['game_pic'],
                                                 HandStats['players_objects'][int(event[-1])].coords,
                                                 HandStats['players_objects'][int(event[-1])].name, bkg_window)
    HandStats['players_objects'][int(event[-1])].set_money(money)

    i = int(event[12])
    name = HandStats['players_objects'][i].name
    money = HandStats['players_objects'][i].money

    bkg_window.set_alpha(0.75)  # makes the background window a bit transparent
    sg.theme('DarkRed1')
    layout = [
        [sg.Text('Modify the player', font=('Bahnschrift', 14))],
        [sg.HorizontalSeparator(color='snow', pad=(10, 5))],
        [sg.Text('Name:  '), sg.Input(default_text=name, size=(15, 1), key='NAME')],
        [sg.Text('Money: '), sg.Input(default_text=money, size=(10, 1), key='MONEY')],
        [sg.Checkbox(text='Set as Folded', key='FOLDED')],
        [sg.Button(button_text="Submit", key='SUBMIT'), sg.Button(button_text="Cancel", key='CANCEL')]
    ]

    w_location = set_windowlocation()
    w_location = (int(w_location[0] * 1.30), w_location[0] // 5)
    window = sg.Window('Modify pot', layout, icon=_icon_, font='Bahnschrift', location=w_location,
                       keep_on_top=True, element_justification='center', modal=True, no_titlebar=True, margins=(40, 30))

    # it doesn't let us update the player unless every information we give is plausible
    ok = False
    while not ok:
        event, values = window.read()
        if event == 'CANCEL':
            window.close()
            del window
            bkg_window.set_alpha(1)
            return HandStats['players_objects']

        if event == 'SUBMIT':
            if values['NAME'] == '':
                sg.popup("You cannot leave the name empty")
            elif not values['MONEY'].isnumeric():
                sg.popup("Money must contain only numbers")
            elif len(values['MONEY']) > 6:
                sg.popup("Money number is too long")
            else:
                ok = True

    name = values['NAME']
    money = int(values['MONEY'])
    is_folded = values['FOLDED']

    window.close()
    del window
    bkg_window.set_alpha(1)

    HandStats['players_objects'][i].set_name(name)
    HandStats['players_objects'][i].set_money(money)
    if is_folded:
        HandStats['players_objects'][i].set_status(False)

    return HandStats['players_objects']


def modify_my_cards(bkg_window, HandStats):
    # makes a little window which has your cards, and lets us edit them
    # while this window is present, the main window is not being updated

    # first, it does a reading of your cards so that it can correct itself without our input
    # however, if this information is still inaccurate then we can change them manually
    my_cards, ___ = image_processing.get_my_cards(HandStats['game_pic'])
    if my_cards == []:
        my_cards = ['unknown_card', 'unknown_card']
    table_cards = HandStats['table_cards']

    bkg_window.set_alpha(0.75)
    sg.theme('DarkRed1')
    cards = []
    for file in os.listdir(globals.cards_path):
        if file.endswith('.png') and file != 'unknown_card.png':
            cards.append(file[:-4])

    layout = [
        [sg.Text('Modify your cards', font=('Bahnschrift', 14))],
        [sg.HorizontalSeparator(color='snow', pad=(10, 5))],
        [sg.Text('First card:  '), sg.Combo(cards, default_value=my_cards[0], key='MYCARD0', size=(15, 1))],
        [sg.Text('Second card: '), sg.Combo(cards, default_value=my_cards[1], key='MYCARD1', size=(15, 1))],
        [sg.Button(button_text="Submit", key='SUBMIT'), sg.Button(button_text="Cancel", key='CANCEL')]
    ]

    w_location = set_windowlocation()
    w_location = (int(w_location[0] * 1.30), w_location[0] // 5)
    window = sg.Window('Modify your cards', layout, icon=_icon_, font='Bahnschrift', location=w_location,
                       keep_on_top=True, element_justification='center', modal=True, no_titlebar=True, margins=(40, 30))

    # it doesn't let us make the updates unless every information we give is plausible
    ok = False
    while not ok:
        ok = True
        event, values = window.read()
        if event == 'SUBMIT':
            if values['MYCARD0'] == values['MYCARD1']:
                sg.popup("You cannot have the same card twice")
                ok = False
            else:
                new_array = [values['MYCARD0'], values['MYCARD1']]
                for i in range(len(new_array)):
                    if new_array[i] in table_cards:
                        sg.popup("You cannot have duplicate cards in hand and table")
                        ok = False
            if ok:
                my_cards = [values['MYCARD0'], values['MYCARD1']]

        if event == 'CANCEL':
            ok = True

    window.close()
    del window
    bkg_window.set_alpha(1)
    return my_cards


def modify_table_cards(bkg_window, HandStats):
    # makes a little window which has table cards, and lets us edit them
    # while this window is present, the main window is not being updated

    # first, it does a reading of the table cards so that it can correct itself without our input
    # however, if this information is still inaccurate then we can change them manually
    table_cards = image_processing.get_table_cards(HandStats['game_pic'])
    my_cards = HandStats['my_cards']

    bkg_window.set_alpha(0.75)
    sg.theme('DarkRed1')
    cards = []
    for file in os.listdir(globals.cards_path):
        if file.endswith('.png'):
            cards.append(file[:-4])

    new_array = []
    for i in range(len(table_cards)):
        new_array.append(table_cards[i])
    for i in range(len(table_cards), 5):
        new_array.append('unknown_card')

    layout = [
        [sg.Text('Modify table cards', font=('Bahnschrift', 14))],
        [sg.HorizontalSeparator(color='snow', pad=(10, 5))],
        [sg.Text('First card:   '), sg.Combo(cards, default_value=new_array[0], key='TABLECARD0', size=(15, 1))],
        [sg.Text('Second card:  '), sg.Combo(cards, default_value=new_array[1], key='TABLECARD1', size=(15, 1))],
        [sg.Text('Third card:   '), sg.Combo(cards, default_value=new_array[2], key='TABLECARD2', size=(15, 1))],
        [sg.Text('Fourth card:  '), sg.Combo(cards, default_value=new_array[3], key='TABLECARD3', size=(15, 1))],
        [sg.Text('Fifth card:   '), sg.Combo(cards, default_value=new_array[4], key='TABLECARD4', size=(15, 1))],
        [sg.Button(button_text="Submit", key='SUBMIT'), sg.Button(button_text="Cancel", key='CANCEL')]
    ]

    w_location = set_windowlocation()
    w_location = (int(w_location[0] * 1.30), w_location[0] // 5)
    window = sg.Window('Modify table cards', layout, icon=_icon_, font='Bahnschrift', location=w_location,
                       keep_on_top=True, element_justification='center', modal=True, no_titlebar=True, margins=(40, 30))

    # it doesn't let us make the updates unless every information we give is plausible
    ok = False
    while not ok:
        event, values = window.read()
        new_array = []
        if event == 'SUBMIT':
            ok = True
            for i in range(5):
                if values[f'TABLECARD{i}'] != 'unknown_card':
                    new_array.append(values[f'TABLECARD{i}'])

            if len(new_array) not in [0, 3, 4, 5]:
                sg.popup("There cannot be this amount of table cards")
                ok = False
            else:
                for j in range(len(new_array) - 1):
                    for k in range(j + 1, len(new_array)):
                        if new_array[j] == new_array[k]:
                            ok = False
                if not ok:
                    sg.popup("You cannot select a card more than once")

            for i in range(len(new_array)):
                if new_array[i] in my_cards:
                    sg.popup("You cannot have duplicate cards in hand and table")
                    ok = False

            if ok:
                table_cards = new_array

        if event == 'CANCEL':
            ok = True

    window.close()
    del window
    bkg_window.set_alpha(1)
    return table_cards


def modify_pot(bkg_window, HandStats):
    # makes a little window which has the pot, and lets us edit it
    # while this window is present, the main window is not being updated

    # first, it does a reading of the pot so that it can correct itself without our input
    # however, if this information is still inaccurate then we can change it manually
    pot = image_processing.readpot(HandStats['game_pic'], bkg_window)

    bkg_window.set_alpha(0.75)
    sg.theme('DarkRed1')
    layout = [
        [sg.Text('Modify the pot', font=('Bahnschrift', 14))],
        [sg.HorizontalSeparator(color='snow', pad=(10, 5))],
        [sg.Text('Pot value:'), sg.Input(default_text=pot, size=(15, 1), key='POT')],
        [sg.Button(button_text="Submit", key='SUBMIT'), sg.Button(button_text="Cancel", key='CANCEL')]
    ]

    w_location = set_windowlocation()
    w_location = (int(w_location[0] * 1.30), w_location[0] // 5)
    window = sg.Window('Modify pot', layout, icon=_icon_, font='Bahnschrift', location=w_location,
                       keep_on_top=True, element_justification='center', modal=True, no_titlebar=True, margins=(40, 30))

    # it doesn't let us make the updates unless the information we give is plausible
    ok = False
    while not ok:
        event, values = window.read()
        if event == 'SUBMIT':
            if not values['POT'].isnumeric():
                sg.popup("Pot must contain only numbers")
            elif len(values['POT']) > 6:
                sg.popup("Pot number is too long")
            else:
                pot = int(values['POT'])
                ok = True

        if event == 'CANCEL':
            ok = True

    window.close()
    del window
    bkg_window.set_alpha(1)

    return pot


def clear_window(window):
    # this resets our ui from the information from the last hand played
    cardspath = globals.cards_path
    for i in range(6):
        window[f'ROLE{i}'].update('')
        window[f'NAME{i}'].update('')
        window[f'MONEY{i}'].update('')
        window[f'ROLE{i}'].update(text_color='floral white')
        window[f'NAME{i}'].update(text_color='floral white')
        window[f'MONEY{i}'].update(text_color='floral white')
        window[f'MODIFYPLAYER{i}'].update(visible=False)

    for i in range(5):
        window[f'TABLECARD{i}'].update(f'{cardspath}/unknown_card.png', subsample=7)

    for i in range(2):
        window[f'MYCARD{i}'].update(f'{cardspath}/unknown_card.png', subsample=5)

    window['PLAYERS_ACTIONS'].update('')
    window['ERRORLOGS'].update('')
    window['CHAT'].update('')


def error(window, msg):
    # gets error messages from our application, it adds it to our global error message
    # texts, and outputs them
    # we write the current time for every error message
    text = f"\n - {datetime.now().strftime('%H:%M:%S')} - {msg}"
    globals.error_text += text
    window['ERRORTEXT'].update(globals.error_text)
