# my files:
import app_functions
import image_processing
import gui


def new_hand_initializer(game_pic, my_cards, table_cards, players_objects, pot, window):
    # gets the game's picture, the cards, player objects, and pot, and will calculate what acitons have the players
    # taken such as betting small blind and big blind this function also initializes the HandStats variable which has
    # all the information about the current hand, and returns it

    # sets player's roles to Small Blind, Big Blind, Button
    players_objects[0].set_role('SB')
    players_objects[1].set_role('BB')
    if len(players_objects) > 2:
        players_objects[-1].set_role('Bt')
    else:
        players_objects[0].set_role('Bt')

    actions = []
    sb_id = 0
    bb_id = 1
    small_blind = 0
    max_raise = -1
    if table_cards == []:  # we are pre-flop
        # calculating the small and big blinds based on the pot size
        if pot % 3 == 0:
            small_blind = pot // 3
        elif pot % 5 == 0:
            small_blind = pot // 5
        elif pot % 7 == 0:
            small_blind = pot // 7

        big_blind = small_blind * 2
        # max_raise = small_blind

        # we create new Action type classes and append them in the actions array
        actions.append(app_functions.Action(sb_id, players_objects[sb_id].name, 'sb', small_blind))
        actions.append(app_functions.Action(bb_id, players_objects[bb_id].name, 'bb', big_blind))
        # Action = id, name, type_of_action, money_value

    else:
        # if we are not preflop we cannot calculate the blinds
        actions.append(app_functions.Action(sb_id, players_objects[sb_id].name, 'ck', 0))
        gui.error(window, "Cloudn't determine the blinds because of the gotten pot value")

    # initialize HandStats
    HandStats = app_functions.create_hand_stats_dictionary(game_pic, my_cards, table_cards, actions, pot, max_raise,
                                                           players_objects)

    HandStats['bar_check'], HandStats['activity_check'] = create_checking_arrays(HandStats, window)

    return HandStats


def create_checking_arrays(HandStats, window):
    lwr = HandStats['last_who_raised']
    players = HandStats['players_objects']
    max_raise = HandStats['max_raise']

    temp_array = []
    for player in players:
        temp_array.append(player.id)
    temp_array *= 2

    index = temp_array.index(lwr)
    temp_array = temp_array[index:]
    index = temp_array.index(lwr, 1)
    temp_array = temp_array[:index]

    bar_check = []
    for i in temp_array:
        if players[i].status == True:
            bar_check.append(i)

    activity_check = []
    for i in temp_array:
        if players[i].status == True:
            activity_check.append(i)

    if max_raise == 0:
        bar_check[0] = 'unavailable'
    elif max_raise > 0:
        bar_check[0], bar_check[1] = 'unavailable', 'unavailable'
        activity_check[0] = 'unavailable'
    elif max_raise == -1:
        activity_check[0] = 'unavailable'

    # gui.error(window, f"{players[lwr].name} is last who raised, max_raise={max_raise}")
    #
    # bar_names = []
    # for i in bar_check:
    #     if i != 'unavailable':
    #         bar_names.append(players[i].name)
    # activity_names = []
    # for i in activity_check:
    #     if i != 'unavailable':
    #         activity_names.append(players[i].name)
    # gui.error(window, f"Bar_check: {bar_names}")
    # gui.error(window, f"Activity_check: {activity_names}")

    return bar_check, activity_check


def read_player_action(HandStats, i, active_enemies, window):
    players = HandStats['players_objects']
    actions = HandStats['actions']
    active_player_nb = HandStats['active_player_nb']
    game_pic = HandStats['game_pic']
    max_raise = HandStats['max_raise']
    pot = HandStats['pot']

    # gui.error(window, f"Currently reading {players[i].name}'s actions")

    current_action = []
    player_is_active = False
    # doing some checks to see if the player folded
    if players[i].name == 'You':
        my_cards, my_coords = image_processing.get_my_cards(game_pic)
        if my_coords:
            player_is_active = True
    else:
        if players[i].coords in active_enemies:
            player_is_active = True
        else:
            for coords in active_enemies:
                if image_processing.approx(players[i].coords[0], coords[0], players[i].coords[1], coords[1]):
                    player_is_active = True
                    break

    # if we cannot find them as actives, then we add to the actions that they folded
    if not player_is_active:
        active_player_nb -= 1
        players[i].set_status(False)

        current_action.append(i)
        current_action.append(players[i].name)
        current_action.append('f')  # f = 'fold'
        current_action.append(0)

    else:  # reading their money to see if it changed
        current_money = image_processing.read_money_at_coord(game_pic, players[i].coords, players[i].name, window)
        # a money value couldn't be correctly read, so we make a Falsey action
        if current_money == -1 or players[i].money == -1:
            current_action = [i, False, False, False]
            gui.error(window, f"Cannot calculate {players[i].name}'s action because one of the money values is 0")

        else:
            current_action.append(i)
            current_action.append(players[i].name)

            # if their money hasn't changed that means that they checked
            if current_money == players[i].money:
                current_action.append('ck')  # ck = 'check'
                current_action.append(0)

            elif current_money < players[i].money:
                raised_value = players[i].money - current_money
                # if the money difference is the same as the previous raise amount then the player called
                if raised_value <= max_raise:
                    current_action.append('cl')  # cl = 'call'
                    current_action.append(raised_value)
                    players[i].set_money(current_money)
                    pot += raised_value
                # if it's bigger than the previous raise then they raised
                elif raised_value > max_raise:
                    current_action.append('r')  # r = 'raise'
                    current_action.append(raised_value)
                    players[i].set_money(current_money)
                    pot += raised_value
                    max_raise = raised_value
                    HandStats['last_who_raised'] = i

            # some error happened
            elif current_money > players[i].money:
                current_action = [i, False, False, False]
                gui.error(window, f"{players[i].name} has more money than previously")

        players[i].set_money(current_money)  # updating players money
    # adding the current action aciton to the action array
    actions.append(app_functions.Action(current_action[0], current_action[1], current_action[2], current_action[3]))

    HandStats['players_objects'] = players
    HandStats['actions'] = actions
    HandStats['active_player_nb'] = active_player_nb
    HandStats['game_pic'] = game_pic
    HandStats['max_raise'] = max_raise
    HandStats['pot'] = pot

    if current_action[2] == 'r':
        return HandStats, True
    else:
        return HandStats, False


