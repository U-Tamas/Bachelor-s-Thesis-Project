# # this is purely a testing file, it is not used anywhere
# # i use this to write and test out different funcitons
#
import cv2 as cv

pic = cv.imread(r"C:\Users\ujlak\Desktop\PROIECT\Ujlaki Tamas proiect licenta\images\pokerstars\button.jpg")
gray = cv.cvtColor(pic, cv.COLOR_BGR2GRAY)
retval, thresh = cv.threshold(pic, 100, 255, cv.THRESH_BINARY)
print(thresh[0])
print(thresh.shape)