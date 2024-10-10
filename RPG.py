import pygame
import random
import math

import sys

sys.setrecursionlimit(10000)

from perlin_noise import PerlinNoise

RandomSeed = 1

random.seed(RandomSeed)

noise1 = PerlinNoise(4,RandomSeed)
noise2 = PerlinNoise(8,RandomSeed)
noise3 = PerlinNoise(12,RandomSeed)
noise4 = PerlinNoise(16,RandomSeed)

ForestNoise = PerlinNoise(30,RandomSeed*math.pi)

# COLORS

WHITE = (255,255,255)
BLACK = (0,0,0)

# GRID DATA

MARGIN = 1

TileSize = 16
ScreenSize = 800

# WORLD

CameraOffset = (0,0)
CameraMovement = (0,0)

# START

pygame.init()
screen = pygame.display.set_mode([ScreenSize,ScreenSize])

pygame.display.set_caption("loading")

# SPRITESHEET

SPRITESHEET = pygame.image.load("SPRITESHEET.png").convert()
ColorKey = (255,0,255)

SPRITES = {
    "Ocean1": (0,0),
    "Ocean2": (16+1,0,),
    "Grass1": (16*5+5,0),
    "Grass2": (16*5+5,17),
    "Sand1": (16*8+8,0),
    "Sand2": (16*8+8,17),
    "Rock1": (16*7+7,0),
    "Rock2": (16*7+7,17),
    "Flower1": (16*28+28,16*9+9),
    "Flower2": (16*29+29,16*9+9),
    "Flower3": (16*30+30,16*9+9),
    "Flower4": (16*31+31,16*9+9),
    "Tree1": (17*13,17*9),
    "Tree2": (17*16,17*9),
    "Tree3": (17*23,17*9),
    "Bush1": (17*24,17*9)
    }

# CLASSES

class Character():
    def __init__(self,name,HP):
        self.Player = False
        self.Name = name
        self.HP = HP or 20
        self.CurrentHP = self.HP
        self.MovementVector = (0,0)
        self.MaximumSpeed = 3

class Tile(pygame.sprite.Sprite):
    def __init__(self,x,y,GridCoord,Color,SpriteValue,Type,SPRITE):
        super().__init__()
        self.Position = (x,y)
        self.Color = Color

        self.GridCoordinate = GridCoord

        self.SpriteValue = SpriteValue
        self.SpriteType = Type

        self.Tile = SPRITE

        self.image = pygame.Surface([TileSize,TileSize])
        self.image.blit(SPRITESHEET,(0,0),(SpriteValue[0],SpriteValue[1],TileSize,TileSize))
        
        self.rect = self.image.get_rect()
        self.rect.x = self.Position[0]
        self.rect.y = self.Position[1]
        
        #pygame.draw.rect(self.image,Color,[0,0,TileSize,TileSize])

    def update(self,GlobalOffset):
        self.rect.x = self.Position[0] - GlobalOffset[0]
        self.rect.y = self.Position[1] - GlobalOffset[1]

    def ResetTexture(self,SPVAL):
        self.image.blit(SPRITESHEET,(0,0),(SPVAL[0],SPVAL[1],TileSize,TileSize))

class Decoration(pygame.sprite.Sprite):
    def __init__(self,x,y,GridCoord,SpriteValue,Type,Sprite):
        super().__init__()

        self.Position = (x,y)

        self.SpriteValue = SpriteValue
        self.SpriteType = Type

        self.GridCoordinate = GridCoord

        self.Tile = Sprite

        self.image = pygame.Surface([TileSize,TileSize])
        self.image.blit(SPRITESHEET,(0,0),(SpriteValue[0],SpriteValue[1],TileSize,TileSize))

        self.image.set_colorkey(ColorKey)
        
        self.rect = self.image.get_rect()
        self.rect.x = self.Position[0]
        self.rect.y = self.Position[1]
        
    def update(self,GlobalOffset):
        self.rect.x = self.Position[0] - GlobalOffset[0]
        self.rect.y = self.Position[1] - GlobalOffset[1]
# LISTS

TileList = pygame.sprite.Group()

# pygame

pygame.display.set_caption("grid time")

done = False
clock = pygame.time.Clock()

# CREATING GRID

MainGrid = []

Islands = []

tiles = 100#int(ScreenSize/TileSize)

for row in range(tiles):
    MainGrid.append([])
    for column in range(tiles):
        NOISE = (noise1([column/100,row/100]))
        NOISE += 0.5 * noise2([column/100,row/100])
        NOISE += .25 * noise3([column/100,row/100])
        NOISE += .125 * noise4([column/100,row/100])

        NOISE = (NOISE + 1) / 2
        
        Color = (255 * NOISE,255 * NOISE,255 * NOISE)
        SpriteValue = None
        SpriteType = "Water"
        Sprite = None
        
        if NOISE <= .5:
            Color = (0,0,255)
            SpriteValue = SPRITES["Ocean"+str(random.randrange(1,3))]
            Sprite = "Water"
        elif NOISE <= .57:
            SpriteType = "Land"
            Color = (255,255,0)
            SpriteValue = SPRITES["Sand"+str(random.randrange(1,3))]
            Sprite = "Sand"
        elif NOISE <= .73:
            SpriteType = "Land"
            Color = (0,255,0)
            SpriteValue = SPRITES["Grass"+str(random.randrange(1,3))]
            Sprite = "Grass"
        else:
            SpriteType = "Land"
            Color = (122,122,122)
            SpriteValue = SPRITES["Rock"+str(random.randrange(1,3))]
            Sprite = "Mountain"
        
        NewTile = Tile(row*TileSize,column*TileSize,(row,column),Color,SpriteValue,SpriteType,Sprite)
        MainGrid[row].append([NewTile,[]])
        TileList.add(NewTile)

