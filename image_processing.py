import cv2 as cv
from pyautogui import screenshot
import pytesseract
import numpy as np
import os
import time
# my files:
import globals
import app_functions
import gui


def approx(val1, val2, val3, val4):
    # returns true if value1 is approximately equal to value2, and the same for val3 and val4
    if (int(val1 * 0.8) <= val2 <= int(val1 * 1.2)) and (int(val3 * 0.8) <= val4 <= int(val3 * 1.2)):
        return True
    else:
        return False


def difference(image0, image1):
    # tells the difference between the two images which it gets
    # both the images need to be black and white
    if len(image0.shape) == 3:  # a color picture's shape is (height, width, rgb), for b&w it's (height, width)
        image0 = cv.cvtColor(image0, cv.COLOR_BGR2GRAY)
    if len(image1.shape) == 3:
        image1 = cv.cvtColor(image1, cv.COLOR_BGR2GRAY)

    # resizes one of the images to the other's sizes, so the comparation can be done
    image0 = cv.resize(image0, (image1.shape[1], image1.shape[0]))

    # we calculate how many pixels does a picture have, so that we can get a universal final result for both small
    # and large images
    pixels = image0.shape[0] * image0.shape[1]
    diff = int(np.sum(cv.absdiff(image0, image1)) / pixels)  # sum(absdiff) says how many pixels are different

    return diff


def whatcard(card_image):
    # gets and image of a card, and returns what card  it is (ex: 'ace_of_spades')
    height = card_image.shape[0]
    width = card_image.shape[1]

    suits = np.zeros(4)
    suitsnames = ['clubs', 'diamonds', 'hearts', 'spades']

    # getting exactly that part of the card where it's suit is located
    card = card_image[int(height * 0.6): int(height * 0.9), 0: (width - height)]
    # making the card to have only completely black and white pixels
    retval, thresh = cv.threshold(card, 150, 255, cv.THRESH_BINARY)
    # inverting these pixels, so we can find the suit's contours
    thresh = cv.bitwise_not(thresh)
    contours, hierarchy = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    try:
        x, y, width1, height1 = cv.boundingRect(contours[0])
    except:
        # no contour has been found, so the image cannot be a card
        return False
    card = thresh[y: y + height1, x: x + width1]

    # calculating to which predefined image is ours most similar to
    i = 0
    for file in os.listdir(globals.suits_path):
        if file.endswith('.jpg'):
            suit = cv.imread(f'{globals.suits_path}/{file}')
            diff = difference(suit, card)
            suits[i] = diff
            i += 1

    # if the difference is too big for any of the predefined images then we can conclude that the image this function
    # got is not a card
    if np.min(suits) > 70:
        return False

    # we do the exact same thing with the cards rank
    ranks = np.zeros(13)
    ranksnames = ['10', '2', '3', '4', '5', '6', '7', '8', '9', 'ace', 'jack', 'king', 'queen']

    card = card_image[0: int(height * 0.6), 0: (width - height)]
    retval, thresh = cv.threshold(card, 150, 255, cv.THRESH_BINARY)
    thresh = cv.bitwise_not(thresh)
    contours, hierarchy = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return False
    elif len(contours) == 1:
        x0, y0, width0, height0 = cv.boundingRect(contours[0])
    else:
        # we only make this difference, because if the number on the card is 10, then we have 2 different contours
        # that we can get, and we want to find the '0'
        x0, y0, width0, height0 = cv.boundingRect(contours[0])
        x1, y1, width1, height1 = cv.boundingRect(contours[1])
        if width1 > width0:  # the contour of the '0' is wider than the '1'
            x0, y0, width0, height0 = x1, y1, width1, height1

    card = thresh[y0: y0 + height0, x0: x0 + width0]

    i = 0
    for file in os.listdir(globals.ranks_path):
        if file.endswith('.jpg'):
            rank = cv.imread(f'{globals.ranks_path}/{file}')
            ranks[i] = difference(rank, card)
            i += 1

    if np.min(ranks) > 70:
        return False

    card_rank = ranksnames[np.argmin(ranks)]
    card_suit = suitsnames[np.argmin(suits)]

    return f'{card_rank}_of_{card_suit}'


