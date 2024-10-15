import pygame
import random
import math

import sys

sys.setrecursionlimit(10000)

from perlin_noise import PerlinNoise

CoolSeeds = [301]

RandomSeed = random.randrange(1,1000000)

print("Seed:",RandomSeed)

random.seed(RandomSeed)

noise1 = PerlinNoise(4,RandomSeed)
noise2 = PerlinNoise(8,RandomSeed)
noise3 = PerlinNoise(12,RandomSeed)
noise4 = PerlinNoise(16,RandomSeed)

ForestNoise = PerlinNoise(30,RandomSeed*math.pi)

RiverNoise = PerlinNoise(3,RandomSeed*math.pi**2)

# COLORS

WHITE = (255,255,255)
BLACK = (0,0,0)

# GRID DATA

MARGIN = 1

TileSize = 16
ScreenSize = 650

MainGrid = []

Islands = []

tiles = 100

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

CHARACTERSHEET = pygame.image.load("CHAR.png").convert()

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

class Character(pygame.sprite.Sprite):
    def __init__(self,name,HP,Player,Pos):
        super().__init__()
        self.Player = Player
        self.Name = name
        self.HP = HP or 20
        self.CurrentHP = self.HP
        self.MovementVector = (0,0)
        self.MaximumSpeed = 1.5
        self.Position = Pos
        self.CameraOffset = (0,0)

        self.image = pygame.Surface([TileSize,TileSize])
        self.image.blit(CHARACTERSHEET,(0,0),(0,0,TileSize,TileSize))
        self.image.set_colorkey(ColorKey)

        self.rect = self.image.get_rect()
        self.rect.x = self.Position[0]
        self.rect.y = self.Position[1]

    def update(self,GlobalOffset):

        if self.Player:

            Multi = 1

            if self.MovementVector[0] != 0 and self.MovementVector[1] != 0:
                Multi = math.pi/4

            self.Position = (self.Position[0]+self.MovementVector[0]*Multi,self.Position[1]+self.MovementVector[1]*Multi)

            if self.Position[0] <= 0:
                self.Position = (0,self.Position[1])
            if self.Position[1] <= 0:
                self.Position = (self.Position[0],0)

            if self.Position[0] >= TileSize*(tiles-1):
                self.Position = (TileSize*(tiles-1),self.Position[1])
                
            if self.Position[1] >= TileSize*(tiles-1):
                self.Position = (self.Position[0],TileSize*(tiles-1))
            
            self.rect.x = self.Position[0] - GlobalOffset[0]
            self.rect.y = self.Position[1] - GlobalOffset[1]

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

        self.images = [self.image]
        
        #pygame.draw.rect(self.image,Color,[0,0,TileSize,TileSize])

    def update(self,GlobalOffset):
        self.rect.x = self.Position[0] - GlobalOffset[0]
        self.rect.y = self.Position[1] - GlobalOffset[1]

    def ResetTexture(self,SPVALT):

        c = 0
        for image in self.images:
            image = image.blit(SPRITESHEET,(0,0),(SPVALT[c][0],SPVALT[c][1],TileSize,TileSize))
            SPVALT.pop(c)
            c += 1
        
        for SPVAL in SPVALT:
            img = pygame.Surface([TileSize,TileSize])
            #img.blit(SPRITESHEET,(0,0),(SPVAL[0],SPVAL[1],TileSize,TileSize))
            #self.images.append(img)
            
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
TotalList = pygame.sprite.Group()
CharacterList = pygame.sprite.Group()

# pygame

pygame.display.set_caption("grid time")

done = False
clock = pygame.time.Clock()

# CREATING GRID

for row in range(tiles):
    MainGrid.append([])
    for column in range(tiles):
        NOISE = (noise1([column/100,row/100]))
        NOISE += 0.5 * noise2([column/100,row/100])
        NOISE += .25 * noise3([column/100,row/100])
        NOISE += .125 * noise4([column/100,row/100])

        '''
        RN = RiverNoise([column/100,row/100])

        if RN > -0.02 and RN < 0.02:
            RN = 1 - RN * 10
        else:
            RN = 0
        
        NOISE -= RN
        '''
        
        NOISE = (NOISE + 1) / 2
        
        Color = (255 * NOISE,255 * NOISE,255 * NOISE)
        SpriteValue = None
        SpriteType = "Water"
        Sprite = None
        
        if NOISE <= .535:
            Color = (0,0,255)
            SpriteValue = SPRITES["Ocean"+str(random.randrange(1,3))]
            Sprite = "Water"
        elif NOISE <= .575:
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
        TotalList.add(NewTile)

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
                TotalList.add(Tree)
                Decorations.append(Tree)
            elif random.randrange(1,30) == 1:
                Flower = Decoration(Tile.Position[0],Tile.Position[1],(row,column),SPRITES["Flower"+str(random.randrange(1,5))],"Decoration","Flower")
                TileList.add(Flower)
                TotalList.add(Flower)
                Decorations.append(Flower)

