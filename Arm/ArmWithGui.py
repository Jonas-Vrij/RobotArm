from tkinter import *
import math
import serial.tools.list_ports
import threading
from Pathplanning import findPath
from Pathplanning import addWall
from Pathplanning import createNodes

endX = 0
endY = 0
ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()
portsList = []
saving_mode = False
clickCounter = 0
inbetweenCoords = ()
inverseAngles = False


def returnAngles(xCoord, yCoord, drawLines, inverse):
    if yCoord == a + c:
        return "90_180_0"

    goalX = xCoord
    goalY = yCoord

    b = math.sqrt((goalX ** 2) + (goalY ** 2))
    if b > a + c:
        print("Coordinates out of range!")

    alpha = math.atan(goalY / goalX)
    beta = math.acos((b ** 2 + a ** 2 - c ** 2) / (2 * a * b))

    angle_A = math.degrees(alpha + beta)
    angle_B = math.degrees(math.acos((a ** 2 + c ** 2 - b ** 2) / (2 * a * c)))
    angle_C = 180 - angle_A - angle_B
    if inverse:
        angle_A = 360 - angle_C
        angle_B = 360 - angle_B

    outStr = f"{round(angle_A)}_{round(angle_B)}_{slider.get()}"
    if drawLines:
        updateLines(round(angle_A), round(angle_B))

    return outStr


def orientation(p, q, r):
    num = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if num == 0:
        return 0  # Collinear
    return 1 if num > 0 else 2  # Clockwise or Counterclockwise


def on_segment(p, q, r):
    return (max(p[0], r[0]) >= q[0] >= min(p[0], r[0]) and
            max(p[1], r[1]) >= q[1] >= min(p[1], r[1]))


def do_intersect(p1, q1, p2, q2):
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    if o1 != o2 and o3 != o4:
        return True

    if o1 == 0 and on_segment(p1, p2, q1):
        return True
    if o2 == 0 and on_segment(p1, q2, q1):
        return True
    if o3 == 0 and on_segment(p2, p1, q2):
        return True
    if o4 == 0 and on_segment(p2, q1, q2):
        return True

    return False


def line_crosses_square(square_vertices, line_points):
    for i in range(4):
        j = (i + 1) % 4
        if do_intersect(square_vertices[i], square_vertices[j], line_points[0], line_points[1]):
            return True
    return False


def drag_start(event):
    label.startX = event.x
    label.startY = event.y


def drag_motion(event):
    global endAngle, inverseAngles, endX, endY
    pX = label.winfo_x() - label.startX + event.x
    y = label.winfo_y() - label.startY + event.y
    updateCoords(pX, y)

def updateCoords(pX, y):
    global inverseAngles
    angles = returnAngles(pX, 500 - y, False, inverseAngles).split('_')
    foreArmPoints = draw_rotated_line(None, None, a, 0, 500, int(angles[0]), False)
    foreArmPoints = [(0, 0), (foreArmPoints[0], 500 - foreArmPoints[1])]
    armPoints = [(foreArmPoints[1][0], foreArmPoints[1][1]), (pX, 500 - y)]

    # check for Minimal value if arms arnt same length
    if a != c:
        if (pX ** 2) + ((500 - y) ** 2) < (a - c) ** 2:
            return 0
    if (pX ** 2) + ((500 - y) ** 2) > (a + c) ** 2:
        return 0

    # check if arms cross with obstacles
    for i in obstructions:
        global endX, endY
        if line_crosses_square(i, foreArmPoints):
            inverseAngles = True
            break
        else:
            inverseAngles = False
            if line_crosses_square(i, armPoints):
                inverseAngles = True
                break
            else:
                inverseAngles = False
    if inverseAngles:
        angles = returnAngles(pX, 500 - y, False, True).split('_')
        foreArmPoints = draw_rotated_line(None, None, a, 0, 500, int(angles[0]), False)
        foreArmPoints = [(0, 0), (foreArmPoints[0], 500 - foreArmPoints[1])]
        armPoints = [(foreArmPoints[1][0], foreArmPoints[1][1]), (pX, 500 - y)]
        for i in obstructions:
            if line_crosses_square(i, foreArmPoints):
                print("Point not in Range!")
                return 0
            if line_crosses_square(i, armPoints):
                print("Point not in Range!")
                return 0
    returnAngles(pX, 500 - y, True, inverseAngles)
    label.place(x=pX - 10, y=y - 10)
    label.lift()
    # Update the coordinates label text
    endX, endY = [pX, 500 - y]
    coordinates_label.config(text=f"({pX}, {500 - y})")
    coordinates_label.place(x=pX - 10, y=y - 30)

    angles = returnAngles(pX, 500 - y, True, inverseAngles).split('_')
    anglesLabel.config(text=f"A:{angles[0]}, B:{angles[1]}, C:{endAngle+facing_slider.get()}")