def get_my_cards(picture):
    # gets the poker game's currnet image, and returns what cards you have, and their coordinates
    my_card_width = globals.interface['my_card_width']  # we will only look for objects with these dimensions
    my_card_height = globals.interface['my_card_height']

    # gets the contours of our image, to which we are applying GaussianBlur = 3 and Threshold = 230
    contours, gray = getcontours(picture, 3, 230)

    my_cards = []
    for contour in contours:
        x, y, width, height = cv.boundingRect(contour)

        if approx(width, my_card_width, height, my_card_height):  # if the current contour dimensions are correct
            my_card = gray[y: y + height, x: x + width]  # we cut out the little card image
            my_card = whatcard(my_card)  # and check what card is it
            if my_card:
                my_cards.append(my_card)
                my_x, my_y = x, y  # saves the coordinates where they are

    if len(my_cards) == 2:  # they can only appear in pairs
        my_cards = my_cards[::-1]  # we need to reverse them because they have been read in the wrong order
        return my_cards, [my_x, my_y]  # returns the cards, and their coordinates
    return [], []  # if they are not in pairs, there is a problem, so we return empty arrays


def get_table_cards(picture):
    # gets the poker game's currnet image, and returns the table cards
    my_card_width = globals.interface['my_card_width']  # we will only look for objects with these dimensions
    my_card_height = globals.interface['my_card_height']

    # gets the contours of our image, to which we are applying GaussianBlur = 3 and Threshold = 230
    contours, gray = getcontours(picture, 3, 230)

    table_cards = []

    # when we read the contours, the reading starts from the bottom right of the image, and for our table cards
    # to be in the right order when we read them, we need to reverse them
    revcon = reversed(contours)
    contours = tuple(revcon)
    for contour in contours:
        x, y, width, height = cv.boundingRect(contour)

        if approx(width, my_card_width, height, my_card_height * 2):  # if the current contour dimensions are correct
            card = gray[y: y + my_card_height, x: x + my_card_width]  # we cut out the little card image
            card = whatcard(card)  # and check what card is it
            if card:
                table_cards.append(card)

    return table_cards


def findbutton(picture, *args):
    # this function gets the game's picture and returns either the button's size, or it's location
    # this depends whether the size was already initialized or not

    # only gets args if we want to initialize the button's width and height
    # if we don't get args that means that we need the button's location
    if len(args) > 0:
        button_width = args[0]
        button_height = args[1]
    else:
        button_width = globals.interface['button_width']
        button_height = globals.interface['button_height']

    # gets the contours of our image, to which we are applying GaussianBlur = 1(None) and Threshold = 190
    contours, gray = getcontours(picture, 1, 190)

    for contour in contours:
        x, y, width, height = cv.boundingRect(contour)
        # if the contour's sizes are correct, we are going to check it against a predefined image to see if it is
        # similar enough
        if approx(height, button_height, width, button_width):
            picture = gray[y: y + height, x: x + width]  # cutting out our image
            button_picture = cv.imread(globals.button_path)  # predefined image
            diff = difference(button_picture, picture)  # difference between them
            if diff < 20:
                if len(args) > 0:
                    return [width, height]
                else:
                    return [x, y]

    return False


