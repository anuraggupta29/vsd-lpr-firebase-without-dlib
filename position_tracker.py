class PositionTracker:
    def __init__(self, position, detectionTime):
        self.position = position
        self.updateTime = detectionTime

    def getPosition(self):
        return self.position

    def updatePosition(self, newCarPosition, updateTime):
        self.position = newCarPosition
        self.updateTime = updateTime

    def centroidComparison(self, newCarPosition):
        #get position of a car
        x, y, w, h = newCarPosition
        xbar = x + 0.5*w
        ybar = y + 0.5*h

        #if centroid of current car is near the centroid of another car
        #in the previous frame, then they are the same car
        tx, ty, tw, th = self.position
        txbar = tx + 0.5 * tw
        tybar = ty + 0.5 * th

        if (tx <= xbar <= (tx + tw)) and (ty <= ybar <= (ty + th)):
            if (x <= txbar <= (x + w)) and (y <= tybar <= (y + h)):
                return True

        return False

    def lastUpdateTime(self):
        return self.updateTime
