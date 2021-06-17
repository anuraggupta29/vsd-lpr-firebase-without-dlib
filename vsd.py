import cv2
import imutils
from position_tracker import PositionTracker
from datetime import datetime
from datetime import timedelta
import os
import numpy as np

#import the variables from data_list file
from data_list import overSpeedArr

#-----------------------------------------------------------------------

#function to clear portion of an image for faster processing
def blackout(image):
    xBlack = 360
    yBlack = 300
    triangle_cnt = None
    triangle_cnt2 = None

    triangle_cnt = np.array( [[0,0], [xBlack,0], [0,yBlack]] )
    triangle_cnt2 = np.array( [[resizeWidth,0], [resizeWidth-xBlack,0], [resizeWidth,yBlack]] )

    cv2.drawContours(image, [triangle_cnt], 0, (0,0,0), -1)
    cv2.drawContours(image, [triangle_cnt2], 0, (0,0,0), -1)
    #return image

#Function to save car image
def saveCarImage(speed,carImage):
    now = None
    nameCurTime = None
    link = None

    now = datetime.today().now()
    nameCurTime = now.strftime("%d-%m-%Y-%H-%M-%S-%f")

    #Make directory to store over-speeding car images
    if not os.path.exists('overspeeding/'):
        os.makedirs('overspeeding/')

    link = 'overspeeding/'+nameCurTime+'.jpeg'
    cv2.imwrite(link,carImage, [int(cv2.IMWRITE_JPEG_QUALITY), 70])

#Function to calculate speed
def estimateSpeed(carID):
    markGap = 50 #Distance in metres between the markers
    fpsFactor = 2 #To compensate for slow processing
    timeDiff = None
    speed = None

    timeDiff = (endTracker[carID]-startTracker[carID]).total_seconds()
    speed = round(markGap/timeDiff*fpsFactor*3.6,2)
    return speed

#-----------------------------------------------------------------------

def vsdMain():
    print('\n---------- Thread 1 ----------')
    #Declaring variables
    global carTracker
    global startTracker
    global endTracker

    resizeWidth = 960 #resizeWidth of video frame
    resizeHeight = 540 #resizeHeight of video frame
    cropBegin = 240 #Crop video frame from this point
    mark1 = 340 #Mark to start timer
    mark2 = 460 #Mmrk to end timer
    speedLimit = 10 #Speedlimit

    #Classifer for detecting cars
    carCascade = cv2.CascadeClassifier('files/HaarCascadeClassifier.xml')

    #Get the video
    video = cv2.VideoCapture('files/test.mp4')

    #print the speed limit
    print('Speed Limit Set at {} Kmph'.format(speedLimit))

    frameCounter = 0 #initialize the frame counter
    currentCarID = 0 #id of last car to be added

    #start Tracking
    while True:
        image = video.read()[1]
        if type(image) == type(None):
            break

        frameTime = datetime.now()

        image = cv2.resize(image, (resizeWidth, resizeHeight))#[cropBegin:resizeHeight,0:resizeWidth]
        resultImage = image.copy()
        #blackout(resultImage)

        cv2.line(resultImage,(0,mark1),(resizeWidth,mark1),(0,0,255),2)  #uncomment to view video
        cv2.line(resultImage,(0,mark2),(resizeWidth,mark2),(0,0,255),2)  #uncomment to view video

        frameCounter = frameCounter + 1

        #Track every 60th frame
        if (frameCounter%6 == 0):
            #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            #detect cars in frame
            cars = carCascade.detectMultiScale(resultImage, 1.1, 13, 18, (120, 120))

            for newCarPosition in cars:
                matchFound = False
                for carID in carTracker:
                    matchFound = carTracker[carID].centroidComparison(newCarPosition)
                    if matchFound:
                        carTracker[carID].updatePosition(newCarPosition, frameTime)
                        break

                if not matchFound:
                    carTracker[currentCarID] = PositionTracker(newCarPosition, frameTime)
                    currentCarID = currentCarID + 1

        carIDtoDelete = set()

        #print(currentCarID)
        for carID in carTracker:
            if carTracker[carID].lastUpdateTime() + timedelta(seconds = 1.5) < frameTime:
                carIDtoDelete.add(carID)
                continue

            tx, ty, tw, th = carTracker[carID].getPosition()

            #Put bounding boxes
            cv2.rectangle(resultImage, (tx, ty), (tx + tw, ty + th), (0, 255, 0), 2)  #uncomment to view video
            cv2.putText(resultImage, str(carID), (tx,ty-5), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 1)  #uncomment to view video

            #check if a car has crossed mark1, if yes add startTracker for carID
            if carID not in startTracker and mark2 > ty+th > mark1 and ty < mark1:
                startTracker[carID] = carTracker[carID].lastUpdateTime()

            #check if a car has crossed mark2, if yes, add endTracker to carID & estimate speed
            elif carID in startTracker and carID not in endTracker and mark2 < ty+th:
                endTracker[carID] = carTracker[carID].lastUpdateTime()
                speed = estimateSpeed(carID)

                if speed > speedLimit:
                    print('Thread 1 : CAR-ID = {} | Speed = {} kmph | Overspeed'.format(carID, speed))

                    #save image of car
                    saveCarImage(speed,image[ty:ty+th, tx:tx+tw])

                    #add data for license detection
                    overSpeedArr.append((frameTime, speed, image[ty:ty+th, tx:tx+tw]))

                else:
                    print('Thread 1 : CAR-ID = {} | Speed = {} kmph'.format(carID, speed))

        for oldCarID in carIDtoDelete:
            carTracker.pop(oldCarID)

        #Display each frame
        cv2.imshow('result', resultImage)  #uncomment to view video
        #cv2.imshow('result', imutils.resize(resultImage, height=360))

        if cv2.waitKey(33) == 27:  #uncomment to view video
            break  #uncomment to view video

    #close the video
    #cv2.destroyAllWindows()  #uncomment to view video

#-----------------------------------------------------------------------

#globals
carTracker = {} #store tracking details of cars
startTracker = {} #Store starting time of cars
endTracker = {} #Store ending time of cars

if __name__ == '__main__':
    vsdMain()