def find_enemies_coords(picture, *args):
    # gets the current game picture, and returns either an enemy player's sizes, or all of the enemy players coordinates
    # on the image

    # only gets args if we want to initialize an enemy player's width and height
    # if we don't get args that means that we need every players' location
    if len(args) > 0:
        enemy_width = args[0]
        enemy_height = args[1]
    else:
        enemy_width = globals.interface['enemy_width']
        enemy_height = globals.interface['enemy_height']

    # because the enemy players' cards are in pairs, we need to find both of them near each other
    possible_first = False
    enemy_locations = []

    # gets the contours of our image, to which we are applying GaussianBlur = 1(None) and Threshold = 190
    contours, gray = getcontours(picture, 1, 190)

    for contour in contours:
        x, y, width, height = cv.boundingRect(contour)
        # if the contour's sizes are correct, we might have found a card pairs' first card
        if approx(width, enemy_width, height, enemy_height):
            if not possible_first:
                possible_first = True
                temp_right_limit = x + width  # we save their place to know if they are near each other
                temp_width = width
                temp_height = height

            # if one has been found, the other has approximately the same size, and is near it
            elif possible_first and approx(width, temp_width, height, temp_height) and (temp_right_limit > x):
                picture = gray[y: y + height, x: temp_right_limit]  # then we cut out a little picture
                enemy_picture = cv.imread(globals.enemy_path)  # get a predefined one
                diff = difference(enemy_picture, picture)  # look at the difference between them
                if diff < 20:
                    # if the difference is small, then we have found a player, and save their size and location
                    enemy_locations.append([x, y])
                    final_width, final_height = width, height
                possible_first = False
                temp_height, temp_width = -10, -10  # security measure
            else:
                possible_first = False
                temp_height, temp_width = -10, -10

    if len(args) > 0:
        # this means our application is in the initialization phase, so we return the sizes
        try:
            return [final_width, final_height]  # this will get an error if no enemy has been found
        except:
            return False
    else:
        return enemy_locations