def draw_rotated_line(pCanvas, line_id, length, pX, y, angle, draw):
    # Convert the angle to radians and calculate trigonometric values
    angle_rad = angle * (math.pi / 180.0)
    cos_angle = math.cos(angle_rad)
    sin_angle = math.sin(angle_rad)

    # Calculate the coordinates of the rotated line
    x1 = pX
    y1 = y
    x2 = pX + length * cos_angle
    y2 = y - length * sin_angle

    # Update the coordinates of the line on the canvas
    if draw:
        pCanvas.coords(line_id, x1, y1, x2, y2)
    return [int(x2), int(y2)]


def updateLines(alpha, beta):
    elbowCoord = draw_rotated_line(canvas, arm, c, 5, 500, alpha, True)
    draw_rotated_line(canvas, foreArm, a, elbowCoord[0], elbowCoord[1], 180 + alpha + beta, True)
    updateFacing(180 + alpha + beta)


def resetPos():
    global obstructions
    global inverseAngles
    inverseAngles = False
    updateCoords(1, 500)
    obstructions = []
    canvas.delete("obstacle")


def changePos():
    # try:
    pX, y = entry.get().split(',')
    planPath(int(pX), int(y))
    updateCoords(int(pX), 500 - int(y))
    # except:
    print("No Valid Input!")
    pass


def loopToZero(num):
    if num == 360:
        slider.set(0)
    elif num == -1:
        slider.set(359)


endAngle = 0


def updateFacing(angle):
    global endAngle
    global endX, endY
    if angle is not None:
        endAngle = angle
    num = endAngle + facing_slider.get()
    draw_rotated_line(canvas, facingLine, 60, endX, 500 - endY, num, True)


def executePeriodically():
    while True:
        try:
            outStr = returnAngles(label.winfo_x(), 500 - label.winfo_y(), False, inverseAngles)
        except:
            outStr = "0_0_0"
        serialInst.write(outStr.encode('utf-8'))
        print(outStr)
        threading.Event().wait(1)


def toggle_saving_mode():
    global saving_mode
    saving_mode = not saving_mode


