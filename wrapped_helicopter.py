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

IMAGES['block'] = pygame.image.load('block2.png').convert_alpha()

IMAGES['heli'] = (
    pygame.image.load('helicopter/1.1.1.png').convert_alpha(),
    pygame.image.load('helicopter/2.1.1.png').convert_alpha(),
    pygame.image.load('helicopter/3.1.1.png').convert_alpha()
    )

IMAGES['smoke'] = pygame.image.load('smoke2.png').convert_alpha()

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
        self.playerx = 200
        self.playery = 200

        self.playeranim = [IMAGES['heli'][i] for i in range(3)]
        self.playerim = self.playeranim[1]
        self.playermask = pygame.mask.from_surface(self.playerim,50)
        self.playerVel = SPEED

        newBlock = getRandomBlock(-100,300)

        self.blockim = IMAGES['block']
        self.blockmask = pygame.mask.from_surface(self.blockim,50)
        self.blocks = [{'x': newBlock['x'], 'y': newBlock['y']}]

        self.smokeim = IMAGES['smoke']
        self.smokex = self.playerx
        self.smokey = self.playery - 4
        self.smokes = [{'x': self.smokex, 'y': self.smokey}]

        self.blockVel = WALL_SPEED
        self.smokeVel = WALL_SPEED

        self.move = False

        #load wall images
        self.walluim = IMAGES['wall'][0]
        self.wallumask = pygame.mask.from_surface(self.walluim,50)
        self.walldim = IMAGES['wall'][1]
        self.walldmask = pygame.mask.from_surface(self.walldim,50)

        self.wall_image_x = 0
        self.wall_image_u_y = -100
        self.wall_image_u_y = 400

    def frame_step(self, input_actions):
        pygame.event.pump()

        reward = 0.1
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
        screen.blit(self.playerim, (self.playerx, self.playery))

        # player's movement
        if self.move:
            if self.playerVel > -4 and self.score%4==0:
                self.playerVel -= 4
        elif self.playerVel < 6 and self.score%3 == 0:
            self.playerVel += 4
        self.playery += self.playerVel

        # playerIndex basex change
        if (self.loopIter + 1) % 3 == 0:
            self.playerIndex = next(PLAYER_INDEX_GEN)
        self.loopIter = (self.loopIter + 1) % 30

        #displaying the wall:
        self.wall_image_u_y = -100+self.score*0.05
        self.wall_image_d_y = 400-self.score*0.05

        if self.wall_image_x > -1400:
            self.wall_image_x -= WALL_SPEED
        else :
            self.wall_image_x += 1390

        screen.blit(IMAGES['wall'][0],(self.wall_image_x,self.wall_image_u_y))
        screen.blit(IMAGES['wall'][1],(self.wall_image_x,self.wall_image_d_y))

        #blocks:
        for block in self.blocks:
            block['x'] -= self.blockVel
            screen.blit(IMAGES['block'],(block['x'],block['y']))

        if 45 < self.blocks[0]['x'] < 55:
            newBlock = getRandomBlock(self.wall_image_u_y, self.wall_image_d_y)
            self.blocks.append(newBlock)

        if 145 < self.blocks[0]['x'] < 155: 
            reward = 1

        if self.blocks[0]['x'] < -50:
            self.blocks.pop(0)

        #smoke:
        for smoke in self.smokes:
            smoke['x'] -= self.smokeVel
            screen.blit(IMAGES['smoke'],(smoke['x'] - random.randint(0,15),smoke['y']))

        if self.smokes[0]['x'] < self.playerx - 15:
            self.smokes.append({'x': self.playerx, 'y': self.playery - 4})

        if self.smokes[0]['x'] < -15:
            self.smokes.pop(0)

        screen.blit(small_font.render('SCORE: %i'%self.score,False,pygame.Color(0,100,255)),(50,460))

        isCrash = check_collide(self.playerx,self.playery,self.wall_image_x,self.wall_image_u_y,self.wall_image_d_y,
            self.wallumask,self.walldmask,self.playermask,self.blockmask,self.blocks)

        #isCrash = check_collide(self.playerx,self.playery,self.playermask,self.blockmask,self.blocks)

        if isCrash:
            terminal = True
            self.__init__()
            reward = -1

        # if check_collide(helicopter,wall_image_x,wall_prime_x, prime_mask, wall_mask, helicopter_mask, blocks):
        #     pygame.draw.circle(screen, pygame.Color('red'), (helicopter.x+39,helicopter.y+18), 60, 3)
        #     pygame.display.update()
        #     while not restart:
        #         for event in pygame.event.get():
        #             if event.type == QUIT:
        #                 pygame.quit()
        #                 sys.exit()
        #             if event.type == MOUSEBUTTONDOWN:
        #                 restart = True


        self.playerim = self.playeranim[self.score%3]

        image_data = pygame.surfarray.array3d(pygame.display.get_surface())
        crash_img = image_data[self.playerx:self.playerx+PLAYER_WIDTH+PLAYER_WIDTH/4, self.playery-PLAYER_HEIGHT:self.playery+PLAYER_HEIGHT*2].copy()
        crash_img[0:PLAYER_WIDTH, PLAYER_HEIGHT-10:PLAYER_HEIGHT*2+10] = (0,0,0)
        pygame.display.update()
        clock.tick(FPS)
        self.score += 1
        return image_data[self.playerx:,:].copy(), reward, terminal, crash_img
    

def check_collide(x, y, wall_image_x, wall_image_u_y, wall_image_d_y, wallumask, walldmask, playermask, blockmask, blocks):
    """uses masks to see if non-transparent pixels overlap"""
    #check if the wall has collided:
    wall_offset_x = x - wall_image_x
    wall_u_offset_y = y - int(wall_image_u_y)
    wall_d_offset_y = y - int(wall_image_d_y)
    offset_y = y
    if wallumask.overlap(playermask,(wall_offset_x,wall_u_offset_y)) or walldmask.overlap(playermask,(wall_offset_x,wall_d_offset_y)):
        return True
    #check if the blocks have collided:
    offset_x = x - blocks[0]['x']
    offset_y = y - blocks[0]['y']
    overlap = blockmask.overlap(playermask,(offset_x,offset_y))
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

def getRandomBlock(wall_image_u_y, wall_image_d_y):
    blockx = SCREEN_WIDTH #right out of view
    blocky = random.randint(int(wall_image_u_y) + 200, int(wall_image_d_y) - 100)
    return {'x': blockx, 'y': blocky}