def get_hand_information(HandStats, active_id, window):
    # this function gets the HandStats variable which has all the information about our current hand, and the id
    # of the player who is currently in action based on this information, it will calculate the respective players'
    # actions, will put it in the HandStats variable, and it will return it

    HandStats['action_player_id'] = active_id  # the player who is currently in action

    # gets the table cards to see if a new round has started: preflop, flop, turn, river
    HandStats['table_cards'] = image_processing.get_table_cards(HandStats['game_pic'])
    if len(HandStats['table_cards']) > HandStats['prev_table_cards_nb'] and HandStats['action_player_id'] > 0:
        HandStats['prev_table_cards_nb'] = len(HandStats['table_cards'])

    # if the pot hasn't been read correctly then we read it again
    if HandStats['pot'] == -1:
        HandStats['pot'] = image_processing.readpot(HandStats['game_pic'], window)

    players = HandStats['players_objects']
    game_pic = HandStats['game_pic']
    bar_check = HandStats['bar_check']
    activity_check = HandStats['activity_check']

    # getting the active players to see if a player folded or not
    active_enemies = image_processing.find_enemies_coords(game_pic)

    # bar_names = []
    # for i in bar_check:
    #     if i != 'unavailable':
    #         bar_names.append(players[i].name)
    # activity_names = []
    # for i in activity_check:
    #     if i != 'unavailable':
    #         activity_names.append(players[i].name)
    # # gui.error(window, f"Bar_check: {bar_names}")
    # # gui.error(window, f"Activity_check: {activity_names}")

    if active_id in bar_check:
        # gui.error(window, f"{players[active_id].name} is in bar check")
        for i in range(len(bar_check)):
            if bar_check[i] == active_id:
                bar_check[i] = 'unavailable'
                break
            else:
                bar_check[i] = 'unavailable'

        for i in range(len(activity_check)):
            if activity_check[i] == active_id:
                break
            else:
                if activity_check[i] != 'unavailable':
                    HandStats, has_raised = read_player_action(HandStats, activity_check[i], active_enemies, window)
                    activity_check[i] = 'unavailable'
                    if has_raised:
                        HandStats['bar_check'], HandStats['activity_check'] = create_checking_arrays(HandStats, window)
                        break

    else:
        # gui.error(window, f"{players[active_id].name} not in bar check, creating arrays")
        for playerid in activity_check:
            if playerid != 'unavailable':
                HandStats, has_raised = read_player_action(HandStats, playerid, active_enemies, window)

        HandStats['max_raise'] = 0
        HandStats['last_who_raised'] = 0
        HandStats['bar_check'], HandStats['activity_check'] = create_checking_arrays(HandStats, window)

    players = HandStats['players_objects']
    bar_check = HandStats['bar_check']
    activity_check = HandStats['activity_check']
    # these are the players who do not fall into the first array, so we don't need to read actions for any of them
    currently_correcting = []
    for player in players:
        if player.id not in activity_check:
            currently_correcting.append(player.id)
    # and this means, that if our program previously read someone's information incorrectly, then it can correct itself
    for i in currently_correcting:
        if players[i].status == True:  # only checks the active players
            if players[i].name in ['Post SB', 'Post BB', 'Check', 'Call', 'Fold', 'Bet', '', '-unknown-']:
                players[i].set_name(image_processing.read_name_at_coord(game_pic, players[i].coords, window))
            if players[i].money == -1:
                players[i].set_money(image_processing.read_money_at_coord(game_pic, players[i].coords, players[i].name,
                                                                          window))

    HandStats['bar_check'] = bar_check
    HandStats['activity_check'] = activity_check
    HandStats['players_objects'] = players

    return HandStats