def get_initial_picture():
    # makes a screenshot, and returns it's left half
    test = r'C:\Users\ujlak\Desktop\PROIECT\testpic1.jpg'
    # you can change this variable manually to make the reading from this source in cv.imread(...)
    # I used this speciific picture for testing

    screenshot(globals.screenshotpath)
    game_pic = cv.imread(globals.screenshotpath)  # reads in an image
    game_pic = game_pic[0:game_pic.shape[0], 0:(game_pic.shape[1] // 2)]  # cuts out the right half

    return game_pic


def getcontours(picture, blur_value, thresh_value):
    # gets an image, how much to blur it, and at what threshold to transform it, and returns the contours on the image
    gray = cv.cvtColor(picture, cv.COLOR_BGR2GRAY)  # making it b&w
    blur = cv.GaussianBlur(gray, (blur_value, blur_value), 0)  # applying blur
    retval, thresh = cv.threshold(blur, thresh_value, 255, cv.THRESH_BINARY)  # thresholding it
    contours, hierarchy = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    return contours, gray


def get_game_stats(image, window):
    # this function gets the game image, and the ui window
    # the ui window is here, so we can pass some error messages to it
    # this function determines:
    #   -the poker application's upper bar coordinates and sizes
    #   -the poker application's chat coordinates and sizes
    #   -the poker application's upper bar coordinates and sizes
    #   -yours and enemy cards' sizes, button size

    interface = globals.interface  # to later make namings shorter

    # gets the contours of our image, to which we are applying GaussianBlur = 1(None) and Threshold = 190
    contours, gray = getcontours(image, 1, 190)

    # finding the poker application's upper bar and chat window
    app_bar_found = False
    chat_found = False
    contours = contours[::-1]  # we reverse the contours to start from the top
    for contour in contours:
        x, y, width, height = cv.boundingRect(contour)

        if width > 300 and height < (width // 10):
            # these should be the dimensions of an application bar
            # so we check if the little icon  in the app bar matches the Pokerstars logo
            app_icon = gray[y: y + height, x: x + height]  # cutting out the image
            original_icon = cv.imread(globals.icon_path)  # getting the logo from our files
            if difference(original_icon, app_icon) < 20:  # if the difference is small enough, we save these infos
                app_bar_found = True
                app_bar_coords = (x, y)
                app_bar_width = width
                app_bar_height = height

        if app_bar_found and (width > app_bar_width // 3) and (height > width // 6):
            # once the app bar has been found, and we find objects which match our desired dimensions
            chat_found = True  # we save the data about the chat
            chat_coords = (x, y)
            chat_width = width
            chat_height = height
            break

    # we must find every component, so we return if we don't
    if not app_bar_found:
        gui.error(window, "Application window was not found in the initial mapping")  # error message
        return False
    app_bar_pic = gray[app_bar_coords[1]: app_bar_coords[1] + app_bar_height,  # the picture of our app bar
                       app_bar_coords[0]: app_bar_coords[0] + app_bar_width]
    interface["app_bar_pic"] = app_bar_pic  # we start writing data in our global data holder
    interface["app_bar_coords"] = app_bar_coords
    interface["app_bar_width"] = app_bar_width
    interface["app_bar_height"] = app_bar_height

    if not chat_found:
        gui.error(window, "Chat was not found in the initial mapping")  # error message
        return False
    interface["chat_coords"] = chat_coords
    interface["chat_width"] = chat_width
    interface["chat_height"] = chat_height

    # now we cut out the screenshot, so we only have the place between the upper app bar and the chat
    # every action is going to happen here in this space
    image = image[(app_bar_coords[1] + app_bar_height): (chat_coords[1]),
                  (app_bar_coords[0]): (app_bar_coords[0] + app_bar_width)]

    # gettin the contours again, now for our new smaller image
    contours, gray = getcontours(image, 1, 190)

    # finding my_card sizes
    found_a_card = False
    for contour in contours:
        x, y, width, height = cv.boundingRect(contour)
        # i have measured that on pokerstars the cards have the below dimensions when compared to the application's bar
        if (app_bar_width // 20 < width < app_bar_width // 17) and (width // 1.5 < height < width // 1.3):
            card = gray[y: y + height, x: x + width]  # cutting out the little images
            if whatcard(card):  # finding out if they are indeed a card or not
                found_a_card = True
                my_card_width = width
                my_card_height = height
                break

    if not found_a_card:
        gui.error(window, "Your cards were not found in the initial mapping")
        return False
    interface["my_card_width"] = my_card_width
    interface["my_card_height"] = my_card_height

    # we know that for pokerstars, the enemy cards are as wide as my cards, and have half the height
    enemy_sizes = find_enemies_coords(image, interface['my_card_width'], interface['my_card_height'] // 2)
    if not enemy_sizes:
        gui.error(window, "No enemy cards found in the initial mapping")
        return False
    interface["enemy_width"] = enemy_sizes[0]
    interface["enemy_height"] = enemy_sizes[1]

    # we know that the button's height is approximately as big as an enemy card's height, and the width should be
    # height*1.35
    button_sizes = findbutton(image, int(interface["enemy_height"] * 1.35), interface["enemy_height"])
    if not button_sizes:
        gui.error(window, "No button found in the initial mapping")
        return False
    interface["button_width"] = button_sizes[0]
    interface["button_height"] = button_sizes[1]

    return True  # everything has been found and documented


def check_if_moved(half_screen):
    # gets half a screenshot, and returns if the poker application has been moved or resized
    i = globals.interface
    current_app_bar = half_screen[(i['app_bar_coords'][1]): (i['app_bar_coords'][1] + i['app_bar_height']),
                                  (i['app_bar_coords'][0]): (i['app_bar_coords'][0] + i['app_bar_width'])]
    # [upper : lower, left : right]

    # checking the difference between our initialized Pokerstars application bar, and the same part of our screenshot
    if difference(current_app_bar, i["app_bar_pic"]) == 0:
        # cuts out the game's part of the screenshot and the chat part of the screenshot, and returns them
        game_pic = half_screen[(i['app_bar_coords'][1] + i['app_bar_height']): (i['chat_coords'][1]),
                               (i['app_bar_coords'][0]): (i['app_bar_coords'][0] + i['app_bar_width'])]

        chat_pic = half_screen[(i['chat_coords'][1]): (i['chat_coords'][1] + i['chat_height']),
                               (i['chat_coords'][0]): (i['chat_coords'][0] + i['chat_width'])]
        return game_pic, chat_pic

    else:
        return False


def read_name_at_coord(picture, coord, window):
    # gets the current game picture, and a player's coordinates, to read and return what is the name of that player
    # we also get 'window' to be able to put error messages in it
    if len(coord) == 2:  # coord=[x,y]
        separating_value = (picture.shape[0] + picture.shape[1]) // 2
        # this is a diagonal across our playing field, because if a player is on the left of this diagonal then
        # his relative coordinates will be different from a player's relative coordinates on the right
        if coord[0] + coord[1] < separating_value:
            coord.append('left')
            coord.append(False)  # we add false because we never need to read Your name
        else:
            coord.append('right')
            coord.append(False)

    # coord=[x,y, left/right, You/notYou]

    # if the coord was already long enough, and we didn't put False in it, and this respective value is True,
    # that means we don't need to read any name
    if coord[3]:
        return 'You'

    width = globals.interface['enemy_width']
    height = globals.interface['enemy_height']
    # calculating different left and right limits for our player
    if coord[2] == 'left':
        left = (coord[0] - (width // 2))
        right = (coord[0] + int(width * 1.5))
    elif coord[2] == 'right':
        left = (coord[0] + int(width * 0.4))
        right = (coord[0] + int(width * 2.5))
    upper = (coord[1] + height) + int(height // 2.1)
    lower = (coord[1] + height) + int(height * 1.5)

    picture = picture[upper:lower, left:right]  # cutting out the picture so we only have the name part

    # manipulating our image a bit, so that Pytesseract will be able to read it better
    gray = cv.cvtColor(picture, cv.COLOR_BGR2GRAY)
    gray = cv.resize(gray, (gray.shape[1] * 5, gray.shape[0] * 5))
    retval, thresh = cv.threshold(gray, 130, 255, cv.THRESH_BINARY)
    thresh = cv.bitwise_not(thresh)

    # cv.imshow('readname', thresh)

    name = pytesseract.image_to_string(thresh)  # pytesseract reads the text from the little image
    name = name.split('\n')[0]  # i don't know why but tesseract puts '\n' at the ending of the name

    if name == '':
        # saves the picture, so we can look at it, to see what's wrong
        cv.imwrite(f'{globals.errors_path}/name_error.jpg', thresh)
        gui.error(window, "A name was not found")  # error message
        name = '-unknown-'  # if we haven't found a name, this is our default

    return name


def read_money_at_coord(picture, coords, name, window):
    # this function gets the game picture, the coordinates and name of the player whose money we want to read
    # it also gets the 'window', so we can output an error message
    # it will return the money value of the player
    # because your cards are taller than the enemy cards, we need to calculate different upper and lower limits
    if name == 'You':
        height = globals.interface['my_card_height']
        width = globals.interface['my_card_width']
    else:
        width = globals.interface['enemy_width']
        height = globals.interface['enemy_height']
    upper = (coords[1] + height) + int(width / 1.7)
    lower = (coords[1] + height) + int(width * 1.05)

    separating_value = (picture.shape[0] + picture.shape[1]) // 2
    # this is a diagonal across our playing field, because if a player is on the left of this diagonal then
    # his relative coordinates will be different from a player's relative coordinates on the right

    if coords[0] + coords[1] < separating_value:
        # the player is on the left side of the game screen divided by the diagonal
        left = (coords[0] - (width // 4))
        right = (coords[0] + int(width * 1.5))
    else:
        # the player is on the right side of the game screen divided by the diagonal
        left = (coords[0] + int(width // 2))
        right = (coords[0] + int(width * 2.2))

    picture = picture[upper:lower, left:right]  # cutting out the picture so we only have the name part

    # manipulating our image a bit, so that Pytesseract will be able to read it better
    gray = cv.cvtColor(picture, cv.COLOR_BGR2GRAY)
    gray = cv.resize(gray, (gray.shape[1] * 5, gray.shape[0] * 5))
    retval, thresh = cv.threshold(gray, 110, 255, cv.THRESH_BINARY)
    thresh = cv.bitwise_not(thresh)

    text = pytesseract.image_to_string(thresh)  # pytesseract reads the text from the little image

    money_value = ''
    for char in text:
        if char.isdigit():
            money_value += char  # we are only interested in digits

    if text.startswith('A'):  # ='All-In'
        money_value = 0

    if money_value != '':
        return int(money_value)
    else:
        cv.imwrite(f'{globals.errors_path}/money_error.jpg', thresh)  # saving the error image
        gui.error(window, f"Cloudn't read the money for {name}")  # output error message
        return -1


def readpot(picture, window):
    # gets the cut picture from pokerstars, reads and returns the pot value
    # we get 'window' so we can output error messages
    height = picture.shape[0]
    width = picture.shape[1]
    val = height // 100
    picture = picture[height // 3 + val: height // 3 + (val * 6),
                      width // 2 - (val * 8): width // 2 + (val * 8)]  # trial and error values
    # we cut out the little place where we can find the pot

    # manipulating our image a bit, so that Pytesseract will be able to read it better
    gray = cv.cvtColor(picture, cv.COLOR_BGR2GRAY)
    gray = cv.resize(gray, (gray.shape[1] * 5, gray.shape[0] * 5))
    retval, thresh = cv.threshold(gray, 120, 255, cv.THRESH_BINARY)
    thresh = cv.bitwise_not(thresh)

    text = pytesseract.image_to_string(thresh)  # pytesseract reads the text from the little image
    money_value = ''
    for char in text:
        if char.isdigit():
            money_value += char  # we are only interested in digits

    if money_value != '':
        return int(money_value)
    else:
        cv.imwrite(f'{globals.errors_path}/pot_error.jpg', thresh)  # saving the error image
        gui.error(window, f"Cloudn't read the pot")  # outpput the error message
        return -1


def button_at_player(players_objects, button_location):
    # gets players, and the button's coords, and returns which player is the closest to it
    button_distance = []

    # calculates the button's distance to each player
    for player in players_objects:
        x_val = player.coords[0]
        y_val = player.coords[1]

        distance0 = button_location[0] - x_val
        if distance0 < 0:
            distance0 *= (-1)  # we can't have negative distances

        distance1 = button_location[1] - y_val
        if distance1 < 0:
            distance1 *= (-1)
        button_distance.append(distance0 + distance1)

    # sees which player has the least distance to the button and returns them
    return button_distance.index(min(button_distance))


def find_visual_cue(HandStats, window):
    # this function gets HandStats = every information about the current hand, and 'window' so we can print errors in it
    # this function finds a viual cue which represents which player is currently in action, and returns their id

    # manipulating our current image, to make it have only fully black and white pixels
    gray = cv.cvtColor(HandStats['game_pic'], cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (11, 11), 0)
    retval, current_thresh = cv.threshold(blur, 60, 255, cv.THRESH_BINARY)

    # manipulating our last image, so we will be able to compare them
    gray = cv.cvtColor(HandStats['prev_pic'], cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (11, 11), 0)
    retval, prev_thresh = cv.threshold(blur, 60, 255, cv.THRESH_BINARY)

    pixels = current_thresh.shape[0] * current_thresh.shape[1]
    try:
        diff = (np.sum(cv.absdiff(current_thresh, prev_thresh)) / pixels)  # comparing the 2 images
    except:
        return None, HandStats
    if diff <= 2.3:
        return None, HandStats
    # if in error comes up, or there isn't any difference, then we return

    players = HandStats['players_objects']
    game_pic = HandStats['game_pic']
    enemy_width = globals.interface['enemy_width']
    enemy_height = globals.interface['enemy_height']
    my_card_width = globals.interface['my_card_width']
    my_card_height = globals.interface['my_card_height']

    # if there was a difference, then we look at which player has the green bar which indicates that it's his turn
    for player in players:
        if player.status == True:
            if player.name == 'You':
                height = my_card_height
                width = my_card_width
            else:
                height = enemy_height
                width = enemy_width

            # determining the area where the current player's green bar should be
            upper = (player.coords[1] + height) + int(width * 1.2)
            lower = (player.coords[1] + height) + int(width * 1.3)
            left = (player.coords[0] - int(width // 10))
            right = (player.coords[0] + int(width * 1.2))
            green_bar = game_pic[upper:lower, left:right]   # cutting out the area

            # checking if the green bar is in the area
            gray = cv.cvtColor(green_bar, cv.COLOR_BGR2GRAY)  # making it b&w
            blur = cv.GaussianBlur(gray, (3, 3), 0)  # applying blur
            retval, thresh = cv.threshold(blur, 100, 255, cv.THRESH_BINARY)  # thresholding it
            # we threshold the pixels from the selected area in a way that every green pixel from the area becomes white
            white_pixels = cv.countNonZero(thresh)
            total_pixels = thresh.shape[0] * thresh.shape[1]
            # if the area contains at least 80% white pixels, then we can confirm that the current player is in action
            if white_pixels / total_pixels > 0.8:
                # gui.error(window, f"\n{player.name} is in action")
                # changes the current pic, so that in the next read loop we can compare its current to this
                HandStats['prev_pic'] = HandStats['game_pic']
                return player.id, HandStats

    # if we cannot find the active player, we return None for the id
    return None, HandStats


def read_new_hand(game_pic, button_location, window):
    # This function gets the game's picture, the location of the button, and makes and returns an array that contains
    # the players' objects. It also reads and returns what cards you have, what cards are on the talbe, and the pot
    # Also returns the game's and chat's pictures We use 'window' for error messages

    # we read the pot from the game's picture
    pot = readpot(game_pic, window)

    # the lines from here until my_cards, my_coords = ... are useless if we leave the time.sleep() commented out
    # I put in these code lines, because this was the way that I was doing the reading, but have since found another
    # solution for the problem which time.sleep() was trying to solve
    # I just leave it here like this, so if I go back to utilizing the previous method, than it can be easily done
    time.sleep(0.5)
    half_screen = get_initial_picture()
    initialized = True

    try:
        game_pic, chat_pic = check_if_moved(half_screen)
    except:
        initialized = False
        return initialized

    # getting all the cards
    my_cards, my_coords = get_my_cards(game_pic)
    table_cards = get_table_cards(game_pic)

    # if we don't have 2 cards then something is not right, so we cannot procede
    if len(my_cards) != 2:
        return initialized

    players_coords = find_enemies_coords(game_pic)
    # if there are no enemies, then something else is not right
    if len(players_coords) == 0:
        return initialized

    # because pokerstars's players objects have 2 directions, pointing at either left or right,
    # we will calculate a line to separate them
    # we append to the coords the direction they are facing, and False because they enemy players, not you
    separating_value = (game_pic.shape[0] + game_pic.shape[1]) // 2
    for coord in players_coords:
        if coord[0] + coord[1] < separating_value:
            coord.append('left')
            coord.append(False)
        else:
            coord.append('right')
            coord.append(False)

    # we append the way your player object is facing, and True because you are the 'You' player
    my_x, my_y = my_coords
    if (my_x + my_y) < separating_value:
        players_coords.append([my_x, my_y, 'left', True])
    else:
        players_coords.append([my_x, my_y, 'right', True])

    # for every coordinate which we have, we will read and append their name and mooney value
    for coord in players_coords:
        coord.append(read_name_at_coord(game_pic, coord, window))
        coord.append(read_money_at_coord(game_pic, [coord[0], coord[1]], coord[4], window))

    # we need to sort the players to be in clockwise order, just like in real life
    # we separate them in 2 different arrays, based on what direction they are facing
    # in the new arrays we will put the Y coordinates, because sorting them gives us the order we want
    left_side, right_side = [], []
    for coord in players_coords:
        if coord[2] == 'left':
            left_side.append(coord[1])
        else:
            right_side.append(coord[1])
    left_side.sort(reverse=True)
    right_side.sort()

    # after the sorting is done, we go through the sorted arrays, and if the coordinates match to a player's coords
    # then we put that player in our final sorted array
    new_combined = []
    for y in left_side:
        for coord in players_coords:
            if (coord[1] == y) and (coord[2] == 'left'):
                new_combined.append(coord)
    for y in right_side:
        for coord in players_coords:
            if (coord[1] == y) and (coord[2] == 'right'):
                new_combined.append(coord)

    # for every player we create a Player object, and put it in our players_objects array
    # every Player object contains the id, coords, name, money, and status
    players_objects = []
    for i in range(len(new_combined)):
        players_objects.append(app_functions.Player(i, [new_combined[i][0], new_combined[i][1]], new_combined[i][4],
                                                    new_combined[i][5]))

    # we calculate which player has the button
    button_player_id = button_at_player(players_objects, button_location)

    # we will sort out players_objects one last time, so that the player with the button will be on the last position
    # and the small and big blinds will be first and second
    temp_array = []
    for i in range(button_player_id + 1, len(players_objects)):
        temp_array.append(players_objects[i])

    for i in range(0, button_player_id + 1):
        temp_array.append(players_objects[i])

    for i in range(len(temp_array)):
        temp_array[i].set_id(i)
    players_objects = temp_array

    return [game_pic, chat_pic, my_cards, table_cards, players_objects, pot]
