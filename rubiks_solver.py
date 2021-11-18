import cv2 as cv
from cmu_112_graphics import *
import numpy as np
import math

class Cube(object):
    colorValues = { 
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "white": (255, 255, 255),
        "orange": (255, 165, 0),
        "yellow": (255, 255, 0)
    }

    faces = {
        "red": [],
        "green": [],
        "blue": [],
        "white": [],
        "orange": [],
        "yellow": []
    }

    lcolors = ["white", None, "yellow"] 
    xcolors = ["blue", None, "green"] 
    ycolors = ["orange", None, "red"]

    pieces = [] 

    algorithm = []

    def getFaces(self):
        return self.faces

    def facesToPieces(self):
        self.pieces = []
        for l in range(3):
            layer = []
            for i in range(9):
                x = i % 3
                y = i // 3
                piece = []
                coords = [x, y, l]
                colors = [self.xcolors, self.ycolors, self.lcolors]
                for i in range(3):
                    if coords[i] == 1:
                        piece.append(None)
                    else:
                        face = self.faces[colors[i][coords[i]]]
                        newCoords = copy.copy(coords)
                        newCoords.pop(i)
                        if (i == 0 and coords[i] == 0) or (i == 1 and coords[i] == 2):
                            newCoords[0] = 2 - newCoords[0]
                        color = face[newCoords[0]][newCoords[1]]
                        if i == 2:
                            if coords[i] == 2:
                                newCoords[1] = 2 - newCoords[1] 
                            color = face[newCoords[1]][newCoords[0]]
                        piece.append(color)
                layer.append(piece)    
            self.pieces.append(layer) 
        #self.rotateFace("white", 1)
        self.rotateFace("green", 1)
        self.rotateFace("green", 1)
        self.rotateFace("red", 1)
        # self.rotateFace("blue", 1)
        # self.rotateFace("red", 1)
        self.facesFromPieces()
        print(self.pieces)
        print(self.faces)
    
    def facesFromPieces(self):
        for face in self.faces:
            self.faces[face] = []
            for _ in range(3):
                self.faces[face].append([])
        for layer in range(3):
            for pieceIndex in range(9):
                piece = self.pieces[layer][pieceIndex]
                if layer == 0:
                    self.faces["white"][pieceIndex // 3].append(piece[2])
                if layer == 2:
                    self.faces["yellow"][pieceIndex // 3].append(piece[2])
                if pieceIndex % 3 == 0:
                    self.faces["blue"][2 - (pieceIndex // 3)].append(piece[0])
                if pieceIndex % 3 == 2:
                    self.faces["green"][pieceIndex // 3].append(piece[0])
                if pieceIndex // 3 == 0:
                    self.faces["orange"][pieceIndex % 3].append(piece[1])
                if pieceIndex // 3 == 2:
                    self.faces["red"][2 - (pieceIndex % 3)].append(piece[1])

    def rotateFace(self, face, direction):
        facePieces = []
        ind = 0
        if face in self.lcolors:
            layerIndex = self.lcolors.index(face)
            facePieces = self.pieces[layerIndex]
            if layerIndex == 2:
                direction *= -1
            ind = 2
        elif face in self.xcolors:
            for layer in self.pieces:
                for i in range(3):
                    facePieces.append(layer[(i * 3) + self.xcolors.index(face)])
            if self.xcolors.index(face) == 0:
                direction *= -1
        else:
            for layer in self.pieces:
                start = self.ycolors.index(face) * 3
                facePieces = facePieces + layer[start:start + 3]
            ind = 1
            if self.ycolors.index(face) == 2:
                direction *= -1
        
        newFace = []

        for piece in facePieces:
            newPiece = copy.copy(piece)
            newPiece.pop(ind)
            newPiece = newPiece[::-1]
            newPiece.insert(ind, face)
            newFace.append(newPiece)

        if ind == 0:
            for l in range(3):
                start = self.xcolors.index(face)
                if direction == 1:
                    self.pieces[l][start::3] = newFace[l::3][::-1]
                else:
                    self.pieces[l][start::3] = newFace[2-l::3]
        elif ind == 1:
            for l in range(3):
                start = self.ycolors.index(face) * 3
                if direction == 1:
                    self.pieces[l][start:start + 3] = newFace[l::3][::-1]
                else:
                    self.pieces[l][start:start + 3] = newFace[2-l::3]
        else:
            if direction == 1:
                self.pieces[self.lcolors.index(face)] = newFace[2::3] + newFace[1::3] + newFace[0::3]
            else:
                self.pieces[self.lcolors.index(face)] = newFace[0::3][::-1] + newFace[1::3][::-1] + newFace[2::3][::-1]


    def setFaces(self):
        #self.getFaceImages()
        for color in self.colorValues:
            image = cv.imread(f"{color}.png")
            self.colorValues[color] = self.getAverageColor(20, 20, 75, 75, image)
        
        for face in self.faces:
            image = cv.imread(f"{face}-face.png")
            self.faces[face] = self.getFaceArray(100, image)
            self.faces[face][1][1] = face
        
        # print(self.faces)
        
    def getFaceImages(self):
        cv.namedWindow("cameraView")
        vc = cv.VideoCapture(0)
        if vc.isOpened():
            rval, frame = vc.read()
        else:
            rval = False
            
        colorNames = list(self.colorValues.keys())
        faceIndex = 0
        while rval:
            face = colorNames[faceIndex]
            cv.imshow("cameraView", frame)
            rval, frame = vc.read()
            frame = cv.flip(frame, 1)
            foreground = np.ones((5,5,3),dtype='uint8')*255
            foreground2 = np.ones((95,95,3),dtype='uint8')
            foreground2[:, :] = [self.colorValues[face][2], self.colorValues[face][1], self.colorValues[face][0]]
            foreground3 = np.ones((60, 400, 3), dtype="uint8")*255
            added_image = cv.addWeighted(frame[0:60, 0:400, :], 0, foreground3[0:60, 0:400, :], 1,0)
            cv.putText(added_image, f"Show the {face} face", (10, 20), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0, 0), 2)
            upFace = "white"
            if face == "white" or face == "yellow":
                upFace = "blue"
            cv.putText(added_image, f"with {upFace} facing up.", (10, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0, 0), 2)
            frame[0:60, 0:400, :] = added_image 
            for box in range(9):
                x = 100 * (box % 3) + 150
                y = 100 * (box // 3) + 100
                if box == 4:
                    colorFrame = copy.deepcopy(frame[y + 5: y + 100, x + 5:x + 100,:])
                    added_image = cv.addWeighted(frame[y + 5: y + 100, x + 5:x + 100,:],0,foreground2[0:95,0:95,:],1,0)
                    frame[y + 5: y + 100, x + 5:x + 100,:] = added_image
                else:
                    for diff in range(0, 100):
                        added_image = cv.addWeighted(frame[y + diff: y + (diff + 5), x: x + 5,:],1,foreground[0:5,0:5,:],1,0)
                        frame[y + diff: y + (diff + 5), x: x + 5,:] = added_image
                        added_image = cv.addWeighted(frame[y + diff: y + (diff + 5), x + 100: x + 100 + 5,:],1,foreground[0:5,0:5,:],1,0)
                        frame[y + diff: y + (diff + 5), x + 100: x + 100 + 5,:] = added_image

                        added_image = cv.addWeighted(frame[y:y + 5, x + diff:x + (diff + 5),:],1,foreground[0:5,0:5,:],1,0)
                        frame[y:y + 5, x + diff:x + (diff + 5),:] = added_image
                        added_image = cv.addWeighted(frame[y + 100:y + 100 + 5, x + diff: x + (diff + 5),:],1,foreground[0:5,0:5,:],1,0)
                        frame[y + 100:y + 100 + 5, x + diff: x + (diff + 5),:] = added_image
            key = cv.waitKey(20)
            if key == 27:
                cv.imwrite(f"{face}-face.png", cv.flip(frame[100:100 + 305, 150:150 + 305, :], 1))
                cv.imwrite(f"{face}.png", cv.flip(colorFrame[0:95, 0:95, :], 1))
                faceIndex += 1
                if faceIndex == 6:
                    break
        vc.release()
        cv.destroyWindow("cameraView")

    def colorDist(self, c1, c2):
        dist = ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2) ** 1/2
        return dist

    def getNearestColor(self, myColor):
        minDist = -1
        colorName = ""
        for color in self.colorValues:
            dist = self.colorDist(self.colorValues[color], myColor)
            if dist < minDist or minDist == -1:
                minDist = dist
                colorName = color 
        return colorName

    def getAverageColor(self, x1, y1, x2, y2, image):
        averageR = 0
        averageG = 0
        averageB = 0
        for x in range(x1, x2):  
            for y in range(y1, y2):
                b,g,r = image[x, y]
                averageB += b
                averageG += g
                averageR += r
        averageR /= abs((x2 - x1) * (y2 - y1))
        averageG /= abs((x2 - x1) * (y2 - y1))
        averageB /= abs((x2 - x1) * (y2 - y1))
        return (int(averageR), int(averageG), int(averageB))

    def getFaceArray(self, size, image):
        face = []
        for box in range(9):
            if box % 3 == 0:
                face.append([])
            face[box // 3].append(0)
            x = size * (box % 3)
            y = size * (box // 3)
            c = self.getAverageColor(x + 20, y + 20, x + size - 20, y + size - 20, image)
            color = self.getNearestColor(c)
            face[box // 3][box % 3] = color
        return face

def appStarted(app):
    app.size = 100
    app.cube = Cube()
    app.cube.setFaces()
    app.cube.facesToPieces()

def drawBox(app, canvas, x, y, color):
    canvas.create_rectangle(x, y, x + app.size, y + app.size, fill=color, outline="black", width=5)
    canvas.create_text(x + app.size/2, y + app.size/2, text=color, fill="black", font="Helvetica 15 bold")

def drawFace(app, canvas, face, startX, startY):
    for box in range(9):
        x = app.size * (box % 3)
        y = app.size * (box // 3)
        c = face[box % 3][box //3]
        drawBox(app, canvas, startX + x, startY + y, c)

def redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill="black")
    startingX = 0
    startingY = 0
    for face in app.cube.getFaces():
        drawFace(app, canvas, app.cube.getFaces()[face], startingX, startingY)
        startingX += 350
        if startingX > 1000:
            startingX = 0
            startingY += 350

runApp(width=1200, height=800)


