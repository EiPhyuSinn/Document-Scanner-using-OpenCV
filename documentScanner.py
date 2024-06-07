import cv2 as cv 
import numpy as np 

capture = cv.VideoCapture(0)
capture.set(3,640)
capture.set(4,480)
capture.set(10,130)

def preprocessing(img):
    img = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    gray = cv.GaussianBlur(img,(5,5),1)
    canny = cv.Canny(gray,200,200)
    kernel = np.ones((5,5))
    dial = cv.dilate(canny,kernel,iterations=2)
    imgThres = cv.erode(dial,kernel,iterations=1)
    return imgThres

def getContours(img):
    biggest = np.array([])
    maxArea = 0
    x,y,w= 0,0,0
    contours, hierarchy = cv.findContours(img,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv.contourArea(cnt)
        if area>5000:
            # cv.drawContours(imgContour,cnt,-1,(0,255,0),3)
            peri = cv.arcLength(cnt,True)
            approx = cv.approxPolyDP(cnt,0.02*peri,True)
            if area>maxArea and len(approx) == 4:
                biggest = approx
                maxArea = area
    cv.drawContours(imgContour,biggest ,-1,(0,255,0),20)
    return biggest

def reorder(myPoints):
    myPoints = myPoints.reshape((4,2))
    myPointsNew = np.zeros((4,1,2),np.int32)
    add = myPoints.sum(1)
    myPointsNew[0] = myPoints[np.argmin(add)]
    myPointsNew[3] = myPoints[np.argmax(add)]
    diff = np.diff(myPoints,axis=1)
    myPointsNew[1] = myPoints[np.argmin(add)]
    myPointsNew[2] = myPoints[np.argmax(add)]

def getWarp(img,biggest):
    biggest = reorder(biggest)
    pts1 = np.float32(biggest)
    pts2 = np.float32([
        [0, 0],    # Top-left
        [250, 0],  # Top-right
        [0, 400],  # Bottom-left
        [250, 400] # Bottom-right
    ])
    matrix = cv.getPerspectiveTransform(pts1, pts2)
    result = cv.warpPerspective(img, matrix, (250, 400))


while True:
    success,frame = capture.read()
    img = cv.resize(frame,(640,480))
    imgContour = img.copy()
    imgThres = preprocessing(img)
    biggest = getContours(imgThres)
    print(biggest)
    imgWrap = getWarp(img,biggest)
    cv.imshow("Video",imgWrap)
    if cv.waitKey(1) & 0xFF == 27:
        break

