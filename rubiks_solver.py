import cv2 as cv
from cmu_112_graphics import *
import numpy as np
import math
from cube import *

def appStarted(app):
    app.page = 0
    app.cube = Cube()
    app.startCoords = {
            "blue" : (200, 50, 2),
            "white": (200, 200, 0),
            "green" : (200, 350, 0),
            "orange" : (50, 200, 3),
            "red" : (350, 200, 1),
            "yellow": (500, 200, 0)
    }
    app.sideOrder = ["orange", "green", "red", "blue"]
    app.top = "white"
    app.left = "orange"
    app.right = "green"

def mousePressed(app, event):
    # Changes color of a single square when clicked on
    if app.page == 1:
        x = event.x
        y = event.y
        face = ""
        xDist = 0
        yDist = 0
        for currFace in app.startCoords:
            if (x in range(app.startCoords[currFace][0], app.startCoords[currFace][0] + 150) and 
                y in range(app.startCoords[currFace][1], app.startCoords[currFace][1] + 150)): 
                face = currFace
                xDist = x - app.startCoords[currFace][0]
                yDist = y - app.startCoords[currFace][1]
        if face != "":
            for _ in range(app.startCoords[face][2]):
                temp = xDist
                xDist = 150 - yDist
                yDist = temp
            if (xDist // 50, yDist // 50) != (1, 1):
                color = app.getUserInput("Enter a color")
                if color != "" and type(color) == str:
                    color = color.lower().strip()
                    if color in app.startCoords:
                        app.cube.changeColor(face, (xDist // 50, yDist // 50), color)

def keyPressed(app, event):
    # Rotates cube
    if (event.key == "a" and app.top == "white") or (event.key == "d" and app.top == "yellow"):
        app.left = app.sideOrder[(app.sideOrder.index(app.left) - 1) % 4]
        app.right = app.sideOrder[(app.sideOrder.index(app.right) - 1) % 4]
    if (event.key == "d" and app.top == "white") or (event.key == "a" and app.top == "yellow"):
        app.left = app.sideOrder[(app.sideOrder.index(app.left) + 1) % 4]
        app.right = app.sideOrder[(app.sideOrder.index(app.right) + 1) % 4]
    if (event.key == "w" or event.key == "s"):
        if app.top == "white":
            app.top = "yellow"
        else:
            app.top = "white"
        temp = app.right
        app.right = app.left
        app.left = temp
    # Resets and takes in new cube images
    if (event.key == "r"):
        app.page = 1
        app.cube.getFaceImages()
        app.cube.setFaces()
    # Moves through steps
    if (event.key == 'Left'):
        if app.page == 2:
            app.cube.stepBackward()
    elif (event.key == 'Right'):
        if app.page == 2:
            app.cube.stepForward()
    # Moves through pages
    elif (event.key == 'Space'):
        if app.page < 2:
            app.page += 1
            if app.page == 1:
                app.cube.getFaceImages()
                app.cube.setFaces()
            if app.page == 2:
                app.cube.solveCube()

def drawBox(app, canvas, x, y, color):
    # Draws a single box in the net
    canvas.create_rectangle(x, y, x + 50, y + 50, fill=color, outline="black", width=5)
    canvas.create_text(x + 25, y + 25, text=color, fill="black", font="Helvetica 10 bold")

def drawFace(app, canvas, faceColor, startX, startY, rotation):
    # Draws a single face in the 2D Net
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

def drawIsometric(app, canvas, startX, startY):
    # Creates isometric projection based on current top, left, and right sides
    topFace = app.cube.getFaces()[app.top]
    rightFace = app.cube.getFaces()[app.right]
    leftFace = app.cube.getFaces()[app.left]
        
    topRotations = (4 - app.sideOrder.index(app.left)) % 4

    if app.top == "yellow":
        topRotations = (4 - topRotations + 2) % 4
        for _ in range(2):
            newLeftFace = [["","",""],["","",""],["","",""]]
            newRightFace = [["","",""],["","",""],["","",""]]
            for i in range(9):
                newLeftFace[i % 3][i // 3] = leftFace[2 - (i // 3)][i % 3]
                newRightFace[i % 3][i // 3] = rightFace[2 - (i // 3)][i % 3]
            leftFace = newLeftFace
            rightFace = newRightFace

    for _ in range(topRotations):
        newTopFace =  [["","",""],["","",""],["","",""]]
        for i in range(9):
            newTopFace[i % 3][i // 3] = topFace[2 - (i // 3)][i % 3]
        topFace = newTopFace

    for i in range(9):
        topX = 43 * ((i % 3) + (i // 3)) + startX
        topY = 25 * ((i % 3) - (i // 3)) + startY
        canvas.create_polygon(topX, topY, topX + 43, topY - 25, topX + 86, topY, topX + 43, topY + 25, fill=topFace[i // 3][i % 3], outline="black", width=5)
        rightX = 129 + 43 * (i // 3) + startX 
        rightY = 50 * (i % 3) - 25 * (i // 3) + startY + 75
        canvas.create_polygon(rightX, rightY, rightX + 43, rightY - 25, rightX + 43, rightY + 25, rightX, rightY + 50, fill=rightFace[i // 3][i % 3], outline="black", width=5)
        leftX = 43 * (i // 3) + startX 
        leftY = 50 * (i % 3) - 25 * (2 - (i // 3)) + startY + 75
        canvas.create_polygon(leftX, leftY - 25, leftX + 43, leftY, leftX + 43, leftY + 50, leftX, leftY + 25, fill=leftFace[i // 3][i % 3], outline="black", width=5)

def redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill="black")
    if app.page == 0:
        # Instructions page
        canvas.create_text(app. width / 2, 50, text="Welcome to Rubik's Cube Solver!", fill="white", font="Helvetica 30 bold")
        canvas.create_text(app. width / 2, 100, text="Press the spacebar to scan your cube.", fill="white", font="Helvetica 20 bold")
        canvas.create_text(app. width / 2, 150, text="Use the left and right arrow keys to navigate through the steps.", fill="white", font="Helvetica 20 bold")
        canvas.create_text(app. width / 2, 200, text="Use the A, W, S, and D keys to rotate the cube.", fill="white", font="Helvetica 20 bold")
        canvas.create_text(app. width / 2, 250, text="Press R at any time to rescan your cube.", fill="white", font="Helvetica 20 bold")
        for i in range(9):
            topX = 43 * ((i % 3) + (i // 3)) + app.width/2 - 125
            topY = 25 * ((i % 3) - (i // 3)) + 400
            canvas.create_polygon(topX, topY, topX + 43, topY - 25, topX + 86, topY, topX + 43, topY + 25, fill="white", outline="black", width=5)
            rightX = 129 + 43 * (i // 3) + app.width/2 - 125
            rightY = 50 * (i % 3) - 25 * (i // 3) + 400 + 75
            canvas.create_polygon(rightX, rightY, rightX + 43, rightY - 25, rightX + 43, rightY + 25, rightX, rightY + 50, fill="green", outline="black", width=5)
            leftX = 43 * (i // 3) + app.width/2 - 125
            leftY = 50 * (i % 3) - 25 * (2 - (i // 3)) + 400 + 75
            canvas.create_polygon(leftX, leftY - 25, leftX + 43, leftY, leftX + 43, leftY + 50, leftX, leftY + 25, fill="orange", outline="black", width=5)
    
    if app.page == 1 or app.page == 2:
        # Draws cube views
        for face in app.cube.getFaces():
            startingX = app.startCoords[face][0]
            startingY = app.startCoords[face][1]
            rotation = app.startCoords[face][2]
            drawFace(app, canvas, face, startingX, startingY, rotation)
        drawIsometric(app, canvas, 800, 200)

    if app.page == 1:
        canvas.create_text(app. width / 2, app.height - 60, text="Click on any box to change its color", fill="white", font="Helvetica 15 bold")
        canvas.create_text(app. width / 2, app.height - 30, text="Press the spacebar to solve the cube", fill="white", font="Helvetica 15 bold")
    
    if app.page == 2:
        if app.cube.currStep != len(app.cube.algorithm):
            # Shows current cube step
            canvas.create_text(app. width / 2, app.height - 60, text=f"Step {app.cube.currStep + 1} / {len(app.cube.algorithm)}", fill="white", font="Helvetica 15 bold")
        canvas.create_text(app. width / 2, app.height - 30, text=app.cube.getCurrentStep(), fill="white", font="Helvetica 15 bold")

runApp(width=1200, height=700)