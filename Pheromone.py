from math import *
from random import randint


class World:

    def __init__(self, width, scoutRobotsNumber, workerRobotsNumber, decreaseRate):
        self.pheromones = [[0 for i in range(width)] for j in range(width)]
        self.width = width

        self.decreaseRate = decreaseRate

        self.workerRobotsNumber = workerRobotsNumber
        self.scoutRobotsNumber = scoutRobotsNumber

        self.swarm = [0, 0]
        self.energy = [0, 0]

        self.getEnergy = 0

        self.letGoWorkerRobots = False

        self.pathFound = False
        self.lastFoundPath = []
        self.commonPathsNumber = 0

        while (abs(self.swarm[0] - self.energy[0]) + (abs(self.swarm[1] - self.energy[1]))) < self.width:
            self.swarm = (randint(0, self.width - 1), randint(0, self.width - 1))
            self.energy = (randint(0, self.width - 1), randint(0, self.width - 1))

        self.robots = []

        for i in range(self.workerRobotsNumber):
            newRobot = Robot(1, self.swarm)
            self.robots.append(newRobot)

        for i in range(self.scoutRobotsNumber):
            newRobot = Robot(0, self.swarm)
            self.robots.append(newRobot)

    def realOptimalDistance(self):
        lengthRealOptimalDistance = 0
        position = [self.energy[0], self.energy[1]]
        finalPosition = [self.swarm[0], self.swarm[1]]

        while position != finalPosition:

            if position[0] != finalPosition[0]:
                if position[0] < finalPosition[0]:
                    position[0] = position[0] + 1
                else:
                    position[0] = position[0] - 1

            if position[1] != finalPosition[1]:
                if position[1] < finalPosition[1]:
                    position[1] = position[1] + 1
                else:
                    position[1] = position[1] - 1

            lengthRealOptimalDistance = lengthRealOptimalDistance + 1

        return lengthRealOptimalDistance

    def returningRobotsNumberPerCell(self):

        robotsNumber = [[0 for i in range(self.width)] for j in range(self.width)]

        for i in range(len(self.robots)):
            if self.robots[i].returning:
                robotsNumber[self.robots[i].X][self.robots[i].Y] = robotsNumber[self.robots[i].X][self.robots[i].Y] + 1

        return robotsNumber

    def robotsNumberPerCell(self):

        robotsNumber = [[0 for i in range(self.width)] for j in range(self.width)]

        for i in range(len(self.robots)):
            robotsNumber[self.robots[i].X][self.robots[i].Y] = robotsNumber[self.robots[i].X][self.robots[i].Y] + 1

        return robotsNumber

    def listAuthorizedCellsAround(self, robot):

        Ax = robot.X
        Ay = robot.Y

        returning = robot.returning

        cellsList = []

        for i in range(-1, 2):
            newX = Ax + i
            if newX >= 0 and newX < self.width:
                for j in range(-1, 2):
                    newY = Ay + j
                    if newY >= 0 and newY < self.width:
                        if i != 0 or j != 0:
                            if (not returning and not (newX == self.swarm[0] and newY == self.swarm[1])) or (
                                    returning and not (newX == self.energy[0] and newY == self.energy[1])):

                                if not ([newX, newY] in robot.visitedCells):
                                    cellsList.append([newX, newY])

        return cellsList

    def chooseInterestingCellAround(self, robotNumber):

        robot = self.robots[robotNumber]

        decision = None
        pheromoneSum = 0

        possibleDecisions = self.listAuthorizedCellsAround(robot)
        if len(possibleDecisions) == 0:
            self.robots[robotNumber].visitedCells = []
            possibleDecisions = self.listAuthorizedCellsAround(robot)

        for i in range(len(possibleDecisions)):
            X = possibleDecisions[i][0]
            Y = possibleDecisions[i][1]
            if (X == self.swarm[0] and Y == self.swarm[1] and robot.returning) or (
                    X == self.energy[0] and Y == self.energy[1] and not robot.returning):

                decision = [X, Y]
                break
            else:
                pheromoneSum = pheromoneSum + self.pheromones[X][Y]

        if decision != None:
            return decision

        probabilitiesList = [None for i in range(len(possibleDecisions))]
        if pheromoneSum == 0:
            decisionNumber = randint(0, len(possibleDecisions) - 1)
            decision = possibleDecisions[decisionNumber]

        else:
            probability = 0
            choosenProbability = randint(0, 99) / 100
            for i in range(0, len(possibleDecisions)):
                X = possibleDecisions[i][0]
                Y = possibleDecisions[i][1]
                pheromones = self.pheromones[X][Y]
                probability += (pheromones / pheromoneSum)
                if probability > choosenProbability:
                    decision = possibleDecisions[i]
                    break
        return decision

    def moveRobots(self):

        for i in range(len(self.robots)):

            if self.robots[i].robotType == 1:

                if self.letGoWorkerRobots:
                    newPosition = self.chooseInterestingCellAround(i)

                    self.robots[i].visitedCells.append([self.robots[i].X, self.robots[i].Y])
                    self.robots[i].X = newPosition[0]
                    self.robots[i].Y = newPosition[1]


            elif self.robots[i].robotType == 0 and not (
                    self.robots[i].X == self.swarm[0] and self.robots[i].Y == self.swarm[1] and self.robots[
                i].returning == True):

                moveX = 0
                moveY = 0

                for j in range(-1, 2):
                    newX = self.robots[i].X + j
                    for k in range(-1, 2):
                        newY = self.robots[i].Y + k
                        if (self.robots[i].returning and newX == self.swarm[0] and newY == self.swarm[1]) or (
                                not self.robots[i].returning and newX == self.energy[0] and newY == self.energy[1]):
                            moveX = j
                            moveY = k

                while (moveX == 0 and moveY == 0) or (self.robots[i].X + moveX) < 0 or (self.robots[i].Y + moveY) < 0 or (
                        self.robots[i].X + moveX) >= self.width or (self.robots[i].Y + moveY) >= self.width:
                    moveX = randint(-1, 1)
                    moveY = randint(-1, 1)

                self.robots[i].visitedCells.append([self.robots[i].X, self.robots[i].Y])
                self.robots[i].X = self.robots[i].X + moveX
                self.robots[i].Y = self.robots[i].Y + moveY

            self.changeRobotState(i)

    def changeRobotState(self, robotNumber):

        if self.robots[robotNumber].X == self.energy[0] and self.robots[robotNumber].Y == self.energy[1]:
            self.robots[robotNumber].returning = True
            self.robots[robotNumber].visitedCells = []

        elif self.robots[robotNumber].X == self.swarm[0] and self.robots[robotNumber].Y == self.swarm[1]:

            if self.robots[robotNumber].returning:

                if self.robots[robotNumber].robotType == 0 and self.letGoWorkerRobots == False:
                    self.letGoWorkerRobots = True

                elif self.robots[robotNumber].robotType == 1:

                    self.getEnergy = self.getEnergy + 1

                    if self.robots[robotNumber].visitedCells == self.lastFoundPath:
                        self.commonPathsNumber = self.commonPathsNumber + 1
                    else:
                        self.commonPathsNumber = 1
                        self.lastFoundPath = self.robots[robotNumber].visitedCells

                self.robots[robotNumber].returning = False
                self.robots[robotNumber].visitedCells = []

    def leaveAllPheromones3(self):

        robotsNumber = self.returningRobotsNumberPerCell()

        for i in range(self.width):
            for j in range(self.width):
                self.pheromones[i][j] = ((1 - self.decreaseRate) * self.pheromones[i][j]) + robotsNumber[i][j] ** (
                    self.width)

    def leaveAllPheromones4(self):

        addedPheromones = [[0 for i in range(self.width)] for j in range(self.width)]

        for i in range(len(self.robots)):

            if 1:
                addedPheromones[self.robots[i].X][self.robots[i].Y] = addedPheromones[self.robots[i].X][self.robots[i].Y] + (
                            1 / (len(self.robots[i].visitedCells) + 1)) ** (self.width)

        for i in range(self.width):
            for j in range(self.width):
                self.pheromones[i][j] = ((1 - self.decreaseRate) * self.pheromones[i][j]) + addedPheromones[i][j] ** (
                    self.width)

    def checkConvergence(self):

        if self.commonPathsNumber > self.workerRobotsNumber / 4:
            self.pathFound = True

    def loop(self):

        self.moveRobots()
        self.leaveAllPheromones3()
        self.checkConvergence()


class Robot:

    def __init__(self, robotType, swarmCoordinates):
        self.robotType = robotType

        if self.robotType == 0:
            self.robotName = "Scout"
        elif self.robotType == 1:
            self.robotName = "Worker"

        self.X = swarmCoordinates[0]
        self.Y = swarmCoordinates[1]

        self.returning = False

        self.visitedCells = []

