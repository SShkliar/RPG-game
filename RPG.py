import pygame
import random

# COLORS

WHITE = (255,255,255)
BLACK = (0,0,0)

# WORLD

CameraOffset = (0,0)
CameraMovement = (0,0)

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
    def __init__(self,x,y):
        super().__init__()
        self.Position = (x,y)
        
        self.image = pygame.Surface([TileSize,TileSize])
        self.image.fill(BLACK)
        #self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.x = self.Position[0]
        self.rect.y = self.Position[1]
        
        pygame.draw.rect(self.image,random.choice([WHITE,BLACK]),[0,0,TileSize,TileSize])

    def update(self,GlobalOffset):
        self.rect.x = self.Position[0] - GlobalOffset[0]
        self.rect.y = self.Position[1] - GlobalOffset[1]
# LISTS

TileList = pygame.sprite.Group()

# GRID

TileSize = 25
ScreenSize = 500

MainGrid = []

tiles = 100#int(ScreenSize/TileSize)

for row in range(tiles):
    MainGrid.append([])
    for column in range(tiles):
        NewTile = Tile(column*TileSize,row*TileSize)
        MainGrid[row].append([NewTile])
        TileList.add(NewTile)
# PLAYER

Player = Character("Player",20)

# pygame

pygame.init()
screen = pygame.display.set_mode([500,500])

pygame.display.set_caption("grid time")

done = False
clock = pygame.time.Clock()

# main program loop

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                CameraMovement = (3,CameraMovement[1])

    r = 0

    CameraOffset = (CameraOffset[0]+CameraMovement[0],CameraOffset[1]+CameraMovement[1])

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
