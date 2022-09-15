import time
import PySimpleGUI as sg
import pytesseract
# my files:
import globals
import image_processing
import gui
import poker_logic


def read(window):
    # this function is what tells what should be read from the screen, what should be calculated, and what should be
    # output
    initialized = False  # has the game application's parameters been read?
    new_hand = True
    errors_open = False  # the initial state of our error logs tab

    # we use increments for the chat, so that it reads every 10 loop iterations, as it is not needed more times
    chat_inc = 0

    while True:

        if not initialized:
            # when you first begin reading the game, or something has been moved, it needs to do a check
            # to see if the game's application window is readable
            # if it is readable then it gives us our global parameters

            start_time = time.time()  # the start of our timer
            gui.output_status(window, 'Waiting for you to play...')

            # the game application from which we are reading must be on the left side of our display
            half_screen = image_processing.get_initial_picture()  # gets the left half of the display

            if globals.interface['button_width'] == 0:  # if parameters have never been initialized
                initialized = image_processing.get_game_stats(half_screen, window)  # -> initializes them
            else:
                # if they have already been initialized, but in the meantime the game has been hidden or moved
                try:
                    # if it has been moved or resized then it does the initializing again
                    initialized = image_processing.check_if_moved(half_screen)  # -> initialized = False
                    initialized = image_processing.get_game_stats(half_screen, window)  # -> initialized = True
                except:
                    # if it has only been hidden, but nothing changed then we don't need to initialize it anymore
                    initialized = True

        while initialized:
            # while we have our parameters, and the game window is completely ok, we do the readings
            start_time = time.time()
            gui.output_status(window, 'Reading game...')

            # display screenshot's left half
            half_screen = image_processing.get_initial_picture()
            try:
                # if everything is ok, it gives us the game's and chat's picture which we will use for reading
                game_pic, chat_pic = image_processing.check_if_moved(half_screen)
            except:
                # if it is not ok, we begin from the initialization
                initialized = False
                break

            # gets the button location, as it will be a very important information
            button_location = image_processing.findbutton(game_pic)
            if not button_location:
                initialized = False
                break

            # until this point the actions were the same, regardless of reading a new hand of poker, or being already
            # inside one

            if not new_hand:
                # i put this option first, because if we see that a new hand has began, than we can just proceed to it
                # HandStats will contain all the information about the current hand, it is initialized in a new hand
                HandStats['game_pic'] = game_pic
                chat_inc += 1

                button_player_id = image_processing.button_at_player(HandStats['players_objects'], button_location)

                # button has gone to different player -> a new hand has been dealt
                if HandStats['players_objects'][button_player_id].role != 'Bt':
                    new_hand = True

                else:
                    # checks which player has the visual cue which tells us whose actions we need to read
                    action_player_id, HandStats = image_processing.find_visual_cue(HandStats, window)
                    if action_player_id is not None:
                        # if the player has been found then we read from the game picture the information that we need
                        # after that, we determine the player's actions
                        HandStats = poker_logic.get_hand_information(HandStats, action_player_id, window)

                    # outputs every information that we found
                    gui.output_players_cards_actions_time(window, HandStats, start_time, new_hand)

            if new_hand:
                gui.clear_window(window)  # clear the ui from the last hand

                # reads from the game picture every information about a new hand
                results = image_processing.read_new_hand(game_pic, button_location, window)
                try:
                    game_pic, chat_pic, my_cards, table_cards, players_objects, pot = results
                except:
                    initialized = results
                    break

                # processes the information which we read
                # creates the HandStats variable which contains all the information about our hand
                HandStats = poker_logic.new_hand_initializer(game_pic, my_cards, table_cards, players_objects, pot,
                                                             window)

                # outputs every information that we found
                gui.output_players_cards_actions_time(window, HandStats, start_time, new_hand)
                new_hand = False

            if chat_inc == 10:
                # reads and outputs the chat
                text = pytesseract.image_to_string(chat_pic)
                gui.output_chat(window, text)
                chat_inc = 0

            # Waits 700 miliseconds for us to make an input. If we give nothing then it does nothing
            event, values = window.read(timeout=700)
            if event == sg.WIN_CLOSED or event == 'STOP':
                return  # closes the read loop and goes back to the menu

            if event == 'ERRORS':
                # opens and closes the error logs tab
                errors_open = not errors_open
                window['ERRORLOGS'].update(visible=errors_open)

            if event.startswith('MODIFYPLAYER'):
                # here we can manually modify a player's information
                HandStats['players_objects'] = gui.modify_player(window, event, HandStats)

            if event == 'MODIFYMYCARDS':
                # here we can manually modify your cards
                HandStats['my_cards'] = gui.modify_my_cards(window, HandStats)

            if event == 'MODIFYTABLECARDS':
                # here we can manually modify the table cards
                HandStats['table_cards'] = gui.modify_table_cards(window, HandStats)

            if event == 'MODIFYPOT':
                # here we can manually modify the pot
                HandStats['pot'] = gui.modify_pot(window, HandStats)

        # to see how much time an unsuccessful initialization takes
        read_time = str(time.time() - start_time)[:5] + ' s'
        window['READ_TIME'].update(read_time)

        # this is only read if we are not in the 'while initialized' loop
        event, values = window.read(timeout=1000)
        if event == sg.WIN_CLOSED or event == 'STOP':
            return

        if event == 'ERRORS':
            # opens and closes the error logs tab
            errors_open = not errors_open
            window['ERRORLOGS'].update(visible=errors_open)