def planPath(goalX, goalY):
    smallGoal = (goalX // 10, goalY // 10)
    smallStart = (endX // 10, (endY) // 10)
    print(f"findPath({smallGoal}, {smallStart})")
    findPath(smallGoal, smallStart)


def addObstacleAsWalls(point1, point2):
    out = []
    newPoint1 = (point1[0] // 10, point1[1] // 10)
    newPoint2 = (point2[0] // 10, point2[1] // 10)
    for x in range(newPoint1[0], newPoint1[1] + 1):
        for y in range(newPoint2[0], newPoint2[1] + 1):
            nodeName = f"Node{x}{y}"
            out.append(nodeName)
    for i in out:
        print(f"Coord {i}, I am a motherfucker")
        addWall(i)


def canvas_click(event):
    global clickCounter
    global saving_mode
    global obstructions
    global inbetweenCoords
    if saving_mode:
        x_coord = event.x
        y_coord = event.y
        clickCounter += 1
        if clickCounter == 1:
            inbetweenCoords = (x_coord, y_coord)
    if clickCounter == 2:
        saving_mode = False
        clickCounter = 0
        obstructions += [
            [(event.x, 500 - event.y), (inbetweenCoords[0], 500 - event.y),
             (inbetweenCoords[0], 500 - inbetweenCoords[1]),
             (event.x, 500 - inbetweenCoords[1])
             ]]
        canvas.create_rectangle(inbetweenCoords[0], inbetweenCoords[1], event.x, event.y,
                                fill="DeepSkyBlue", outline="blue",
                                tags="obstacle")  # Set outline to empty string for no border
        point2 = (event.x, event.y)
        addObstacleAsWalls(inbetweenCoords, point2)


obstructions = []
out = "0_0_0"
c, a = input("Arm,Forearm: ").split(',')
a = int(a)  # forearm
c = int(c)  # arm

if input("Arduino? y/n: ") == "y":

    print("arduino")
    for onePort in ports:
        portsList.append(str(onePort))
        print(str(onePort))
    val = input("Select Port: COM")
    # get wanted port from input
    portVar = ""
    for x in range(0, len(portsList)):
        if portsList[x].startswith("CM" + str(val)):
            portVar = "COM" + str(val)
            print(portVar)
    # change this \/ value for the port of the ARDUINO
    portVar = "COM" + input("COM")
    serialInst.baudrate = 9600
    serialInst.port = portVar
    serialInst.open()
    threading.Thread(target=executePeriodically).start()

window = Tk()
window.title("Moving Lines")
window.geometry("800x550")
createNodes(80, 55)
# Create a Canvas widget
canvas = Canvas(window, width=5000, height=5000)
canvas.pack()

center_x, center_y = 0, 500
radius = a + c
canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, outline="gray", width=2)

center_x, center_y = 0, 500
radius = abs(a - c)
canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, outline="gray", width=2)
# Draw the initial lines
arm = canvas.create_line(0, 500, c, 500, fill='red', width=2)
foreArm = canvas.create_line(c, 500, c + a, 500, fill='blue', width=2)
achse = canvas.create_line(0, 500, 1000000, 500, fill="black", width=2)
facingLine = canvas.create_line(0, 500, 20, 500, fill='green', width=2)
# Place the canvas in the background
canvas.place(relx=0, rely=0)

# Create the draggable label
label = Label(window, bg="blue", width=2, height=1)
label.place(x=0, y=500)

reset = Button(window, text="Reset", command=resetPos)
reset.place(x=0, y=40)

entry = Entry(window)
entry.place(x=0, y=60)
change = Button(window, text="Change Position", command=changePos)
change.place(x=0, y=80)

# rotation axis slider
slider = Scale(window, length=300, from_=-1, to=360, orient="horizontal", command=loopToZero)
slider.config(command=lambda num: (loopToZero(int(num))))
slider.place(x=500, y=0)

# facing direction slider
facing_slider = Scale(window, length=300, from_=90, to=-90, orient="vertical", command=updateFacing)
facing_slider.config(command=lambda num: (updateFacing(None)))
facing_slider.place(x=750, y=40)

# create new obstruction box
toggle_button = Button(window, text="create Obstacle", command=toggle_saving_mode)
toggle_button.place(x=700, y=0)

# Create a label to display the coordinates
coordinates_label = Label(window, text="(0, 0)")
coordinates_label.place(x=0, y=-20)  # Set a negative y-coordinate to place it above the label

anglesLabel = Label(window, text="A:0, B:0")
anglesLabel.place(x=0, y=20)
label.lift()

label.bind("<Button-1>", drag_start)
label.bind("<B1-Motion>", drag_motion)
canvas.bind("<Button-1>", canvas_click)
window.mainloop()
