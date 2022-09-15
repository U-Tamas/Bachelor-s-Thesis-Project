# this file is used to only run a single function, which we don't need for every startup of our main program
# this file is not imported anywhere
import cv2 as cv
import os
import string
import globals
import time

# these 3 functions get some pre-screenshoted cards, processes them, saves them in a folder, so the main application
# can use these saved pictures later on
# ideally we will not need to use these functions anymore, but I saved it, because you never know when you might need it

# processes the ranks of the cards
def ranker():
    project_dir = globals.project_dir
    loadpath =  f'{project_dir}/images/pokerstars/ranks_originals'
    save_path =  f'{project_dir}/images/pokerstars/ranks'
    for file in os.listdir(loadpath):
        if file.endswith('.jpg'):
            picture = cv.imread(f'{loadpath}/{file}')
            gray = cv.cvtColor(picture, cv.COLOR_BGR2GRAY)
            blur = cv.GaussianBlur(gray, (5, 5), 0)

            retval, thresh = cv.threshold(blur, 230, 255, cv.THRESH_BINARY)

            contours, hierarchy = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            # thresh = cv.drawContours(picture, contours, -1, (0, 255, 75), 2)

            for contour in contours:
                x, y, width, height = cv.boundingRect(contour)
                height = height // 2
                if 80 <= width <= 85 and 55 <= height <= 60:
                    my_card = gray[y : y+int(height*0.6), x : x+(width - height)]

                    retval, thresh = cv.threshold(my_card, 150, 255, cv.THRESH_BINARY)
                    thresh = cv.bitwise_not(thresh)
                    contours, hierarchy = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

                    if len(contours) == 0:
                        return False
                    elif len(contours) == 1:
                        x0, y0, width0, height0 = cv.boundingRect(contours[0])
                    else:
                        x0, y0, width0, height0 = cv.boundingRect(contours[0])
                        x1, y1, width1, height1 = cv.boundingRect(contours[1])
                        if width1 > width0:
                            x0, y0, width0, height0 = x1, y1, width1, height1

                    my_card = thresh[y0: y0 + height0, x0: x0 + width0]

                    cv.imwrite(f'{save_path}/{file}', my_card)


# processes the suits of the cards
def suiter():
    project_dir = globals.project_dir
    loadpath = f'{project_dir}/images/pokerstars/suits_originals'
    save_path = f'{project_dir}/images/pokerstars/suits'
    for file in os.listdir(loadpath):
        if file.endswith('.jpg'):
            picture = cv.imread(f'{loadpath}/{file}')
            gray = cv.cvtColor(picture, cv.COLOR_BGR2GRAY)
            blur = cv.GaussianBlur(gray, (5, 5), 0)

            retval, thresh = cv.threshold(blur, 230, 255, cv.THRESH_BINARY)

            contours, hierarchy = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            # thresh = cv.drawContours(picture, contours, -1, (0, 255, 75), 2)
            # cv.imshow('pic', picture)

            for contour in contours:
                x, y, width, height = cv.boundingRect(contour)
                height //= 2
                if 80 <= width <= 85 and  55 <= height <= 60:
                    my_card = gray[y+int(height*0.6) : y+int(height*0.9), x : x+(width-height)]

                    retval, thresh = cv.threshold(my_card, 150, 255, cv.THRESH_BINARY)
                    thresh = cv.bitwise_not(thresh)
                    contours, hierarchy = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

                    x, y, width, height = cv.boundingRect(contours[0])

                    my_card = thresh[y : y+height, x : x+width]

                    cv.imwrite(f'{save_path}/{file}', my_card)


def defenemy():
    # megtalalja az enemy kartyakat, s kiolvassa alattuk a penzeket
    enemy_path = f'{project_dir}/images/pokerstars/enemy1.jpg'
    picture = cv.imread(enemy_path)
    possible_first = False

    # getting the top and bottom cut out
    gray = cv.cvtColor(picture, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (5, 5), 0)

    threshvalue = 170

    retval, thresh = cv.threshold(blur, threshvalue, 255, cv.THRESH_BINARY)
    cv.imshow('alap', thresh)

    contours, hierarchy = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cv.drawContours(picture, contours, -1, (0, 255, 0), 3)
    cv.imshow('konturok', picture)
    print(len(contours))

    for contour in contours:
        x, y, width, height = cv.boundingRect(contour)
        print(width, height)
        if int(height*2.7) <= width <= int(height*2.9):
            if possible_first == False:
                possible_first = True
                temp_right_limit = right_limit
            elif possible_first == True:
                picture = thresh[upper_limit:lower_limit, left_limit:temp_right_limit]

                cv.imshow('vegso', picture)
                cv.imwrite(enemy_path, picture)


# path = os.path.abspath(os.sep)
# # print(path)


def search():
    start_time = time.time()
    available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]

    for drive in available_drives:
        first_dirs = os.listdir(f"{drive}/")
        if 'Tesseract-OCR' in first_dirs:
            return f"{drive}/Tesseract-OCR/tesseract"
        else:
            for fdir in first_dirs:
                try:
                    second_dirs = os.listdir(f"{drive}/{fdir}")
                    if 'Tesseract-OCR' in second_dirs:
                        return f"{drive}/{fdir}/Tesseract-OCR/tesseract"
                    else:
                        for sdir in second_dirs:
                            try:
                                third_dirs = os.listdir(f"{drive}/{fdir}/{sdir}")
                                if 'Tesseract-OCR' in third_dirs:
                                    return f"{drive}/{fdir}/{sdir}/Tesseract-OCR/tesseract"
                            except:
                                pass
                except:
                    pass

        # for root, dirs, files in os.walk(drive):
        #     if 'Tesseract-OCR' in dirs:
        #         pass

        print(time.time() - start_time)


# tesspath = search()
# print(tesspath)

suiter()