def PartOfIsland(coord):

    IsInIsland = False
    
    for island in Islands:
        if not island:
            return True
        for tile in island:
            if tile[0] == coord[0] and tile[1] == coord[1]: #means same tile as one we found
                IsInIsland = True

    return IsInIsland

def GetAdjacentLandmass(ISLANDTABLE,coord,TABLEID):
    AdjacentTiles = []

    if coord[0] <= 0 or coord[1] <= 0:
        return ISLANDTABLE

    for x in range(-1,2,2):
        if coord[0]+x > len(MainGrid)-1:
            continue
        Tile = MainGrid[coord[0]+x][coord[1]][0]
        if Tile.SpriteType == "Land" and not PartOfIsland(([coord[0]+x],[coord[1]])):
            AdjacentTiles.append(Tile)
    for y in range(-1,2,2):
        if coord[1]+y > len(MainGrid)-1:
            continue
        Tile = MainGrid[coord[0]][coord[1]+y][0]
        if Tile.SpriteType == "Land" and not PartOfIsland(([coord[0]],[coord[1]+y])):
            AdjacentTiles.append(Tile)

    for tile in AdjacentTiles:
        Islands[TABLEID].append(tile.GridCoordinate)
        GetAdjacentLandmass(ISLANDTABLE,tile.GridCoordinate,TABLEID)

    return ISLANDTABLE

'''
for column in range(len(MainGrid)):
    for row in range(len(MainGrid[column])):   
        TileData = MainGrid[column][row]
        Tile = TileData[0]

        IsInIsland = PartOfIsland((column,row))
        
        if IsInIsland:
            continue
        
        ISLANDTABLE = []
        ISLANDTABLE.append((column,row))

        Islands.append(ISLANDTABLE)

        TableID = len(Islands)-1

        GetAdjacentLandmass(ISLANDTABLE,(column,row),TableID)
'''

for row in range(len(MainGrid)):
    for column in range(len(MainGrid[row])):
        TileData = MainGrid[row][column]
        Tile = TileData[0]

        Decorations = TileData[1]

        if Tile.Tile == "Grass":
            FN = ((ForestNoise([row/100,column/100])) + 1) / 2
            if FN > .55 and random.randrange(1,8) < 7:
                Tree = Decoration(Tile.Position[0],Tile.Position[1],(row,column),SPRITES["Tree"+str(random.randrange(1,4))],"Decoration","Tree")
                TileList.add(Tree)
                Decorations.append(Tree)
            elif random.randrange(1,30) == 1:
                Flower = Decoration(Tile.Position[0],Tile.Position[1],(row,column),SPRITES["Flower"+str(random.randrange(1,5))],"Decoration","Flower")
                TileList.add(Flower)
                Decorations.append(Flower)
# PLAYER

Player = Character("Player",20)

# main program loop

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                CameraMovement = (3,CameraMovement[1])
            elif event.key == pygame.K_a:
                CameraMovement = (-3,CameraMovement[1])
            elif event.key == pygame.K_w:
                CameraMovement = (CameraMovement[0],-3)
            elif event.key == pygame.K_s:
                CameraMovement = (CameraMovement[0],3)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_d:
                CameraMovement = (0,CameraMovement[1])
            if event.key == pygame.K_s or event.key == pygame.K_w:
                CameraMovement = (CameraMovement[0],0)

    r = 0

    CameraOffset = (CameraOffset[0]+CameraMovement[0],CameraOffset[1]+CameraMovement[1])

    if CameraOffset[0] < 0:
        CameraOffset = (0,CameraOffset[1])
    elif CameraOffset[0] > tiles * TileSize - ScreenSize:
        CameraOffset = (tiles * TileSize - ScreenSize, CameraOffset[1])

    if CameraOffset[1] < 0:
        CameraOffset = (CameraOffset[0],0)
    elif CameraOffset[1] > tiles * TileSize - ScreenSize:
        CameraOffset = (CameraOffset[0],tiles * TileSize - ScreenSize)

    TileList.update(CameraOffset)
    TileList.draw(screen)
    
    for row in MainGrid:
        c = 0
        for column in row:
           # pygame.draw.rect(screen,column[0],[c*TileSize,r*TileSize,TileSize,TileSize])
            c += 1
        r += 1
    
    clock.tick(60)
    pygame.display.flip()
pygame.quit()
