nodes = {}


class Node:
    def __init__(self, pX, pY):
        self.coords = (pX, pY)
        self.isWall = False
        self.parent = None
        self.hCost = 0
        self.gCost = 0
        self.fCost = 0

    def setGCost(self, goal):
        goalX, goalY = goal
        selfX, selfY = self.coords
        x = abs(goalX - selfX)
        y = abs(goalY - selfY)
        self.gCost = (min(x, y) * 14) + ((max(x, y) - min(x, y)) * 10)
        self.fCost = self.gCost + self.hCost

    def setHCost(self, pHCost):
        self.hCost = pHCost
        self.fCost = self.gCost + self.hCost

    def setFCost(self, goal):
        self.setGCost(goal)
        goalX, goalY = goal  # Unpack goal coordinates from the tuple
        if self.parent is None:
            self.hCost = self.gCost
            return
        if self.parent.coords[0] == self.coords[0] or self.parent.coords[1] == self.coords[1]:
            distance = 10
        else:
            distance = 14
        self.hCost = self.parent.hCost + distance
        self.fCost = self.gCost + self.hCost


def getLowestOpen(open):
    out = open[0]

    for i in open:
        if i.fCost == out.fCost:
            if i.gCost < out.gCost:
                out = i
        elif i.fCost < out.fCost:
            out = i
    return out


def addWall(nodeName):
    global nodes
    if nodeName in nodes:
        nodes[nodeName].isWall = True
    else:
        print("you fucked up")

def createNodes(l, w):
    global nodes

    for i in range(l):
        for j in range(w):
            node_name = f"Node{i}{j}"  # Create a variable name
            nodes[node_name] = Node(i, j)  # Store the Node instance in the dictionary

    return nodes


def neighboursOf(node):
    global nodes
    out = []
    x, y = node.coords  # Fixed the variable assignment
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            new_x, new_y = x + i, y + j
            name = f"Node{new_x}{new_y}"  # Fixed the variable assignment
            if name in nodes:
                out.append(nodes[name])  # Appending the node to the list
    return out


def calculateHCost(node, goal):
    node.setGCost(goal)
    goalX, goalY = goal  # Unpack goal coordinates from the tuple
    if node.parent is None:
        return node.gCost
    if node.parent.coords[0] == node.coords[0] or node.parent.coords[1] == node.coords[1]:
        distance = 10
    else:
        distance = 14
    return node.parent.hCost + distance


def returnObjects(node, start):
    current = node
    nodeCoords = []
    while current.parent is not None:
        x, y = current.coords
        nodeCoords += [(x, y)]
        current = current.parent
    nodeCoords += [tuple(start)]
    return nodeCoords


def addWalls(nodes):
    ''''
    while True:
        inp = input("Wall Coordinates(x,y): ")
        if inp == "exit":
            return
        x, y = inp.split(',')
        nodeName = f"Node{x}{y}"
        if nodeName in nodes:
            nodes[nodeName].isWall = True
    '''
    pass


def findPath(goal, start):
    global nodes
    addWalls(nodes)
    startNode = f"Node{start[0]}{start[1]}"
    nodes[startNode].parent = None
    open = [nodes[startNode]]
    closed = []
    while True:
        current = getLowestOpen(open)
        open.remove(current)
        closed.append(current)

        if current.coords == goal:
            print(returnObjects(current, start))
            return
        for i in neighboursOf(current,):
            if i.isWall or i in closed:
                continue

            if i.hCost > calculateHCost(i, goal) or i not in open:
                i.parent = current
                i.setFCost(goal)
                if i not in open:
                    open.append(i)
