import pygame
from pygame.locals import *
import os
import sys
import random
import pygame.surfarray as surfarray
from itertools import cycle

FPS = 30
SPEED = 5
WALL_SPEED = 10

#os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 700,500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font('DS-DIGIB.TTF',50)
small_font = pygame.font.Font('DS-DIGIB.TTF',30)
highscore = 0

IMAGES = {}

IMAGES['block'] = pygame.image.load('block.png').convert_alpha()

IMAGES['heli'] = (
    pygame.image.load('helicopter/1.1.png').convert_alpha(),
    pygame.image.load('helicopter/2.1.png').convert_alpha(),
    pygame.image.load('helicopter/3.1.png').convert_alpha()
    )

IMAGES['smoke'] = pygame.image.load('smoke.png').convert_alpha()

IMAGES['wall'] = (
    pygame.image.load('wallup.png').convert_alpha(),
    pygame.image.load('walldown.png').convert_alpha()
    )

PLAYER_INDEX_GEN = cycle([0, 1, 2, 1])
PLAYER_WIDTH = IMAGES['heli'][0].get_width()
PLAYER_HEIGHT = IMAGES['heli'][0].get_height()

class GameState:
    def __init__(self):
        self.score = self.playerIndex = self.loopIter = 0
        self.playerX = 200
        self.playerY = 200

        self.playerAnim = [IMAGES['heli'][i] for i in range(3)]
        self.playerIM = self.playerAnim[1]
        self.playerMask = pygame.mask.from_surface(self.playerIM,50)
        self.playerVel = SPEED

        newBlock = getRandomBlock(-100,300)

        self.blockIM = IMAGES['block']
        self.blockMask = pygame.mask.from_surface(self.blockIM,50)
        self.blocks = [{'x': newBlock['x'], 'y': newBlock['y']}]

        self.smokeIM = IMAGES['smoke']
        self.smokeX = self.playerX
        self.smokeY = self.playerY - 4
        self.smokes = [{'x': self.smokeX, 'y': self.smokeY}]

        self.blockVel = WALL_SPEED
        self.smokeVel = WALL_SPEED

        self.move = False

        #load wall images
        self.walluIM = IMAGES['wall'][0]
        self.walluMask = pygame.mask.from_surface(self.walluIM,50)
        self.walldIM = IMAGES['wall'][1]
        self.walldMask = pygame.mask.from_surface(self.walldIM,50)

        self.wallIMX = 0
        self.walluIMY = -100
        self.walldIMY = 400

    def frame_step(self, input_actions):
        pygame.event.pump()

        reward = 0.5
        terminal = False

        if sum(input_actions) != 1:
            raise ValueError('Multiple input actions!')

        if input_actions[1] == 1:
            self.move = True
        else:
            self.move = False

        # for event in pygame.event.get():
        #     if event.type == QUIT:
        #         pygame.quit()
        #         sys.exit()
        #     if event.type == MOUSEBUTTONDOWN:
        #         move = True
        #     if event.type == MOUSEBUTTONUP:
        #         move = False

        screen.fill(pygame.Color('black'))
        screen.blit(self.playerIM, (self.playerX, self.playerY))

        # player's movement
        if self.move:
            if self.playerVel > -4 and self.score%4==0:
                self.playerVel -= 4
        elif self.playerVel < 6 and self.score%3 == 0:
            self.playerVel += 4
        self.playerY += self.playerVel

        # playerIndex basex change
        if (self.loopIter + 1) % 3 == 0:
            self.playerIndex = next(PLAYER_INDEX_GEN)
        self.loopIter = (self.loopIter + 1) % 30

        #displaying the wall:
        self.walluIMY = -100+self.score*0.05
        self.walldIMY = 400-self.score*0.05

        if self.wallIMX > -1400:
            self.wallIMX -= WALL_SPEED
        else :
            self.wallIMX += 1390

        screen.blit(IMAGES['wall'][0],(self.wallIMX,self.walluIMY))
        screen.blit(IMAGES['wall'][1],(self.wallIMX,self.walldIMY))

        #block:
        for block in self.blocks:
            block['x'] -= self.blockVel
            screen.blit(IMAGES['block'],(block['x'],block['y']))

        if 45 < self.blocks[0]['x'] < 55:
            newBlock = getRandomBlock(self.walluIMY, self.walldIMY)
            self.blocks.append(newBlock)

        if 145 < self.blocks[0]['x'] < 155: 
            reward = 1

        if self.blocks[0]['x'] < -50:
            self.blocks.pop(0)

        #smoke:
        for smoke in self.smokes:
            smoke['x'] -= self.smokeVel
            screen.blit(IMAGES['smoke'],(smoke['x'] - random.randint(0,15),smoke['y']))

        if self.smokes[0]['x'] < self.playerX - 15:
            self.smokes.append({'x': self.playerX, 'y': self.playerY - 4})

        if self.smokes[0]['x'] < -15:
            self.smokes.pop(0)

        screen.blit(small_font.render('SCORE: %i'%self.score,False,pygame.Color(0,100,255)),(50,460))

        isCrash = check_collide(self.playerX,self.playerY,self.wallIMX,self.walluIMY,self.walldIMY,
            self.walluMask,self.walldMask,self.playerMask,self.blockMask,self.blocks)

        if isCrash:
            terminal = True
            self.__init__()
            reward = -1

        self.playerIM = self.playerAnim[self.score%3]

        image_data = pygame.surfarray.array3d(pygame.display.get_surface())
        crashIM = image_data[self.playerX:self.playerX+PLAYER_WIDTH+PLAYER_WIDTH/4, self.playerY-PLAYER_HEIGHT:self.playerY+PLAYER_HEIGHT*2].copy()
        crashIM[0:PLAYER_WIDTH, PLAYER_HEIGHT-10:PLAYER_HEIGHT*2+10] = (0,0,0)
        pygame.display.update()
        clock.tick(FPS)
        self.score += 1
        return image_data[self.playerX:,:].copy(), reward, terminal, crashIM
    

def check_collide(x, y, wallIMX, walluIMY, walldIMY, walluMask, walldMask, playerMask, blockMask, blocks):
    """uses masks to see if non-transparent pixels overlap"""
    #check if the wall has collided:
    wallOffsetX = x - wallIMX
    walluOffsetY = y - int(walluIMY)
    walldOffsetY = y - int(walldIMY)
    if walluMask.overlap(playerMask,(wallOffsetX,walluOffsetY)) or walldMask.overlap(playerMask,(wallOffsetX,walldOffsetY)):
        return True
    #check if the blocks have collided:
    offsetX = x - blocks[0]['x']
    offsetY = y - blocks[0]['y']
    overlap = blockMask.overlap(playerMask,(offsetX,offsetY))
    if overlap: return True

# def check_collide(x,y,playermask, blockmask, blocks):
#     """uses masks to see if non-transparent pixels overlap"""
#     #check if the wall has collided:
#     if y<0 or y>500:
#         return True
#     #check if the blocks have collided:
#     for block in blocks:
#         offset_x = x - block['x']
#         offset_y = y - block['y']
#         overlap = blockmask.overlap(playermask,(offset_x,offset_y))
#         if overlap: return True

def getRandomBlock(walluIMY, walldIMY):
    blockX = SCREEN_WIDTH #right out of view
    blockY = random.randint(int(walluIMY) + 200, int(walldIMY) - 100)
    return {'x': blockX, 'y': blockY}
