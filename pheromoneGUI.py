import Pheromone
import pygame
from pygame.locals import *
from time import sleep
import argparse


class Screen:

    def __init__(self, L, swarm, energy, elementSize=80, borderSize=1, margin=20):
        self.L = L

        self.swarm = swarm
        self.energy = energy

        self.elementSize = elementSize
        self.borderSize = borderSize

        self.margin = margin

        self.ScreenLength = L * (self.elementSize + self.borderSize) + 2 * self.margin
        self.XText = self.margin / 2
        self.YText = self.margin / 4
        self.SXText = 0
        self.SYText = 0

        self.window = None

        self.basicRect = pygame.Surface(
            (self.elementSize + 2 * self.borderSize, self.elementSize + 2 * self.borderSize))
        self.basicRect.fill(Color("black"))

        self.innerRect = pygame.Surface((self.elementSize, self.elementSize))
        self.innerRect.fill(Color("white"))
        self.basicRect.blit(self.innerRect, (self.borderSize, self.borderSize))

        pygame.init()
        self.opened = False

        self.font = pygame.font.Font(pygame.font.get_default_font(), 14)

    def drawText(self, text, X, Y, SX, SY):

        pygame.draw.rect(self.window, Color("white"), (X, Y, SX, SY))
        self.window.blit(self.font.render(text, True, Color("black")), (X, Y))
        return self.font.size(text)

    def startScreen(self):
        self.window = pygame.display.set_mode((self.ScreenLength, self.ScreenLength))
        pygame.display.set_caption("Swarm Robots GUI")

        self.window.fill(Color("white"))

        X = self.margin

        for i in range(self.L):
            for j in range(self.L):
                coords = self.getPygameCornerOfCell(i, j)
                self.window.blit(self.basicRect, coords)

        swarmCoords = self.getPygameCornerOfCell(self.swarm[0], self.swarm[1])
        self.changeInnerRectColor("brown")
        self.window.blit(self.basicRect, swarmCoords)

        energyCoords = self.getPygameCornerOfCell(self.energy[0], self.energy[1])
        self.changeInnerRectColor("green")
        self.window.blit(self.basicRect, energyCoords)

        pygame.display.update()
        self.opened = True

    def getPygameCornerOfCell(self, cellX, cellY):

        PosX = cellX * (self.elementSize + self.borderSize) + self.margin

        PosY = self.L - cellY - 1
        PosY = PosY * (self.elementSize + self.borderSize) + self.margin

        return PosX, PosY

    def changeInnerRectColor(self, color="white"):

        if isinstance(color, tuple):
            if color[0] > 255:
                color = (255, color[1], color[2])
            if color[1] > 255:
                color = (color[0], 255, color[2])
            if color[2] > 255:
                color = (color[0], color[1], 255)
            if color[0] < 0:
                color = (0, color[1], color[2])
            if color[1] < 0:
                color = (color[0], 0, color[2])
            if color[2] < 0:
                color = (color[0], color[1], 0)
            self.innerRect.fill(Color(color[0], color[1], color[2], 255))
        else:
            self.innerRect.fill(Color(color))
        self.basicRect.blit(self.innerRect, (self.borderSize, self.borderSize))

    def updateScore(self, score):

        pos = self.drawText("Round trip(s) : {}".format(score), self.XText, self.YText, self.SXText, self.SYText)
        self.SXText = pos[0]
        self.SYText = pos[1]

    def updatePheromones(self, pheromones):

        for i in range(len(pheromones)):
            for j in range(len(pheromones)):

                if not ((i == self.swarm[0] and j == self.swarm[1]) or (i == self.energy[0] and j == self.energy[1])):
                    cellCoords = self.getPygameCornerOfCell(i, j)
                    rgb = 255 - round(pheromones[i][j])
                    self.changeInnerRectColor((rgb, rgb, rgb))
                    self.window.blit(self.basicRect, cellCoords)

    def updateRobots(self, robots):

        for i in range(len(robots)):
            for j in range(len(robots)):
                if not ((i == self.swarm[0] and j == self.swarm[1]) or (i == self.energy[0] and j == self.energy[1])):
                    cellCoords = self.getPygameCornerOfCell(i, j)
                    rgb = 255 - round(robots[i][j]) * 10
                    self.changeInnerRectColor((rgb, rgb, rgb))
                    self.window.blit(self.basicRect, cellCoords)

    def listen(self):
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                self.opened = False
                pygame.quit()


def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("argument needs to be positive")
    return ivalue


def check_0_1(value):
    fvalue = float(value)
    if fvalue < 0 or fvalue > 1:
        raise argparse.ArgumentTypeError("argument needs to be between 0 and 1")
    return fvalue


parser = argparse.ArgumentParser("Console.py",
                                 description="Runs a simulation of the algorithm and displays the resulted path.")
parser.add_argument("--width", help="Side size of the world. (Default: 10)", type=check_positive)
parser.add_argument("-s", "--scouts", help="Number of scout robots. (Default: width)", type=check_positive)
parser.add_argument("-w", "--workers", help="Number of worker robots. (Default: 10*width)", type=check_positive)
parser.add_argument("-r", "--rate", help="Pheromones decrease rate between 0 and 1. (Default: 0.7)", type=check_0_1)
args = parser.parse_args()

if args.width:
    width = args.width
else:
    width = 10

if args.scouts:
    scoutRobots = args.scouts
else:
    scoutRobots = width

if args.workers:
    workerRobots = args.workers
else:
    workerRobots = 10 * width

if args.rate:
    decreaseRate = args.rate
else:
    decreaseRate = 0.7

world = Pheromone.World(width, scoutRobots, workerRobots, decreaseRate)
screen = Screen(world.width, world.swarm, world.energy)
screen.startScreen()

while screen.opened:
    world.loop()
    screen.updateRobots(world.robotsNumberPerCell())
    screen.updateScore(world.getEnergy)
    pygame.display.update()
    screen.listen()
    sleep(0.016)