'''
def SmoothEdges(tile):
    TileCoordinates = tile.GridCoordinate

    if TileCoordinates[0] + 1 >= len(MainGrid) or TileCoordinates[0] - 1 < 0:
        return
    if TileCoordinates[1] + 1 >= len(MainGrid[0]) or TileCoordinates[1] - 1 < 0:
        return

    if tile.Tile == "Grass":
        if MainGrid[TileCoordinates[0]+1][TileCoordinates[1]][0].Tile != "Grass":
            tile.ResetTexture([SPRITES["Sand1"],(17*2,17)])

for row in range(len(MainGrid)):
    for column in range(len(MainGrid[row])):
        Tile = MainGrid[row][column][0]

        SmoothEdges(Tile)
'''

# PLAYER

CTSOffset = ScreenSize/2-16 #character to screen offset

Player = Character("Player",20,True,(CTSOffset,CTSOffset))
TotalList.add(Player)

SetPlayerPos = False


while not SetPlayerPos:
    RandomTile = MainGrid[random.randrange(30,70)][random.randrange(30,70)][0]

    if RandomTile.SpriteType != "Water":
        SetPlayerPos = True
        Player.Position = RandomTile.Position

CameraOffset = (Player.Position[0]-ScreenSize/2+TileSize,Player.Position[1]-ScreenSize/2+TileSize)

# main program loop

while not done:

    PMS = Player.MaximumSpeed #player movement speed, i just didnt want code lines to be too long
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                Player.MovementVector = (PMS,Player.MovementVector[1])
            elif event.key == pygame.K_a:
                Player.MovementVector = (-PMS,Player.MovementVector[1])
            elif event.key == pygame.K_w:
                Player.MovementVector = (Player.MovementVector[0],-PMS)
            elif event.key == pygame.K_s:
                Player.MovementVector = (Player.MovementVector[0],PMS)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_d:
                Player.MovementVector = (0,Player.MovementVector[1])
            if event.key == pygame.K_s or event.key == pygame.K_w:
                Player.MovementVector = (Player.MovementVector[0],0)

    r = 0

    Multi = 1

    if Player.MovementVector[0] != 0 and Player.MovementVector[1] != 0:
        Multi = math.pi/4 # keeps diagonal movement magnitude equal to horizontal

    CameraOffset = (CameraOffset[0]+Player.MovementVector[0]*Multi,CameraOffset[1]+Player.MovementVector[1]*Multi)

    # camera stuff making it follow the player

    if CameraOffset[0] < 0:
        CameraOffset = (0,CameraOffset[1])
         
    elif CameraOffset[0] >= tiles * TileSize - ScreenSize:
        CameraOffset = (tiles * TileSize - ScreenSize, CameraOffset[1])

    if CameraOffset[1] <= 0:
        CameraOffset = (CameraOffset[0],0)
    elif CameraOffset[1] >= tiles * TileSize - ScreenSize:
        CameraOffset = (CameraOffset[0],tiles * TileSize - ScreenSize)

    # making sure player can go back from border

    if Player.Position[0] < ScreenSize/2 - TileSize:

        CameraOffset = (0,CameraOffset[1])
        
    elif Player.Position[0] > tiles*TileSize-ScreenSize/2:

        CameraOffset = (tiles*TileSize-ScreenSize,CameraOffset[1])

    if Player.Position[1] < ScreenSize/2-TileSize:

        CameraOffset = (CameraOffset[0],0)

    elif Player.Position[1] > tiles*TileSize-ScreenSize/2:

        CameraOffset = (CameraOffset[0],tiles*TileSize-ScreenSize)

    TotalList.update(CameraOffset)
    TotalList.draw(screen)

    for row in MainGrid:
        c = 0
        for column in row:
           # pygame.draw.rect(screen,column[0],[c*TileSize,r*TileSize,TileSize,TileSize])
            c += 1
        r += 1
    
    clock.tick(60)
    pygame.display.flip()
pygame.quit()
