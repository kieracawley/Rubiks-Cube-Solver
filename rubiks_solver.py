import cv2 as cv
from cmu_112_graphics import *
import numpy as np
import math

class Cube(object):
    colorValues = { 
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "orange": (255, 165, 0),
        "white": (255, 255, 255),
        "yellow": (255, 255, 0)
    }


    faces = {
        "red": [],
        "green": [],
        "blue": [],
        "orange": [],
        "white": [],
        "yellow": []
    }

    currStep = 0

    lcolors = ["white", None, "yellow"] 
    xcolors = ["blue", None, "green"] 
    ycolors = ["orange", None, "red"]

    pieces = [] 

    algorithm = []

    def stepForward(self):
        if self.currStep < len(self.algorithm):
            self.runAlgorithm([self.algorithm[self.currStep]])
            self.currStep += 1

    def stepBackward(self):
        if self.currStep > 0:
            self.currStep -= 1 
            self.runAlgorithm([(self.algorithm[self.currStep][0], self.algorithm[self.currStep][1] * -1)])

    def resetCube(self):
        for move in self.algorithm[::-1]:
            self.runAlgorithm([(move[0], -1 * move[1])])

    def shortenAlgorithm(self):
        newAlgorithm = []
        prevFace = ""
        prevDirection = 0
        for move in self.algorithm:
            if move[0] == prevFace:
                prevDirection += move[1]
            else:
                if prevDirection % 4 != 0:
                    newAlgorithm.append((prevFace, prevDirection))
                prevFace = move[0]
                prevDirection = move[1]
        newAlgorithm.append((prevFace, prevDirection))
        self.algorithm = newAlgorithm

    def solveCube(self):
        self.algorithm = []
        self.solveWhiteCross()
        self.solveTopCorners()
        self.solveMidEdges()
        self.solveYellowEdges()
        self.solveYellowCorners()
        for _ in range(5):
            self.shortenAlgorithm()
        self.resetCube()

    def solveYellowCorners(self):
        for _ in range(4):
            while self.pieces[2][0][2] != "yellow":
                algorithm = []
                algorithm.append(("blue", -1)) 
                algorithm.append(("white", -1))
                algorithm.append(("blue", 1))
                algorithm.append(("white", 1))
                self.algorithm = self.algorithm + algorithm
                self.runAlgorithm(algorithm)
            self.algorithm.append(("yellow", 1))
            self.rotateFace("yellow", 1)
        algorithm = []
        algorithm.append(("orange", -1))
        algorithm.append(("white", -1))
        algorithm.append(("orange", 1))
        algorithm.append(("yellow", 1))
        algorithm.append(("orange", -1))
        algorithm.append(("white", 1))
        algorithm.append(("orange", 1))
        algorithm.append(("yellow", 1))
        algorithm.append(("orange", -1))
        algorithm.append(("white", -1))
        algorithm.append(("orange", 1))
        algorithm.append(("yellow", -2))
        algorithm.append(("orange", -1))
        algorithm.append(("white", 1))
        algorithm.append(("orange", 1))
        
        correctCorners = self.correctYellowCorners()

        if correctCorners != 4:
            if len(correctCorners) == 0:
                self.algorithm = self.algorithm + algorithm
                self.runAlgorithm(algorithm)
                correctCorners = self.correctYellowCorners()
            rotations = 0
            while self.findPiece(correctCorners[0]) != (2, 8):
                rotations += 1 
                self.algorithm.append(("yellow", 1))
                self.rotateFace("yellow", 1)
            while len(correctCorners) == 1:
                self.algorithm = self.algorithm + algorithm
                self.runAlgorithm(algorithm)
                correctCorners = self.correctYellowCorners()
            for _ in range(rotations):
                self.algorithm.append(("yellow", -1))
                self.rotateFace("yellow", -1)
        
    def correctYellowCorners(self):
        rotations = 0
        while self.findPiece([None, "orange", "yellow"]) != (2, 1):
            self.rotateFace("yellow", 1)
            rotations += 1
        incorrect = []
        corners = [0, 2, 6, 8]
        for i in range(4):
            cornerCoords = (2, corners[i])
            piece = [self.xcolors[cornerCoords[1] % 3], self.ycolors[cornerCoords[1] // 3], "yellow"]
            pieceCoords = self.findPiece(piece)
            if cornerCoords == pieceCoords:
                incorrect.append(piece)
        for _ in range(rotations):
            self.rotateFace("yellow", -1)
        return incorrect

    def solveYellowEdges(self):
        faces = self.getYellowFaces()
        algorithm = []
        algorithm.append(("blue", 1))
        algorithm.append(("red", 1))
        algorithm.append(("yellow", 1))
        algorithm.append(("red", -1))
        algorithm.append(("yellow", -1))
        algorithm.append(("blue", -1))

        if len(faces) == 0:
            self.algorithm = self.algorithm + algorithm
            self.runAlgorithm(algorithm)
            faces = self.getYellowFaces()
        
        while len(faces) == 2:
            while faces != [1, 7] and faces != [1, 5]:
                self.algorithm.append(("yellow", 1))
                self.rotateFace("yellow", 1)
                faces = self.getYellowFaces()
            self.algorithm = self.algorithm + algorithm
            self.runAlgorithm(algorithm)
            faces = self.getYellowFaces()

        for i in range(3):
            endCoords = (2, 1 + (i * 2))
            piece = [None, "yellow"]
            if i == 0:
                piece.insert(1, self.ycolors[endCoords[1] // 3])
            else:
                piece.insert(0, self.xcolors[endCoords[1] % 3])
            pieceCoords = self.findPiece(piece)
            if endCoords != pieceCoords:
                if self.isAcross(endCoords, pieceCoords):
                    self.acrossEdgeSwao(endCoords, pieceCoords)
                else:
                    self.adjacentEdgeSwap(endCoords, pieceCoords)
            pieceCoords = self.findPiece(piece)

    def getYellowFaces(self):
        yellowFaces = []
        for i in range(4):
            edgeCoords = [2, 1 + (2 * i)]
            if self.pieces[edgeCoords[0]][edgeCoords[1]][2] == "yellow":
                yellowFaces.append(edgeCoords[1])
        return yellowFaces

    def solveMidEdges(self):
        edges = [0, 2, 8, 6]
        colors = ["orange", "blue", "red", "green"]
        for i in range(4):
            endCoords = (1, edges[i])
            xcolor = self.xcolors[endCoords[1] % 3]
            ycolor = self.ycolors[endCoords[1] // 3]
            leftSide = xcolor
            rightSide = ycolor
            if colors[(colors.index(xcolor) - 1)] == ycolor:
                leftSide = ycolor
                rightSide = xcolor
            piece = [self.xcolors[endCoords[1] % 3], self.ycolors[endCoords[1] // 3], None]
            pieceCoords = self.findPiece(piece)
            if self.pieces[endCoords[0]][endCoords[1]] != piece:
                if pieceCoords[0] == 1:
                    currLeftSide = self.xcolors[pieceCoords[1] % 3]
                    currRightSide = self.ycolors[pieceCoords[1] // 3]
                    if colors[(colors.index(self.xcolors[pieceCoords[1] % 3]) - 1)] == self.ycolors[pieceCoords[1] // 3]:
                        currLeftSide = self.ycolors[pieceCoords[1] // 3]
                        currRightSide = self.xcolors[pieceCoords[1] % 3]
                    algorithm = []
                    algorithm.append(("yellow", -1))
                    algorithm.append((currLeftSide, -1))
                    algorithm.append(("yellow", 1))
                    algorithm.append((currLeftSide, 1))
                    algorithm.append(("yellow", 1))
                    algorithm.append((currRightSide, 1))
                    algorithm.append(("yellow", -1))
                    algorithm.append((currRightSide, -1))
                    self.algorithm = self.algorithm + algorithm
                    self.runAlgorithm(algorithm)
                    pieceCoords = self.findPiece(piece)
                centerFace = self.pieces[pieceCoords[0]][pieceCoords[1]][0]
                if centerFace == None:
                    centerFace = self.pieces[pieceCoords[0]][pieceCoords[1]][1]
                centerCoords = self.findPiece([None, None, centerFace])
                while pieceCoords[1] != centerCoords[1]:
                    self.rotateFace("yellow", 1)
                    self.algorithm.append(("yellow", 1))
                    pieceCoords = self.findPiece(piece)
                face1 = xcolor
                if xcolor == centerFace:
                    face1 = ycolor
                direction = 1
                if centerFace == rightSide:
                    direction = -1
                algorithm = []
                algorithm.append(("yellow", direction))
                algorithm.append((face1, direction))
                algorithm.append(("yellow", -1 * direction))
                algorithm.append((face1, -1 * direction))
                algorithm.append(("yellow", -1 * direction))
                algorithm.append((centerFace, -1 * direction))
                algorithm.append(("yellow", direction))
                algorithm.append((centerFace, direction))
                self.algorithm = self.algorithm + algorithm
                self.runAlgorithm(algorithm)
                pieceCoords = self.findPiece(piece)

    def solveTopCorners(self):
        cornerIndexes = [0, 2, 8, 6]
        for i in range(4):
            endCoords = (0, cornerIndexes[i]) 
            xColor = self.xcolors[endCoords[1] % 3]
            yColor = self.ycolors[endCoords[1] // 3]
            piece = [xColor, yColor, "white"]
            pieceCoords = self.findPiece(piece)
            direction = 1 
            if endCoords[1] == 2 or endCoords[1] == 6:
                    direction = -1
            if pieceCoords != endCoords:
                if pieceCoords[0] == endCoords[0]:
                    algorithm = []
                    currXColor = self.pieces[1][3 + (pieceCoords[1] % 3)][0]
                    currDirection = 1
                    if pieceCoords[1] == 2 or pieceCoords[1] == 6:
                        currDirection = -1
                    algorithm.append((currXColor, currDirection))
                    algorithm.append(("yellow", currDirection))
                    algorithm.append((currXColor, currDirection * -1 ))
                    algorithm.append(("yellow", currDirection * -1 ))
                    self.algorithm = self.algorithm + algorithm
                    self.runAlgorithm(algorithm) 
                while pieceCoords[1] != endCoords[1]:
                    self.algorithm.append(("yellow", 1))
                    self.rotateFace("yellow", 1)
                    pieceCoords = self.findPiece(piece)
                algorithm = []
                algorithm.append(("yellow", direction))
                algorithm.append((xColor, direction))
                algorithm.append(("yellow", direction * -1 ))
                algorithm.append((xColor, direction * -1 ))
                self.algorithm = self.algorithm + algorithm
                self.runAlgorithm(algorithm)
            while self.pieces[0][endCoords[1]][2] != "white":
                for _ in range(2):
                    algorithm = []
                    algorithm.append((xColor, direction))
                    algorithm.append(("yellow", direction))
                    algorithm.append((xColor, direction * -1 ))
                    algorithm.append(("yellow", direction * -1 ))
                    self.algorithm = self.algorithm + algorithm
                    self.runAlgorithm(algorithm)
             
    def runAlgorithm(self, algorithm):
         for move in algorithm:
            face = move[0]
            direction = move[1] // abs(move[1])                    
            for _ in range(abs(move[1])):
                self.rotateFace(face, direction)

    def solveWhiteCross(self):
        colors = ["orange", "blue", "red", "green"]
        clockwise = [1, 3, 7, 5]
        for i in range(4):
            endCoords = (0, clockwise[i])
            piece = [colors[i], "white"]
            if i == 1 or i == 2:
                piece.insert(1, None)
            else:
                piece.insert(0, None)
            pieceCoords = self.findPiece(piece)
            if pieceCoords != endCoords:
                if pieceCoords[0] == endCoords[0]:
                    currFace = colors[clockwise.index(pieceCoords[1])]
                    self.rotateFace(currFace, 1)
                    self.rotateFace(currFace, 1)
                    self.algorithm.append((currFace, 2))
                    pieceCoords = self.findPiece(piece)
                rotations = 0
                while self.shareFace(endCoords, pieceCoords) == False:
                    self.rotateFace("white", 1)
                    self.algorithm.append(("white", 1))
                    rotations += 1 
                    endCoords = (0, clockwise[(clockwise.index(endCoords[1]) + 1) % 4])
                sharedFace = colors[clockwise.index(endCoords[1])]
                if self.isAcross(endCoords, pieceCoords):
                    self.rotateFace(sharedFace, 1)
                    self.rotateFace(sharedFace, 1)
                    self.algorithm.append((sharedFace, 2))
                    pieceCoords = self.findPiece(piece)
                else:
                    while endCoords != pieceCoords:
                        self.rotateFace(sharedFace, 1)
                        self.algorithm.append((sharedFace, 1))
                        pieceCoords = self.findPiece(piece)

                for _ in range(rotations):
                    self.rotateFace("white", -1)
                    self.algorithm.append(("white", -1))
            endCoords = (0, clockwise[i])
            if self.pieces[0][endCoords[1]][2] != "white":
                frontCoords = (1, clockwise[(clockwise.index(endCoords[1]) + 1) % 4])
                front = self.pieces[1][frontCoords[1]][0]
                right = self.pieces[0][endCoords[1]][2]
                if front == None:
                    front = self.pieces[1][frontCoords[1]][1]
                newAlgorithm = []
                newAlgorithm.append((right, -1))
                newAlgorithm.append(("white", 1))
                newAlgorithm.append((front, -1))
                newAlgorithm.append(("white", -1))
                self.algorithm = self.algorithm + newAlgorithm
                self.runAlgorithm(newAlgorithm)

    def shareFace(self, piece1Coords, piece2Coords):
        if piece1Coords[0] == piece2Coords[0] and piece1Coords[0] != 1:
            return True
        if piece1Coords[1] % 3 == piece2Coords[1] % 3 and piece1Coords[1] % 3 != 1:
            return True
        if piece1Coords[1] // 3 == piece2Coords[1] // 3 and piece1Coords[1] // 3 != 1:
            return True
        return False

    def isAcross(self, piece1Coords, piece2Coords):
        if piece1Coords[1] == piece2Coords[1]:
            return True
        if piece1Coords[0] == piece2Coords[0]:
            if piece1Coords[1] % 3 == piece2Coords[1] % 3 or piece1Coords[1] // 3 == piece2Coords[1] // 3:
                return True
        return False

    def findPiece(self, piece):
        for layer in range(3):
            for i in range(9):
               if self.matchPermutations(piece, self.pieces[layer][i]):
                   return (layer, i)
        return None
    
    def matchPermutations(self, piece1, piece2):
        for i in range(3):
            if piece1[i:] + piece1[:i] == piece2 or piece1[i:] + piece1[:i] == piece2[::-1]:
                return True
        return False

    def getFaces(self):
        return self.faces

    def adjacentEdgeSwap(self, side1Coords, side2Coords):
        top = ""
        right = ""
        if side1Coords[0] == side2Coords[0]:
            top = self.pieces[side1Coords[0]][4][2]
            leftSideCoords = []
            order  = [1, 3, 7, 5]
            if top == "yellow":
                order = order[::-1]
            if (order.index(side2Coords[1]) + 1) % 4 == order.index(side1Coords[1]):
                leftSideCoords = side1Coords
            else:
                leftSideCoords = side2Coords
            if leftSideCoords[1] % 3 == 1:
                rightCoords = [0, (2 - leftSideCoords[1] // 3) * 3 +  1]
                right = self.pieces[1][rightCoords[1]][1]
            else:
                rightCoords = [0, 3 + (2 - leftSideCoords[1] % 3)]
                right = self.pieces[1][rightCoords[1]][0]
        elif side1Coords[1] % 3 == side2Coords[1] % 3:
            top = self.pieces[1][3 + (side1Coords[1] % 3)][0]
            side1Num = side1Coords[0] + (side1Coords[1] // 3) * 3
            side2Num = side2Coords[0] + (side2Coords[1] // 3) * 3
            order  = [1, 3, 7, 5]
            if top == "blue":
                order = order[::-1]
            if (order.index(side2Num) + 1) % 4 == order.index(side1Num):
                leftSideCoords = side1Coords
            else:
                leftSideCoords = side2Coords
            if leftSideCoords[0] == 1:
                rightCoords = [leftSideCoords[0], (2 - leftSideCoords[1] // 3) * 3 +  1]
                right = self.pieces[1][rightCoords[1]][1]
            else:
                rightCoords = [2 - leftSideCoords[0], leftSideCoords[1]]
                right = self.pieces[rightCoords[0]][4][2]
        else:
            top = self.pieces[1][ 1 + ((side1Coords[1] // 3) * 3)][1]
            side1Num = side1Coords[0] + (side1Coords[1] % 3) * 3 
            side2Num = side2Coords[0] + (side2Coords[1] % 3) * 3 
            order  = [1, 3, 7, 5]
            if top == "red":
                order = order[::-1]
            if (order.index(side2Num) + 1) % 4 == order.index(side1Num):
                leftSideCoords = side1Coords
            else:
                leftSideCoords = side2Coords
            if leftSideCoords[0] == 1:
                rightCoords = [leftSideCoords[0], 3 + (2 - leftSideCoords[1] % 3)]
                right = self.pieces[1][rightCoords[1]][0]
            else:
                rightCoords = [2 - leftSideCoords[0], leftSideCoords[1]]
                right = self.pieces[rightCoords[0]][4][2]
        
        algorithm = []

        algorithm.append((right, 1))
        algorithm.append((top, 1))
        algorithm.append((right, -1))
        algorithm.append((top, 1))
        algorithm.append((right, 1))
        algorithm.append((top, 2))
        algorithm.append((right, -1))
        algorithm.append((top, 1))

        self.algorithm = self.algorithm + algorithm

        self.runAlgorithm(algorithm)

    def acrossEdgeSwao(self, side1Coords, side2Coords):
        midSideCoords = []
        if side1Coords[0] == side2Coords[0]: 
            if side1Coords[0] != 1:
                if side1Coords[1] // 3 == side2Coords[1] // 3:
                    midSideCoords = (side1Coords[0], 1)
                else:
                    midSideCoords = (side1Coords[0], 3)
            else:
                if side1Coords[1] % 3 == side2Coords[1] % 3:
                    midSideCoords = (2, 3 + side1Coords[1] % 3)
                else:
                    midSideCoords = (2, (side1Coords[1] // 3) * 3 + 1)
        else:
            if side1Coords[1] % 3 == 1:
                midSideCoords = (1, 3 * (side1Coords[1] // 3))
            else:
                midSideCoords = (1, side1Coords[1] % 3)
        self.adjacentEdgeSwap(side1Coords, midSideCoords)
        self.adjacentEdgeSwap(midSideCoords, side2Coords)
        self.adjacentEdgeSwap(side1Coords, midSideCoords)

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
                    self.faces["yellow"][2 - (pieceIndex // 3)].append(piece[2])
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
            newPiece.insert(ind, piece[ind])
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
        self.facesFromPieces()

    def setFaces(self):
        for color in self.colorValues:
            image = cv.imread(f"{color}.png")
            self.colorValues[color] = self.getAverageColor(20, 20, 75, 75, image)
        
        for face in self.faces:
            image = cv.imread(f"{face}-face.png")
            self.faces[face] = self.getFaceArray(100, image)
            self.faces[face][1][1] = face
        self.facesToPieces()
        
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

    def getCurrentStep(self):
        if self.currStep < len(self.algorithm):
            step = self.algorithm[self.currStep]
            direction = "clockwise"
            if step[1] < 0:
                direction = "counterclockwise"
            return f"Rotate the {step[0]} face {direction} {abs(step[1])} time(s)"
        return "The cube is sovled!"

def appStarted(app):
    app.page = 0
    app.cube = Cube()

def keyPressed(app, event):
    if (event.key == "r"):
        app.page = 1
        app.cube.getFaceImages()
        app.cube.setFaces()
    if (event.key == 'Left'):
        if app.page == 2:
            app.cube.stepBackward()
    elif (event.key == 'Right'):
        if app.page == 2:
            app.cube.stepForward()
    elif (event.key == 'Space'):
        if app.page < 2:
            app.page += 1
            if app.page == 1:
                app.cube.getFaceImages()
                app.cube.setFaces()
            if app.page == 2:
                app.cube.solveCube()

def drawBox(app, canvas, x, y, color):
    canvas.create_rectangle(x, y, x + 50, y + 50, fill=color, outline="black", width=5)
    canvas.create_text(x + 25, y + 25, text=color, fill="black", font="Helvetica 10 bold")

def drawFace(app, canvas, faceColor, startX, startY, rotation):
    face = app.cube.getFaces()[faceColor]
    for _ in range(rotation):
        newFace = [["","",""],["","",""],["","",""]]
        for i in range(9):
            newFace[i % 3][i // 3] = face[2 - (i // 3)][i % 3]
        face = newFace
    for box in range(9):
        x = 50 * (box % 3)
        y = 50 * (box // 3)
        c = face[box % 3][box //3]
        drawBox(app, canvas, startX + x, startY + y, c)

def drawIsometric(app, canvas, top, right, left, startX, startY):
    rotations = {
        "white": 0,
        "green": 0,
        "orange": 0,
        "red": 2,
        "blue": 2,
        "yellow": 1
    }
    topFace = app.cube.getFaces()[top]
    rightFace = app.cube.getFaces()[right]
    leftFace = app.cube.getFaces()[left]
    
    faces = [[topFace, top], [rightFace, right], [leftFace, left]]

    for face in faces:
        for _ in range(rotations[face[1]]):
            newFace = [["","",""],["","",""],["","",""]]
            for i in range(9):
                newFace[i % 3][i // 3] = face[0][2 - (i // 3)][i % 3]
            face[0] = newFace

    for i in range(9):
        topX = 43 * ((i % 3) + (i // 3)) + startX
        topY = 25 * ((i % 3) - (i // 3)) + startY
        canvas.create_polygon(topX, topY, topX + 43, topY - 25, topX + 86, topY, topX + 43, topY + 25, fill=faces[0][0][i // 3][i % 3], outline="black", width=5)
        rightX = 129 + 43 * (i // 3) + startX 
        rightY = 50 * (i % 3) - 25 * (i // 3) + startY + 75
        canvas.create_polygon(rightX, rightY, rightX + 43, rightY - 25, rightX + 43, rightY + 25, rightX, rightY + 50, fill=faces[1][0][i // 3][i % 3], outline="black", width=5)
        leftX = 43 * (i // 3) + startX 
        leftY = 50 * (i % 3) - 25 * (2 - (i // 3)) + startY + 75
        canvas.create_polygon(leftX, leftY - 25, leftX + 43, leftY, leftX + 43, leftY + 50, leftX, leftY + 25, fill=faces[2][0][i // 3][i % 3], outline="black", width=5)

def redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill="black")
    if app.page == 0:
        canvas.create_text(app. width / 2, 50, text="Welcome to Rubik's Cube Solver!", fill="white", font="Helvetica 30 bold")
        canvas.create_text(app. width / 2, 100, text="Press the spacebar to scan your cube.", fill="white", font="Helvetica 20 bold")
        canvas.create_text(app. width / 2, 150, text="Use the left and right arrow keys to navigate through the steps.", fill="white", font="Helvetica 20 bold")
    if app.page == 1 or app.page == 2:
        startCoords = {
            "blue" : (200, 50, 2),
            "white": (200, 200, 0),
            "green" : (200, 350, 0),
            "orange" : (50, 200, 3),
            "red" : (350, 200, 1),
            "yellow": (500, 200, 0)
        }
        for face in app.cube.getFaces():
            startingX = startCoords[face][0]
            startingY = startCoords[face][1]
            rotation = startCoords[face][2]
            drawFace(app, canvas, face, startingX, startingY, rotation)
        drawIsometric(app, canvas, "white", "green", "orange", 900, 100)
        drawIsometric(app, canvas, "yellow", "red", "blue", 900, 400)

    if app.page == 1:
        canvas.create_text(app. width / 2, app.height - 30, text="Press the spacebar to solve the cube", fill="white", font="Helvetica 15 bold")
    
    if app.page == 2:
        if app.cube.currStep != len(app.cube.algorithm):
            canvas.create_text(app. width / 2, app.height - 60, text=f"Step {app.cube.currStep + 1} / {len(app.cube.algorithm)}", fill="white", font="Helvetica 15 bold")
        canvas.create_text(app. width / 2, app.height - 30, text=app.cube.getCurrentStep(), fill="white", font="Helvetica 15 bold")

runApp(width=1200, height=700)