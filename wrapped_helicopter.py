import pygame
from pygame.locals import *
import sys
import random
import pygame.surfarray as surfarray

FPS = 60
SPEED = 5
WALL_SPEED = 10

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

IMAGES['wall'] = pygame.image.load('walls2.png').convert_alpha()


class GameState:
    def __init__(self):
        self.score = self.playerIndex = self.loopIter = 0
        self.playerx = 200
        self.playery = 200

        self.playeranim = [IMAGES['heli'][i] for i in range(3)]
        self.playerim = self.playeranim[1]
        self.playermask = pygame.mask.from_surface(self.playerim,50)
        self.playerVel = SPEED

        newBlock = getRandomBlock()

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
        self.wall_image = IMAGES['wall']
        self.wall_prime = IMAGES['wall'] #used for looping the wall
        self.wall_mask = pygame.mask.from_surface(self.wall_image,50)
        self.prime_mask = pygame.mask.from_surface(self.wall_prime,50)
        self.wall_prime_x = -100000
        self.wall_image_x = 0
        self.main_wall = self.wall_image

    def frame_step(self, input_actions):
        pygame.event.pump()

        reward = 0.1
        terminal = False

        if sum(input_actions) != 1:
            raise ValueError('Multiple input actions!')

        if input_actions[1] == 1:
            self.move = True

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

        #displaying the wall:
        if self.wall_image_x > -2100:
            screen.blit(self.wall_image, (self.wall_image_x,0))
            self.wall_image_x -= WALL_SPEED
        if self.wall_prime_x > -2100:
            screen.blit(self.wall_prime,(self.wall_prime_x,0))
            self.wall_prime_x -= WALL_SPEED
        if self.main_wall == self.wall_image:
            if self.wall_image_x <= -700:
                self.main_wall = self.wall_prime
                self.wall_prime_x = self.wall_image_x+1399
        elif self.main_wall == self.wall_prime:
            if self.wall_prime_x <= -700:
                self.main_wall = self.wall_image
                self.wall_image_x = self.wall_prime_x+1399

        #blocks:
        for block in self.blocks:
            block['x'] -= self.blockVel
            screen.blit(IMAGES['block'],(block['x'],block['y']))

        if 50 < self.blocks[0]['x'] < 100:
            newBlock = getRandomBlock()
            self.blocks.append(newBlock)

        if self.blocks[0]['x'] < -50:
            self.blocks.pop(0)

        #smoke:
        for smoke in self.smokes:
            smoke['x'] -= self.smokeVel
            screen.blit(IMAGES['smoke'],(smoke['x'],smoke['y']))

        if self.smokes[0]['x'] < self.playerx - 30:
            self.smokes.append({'x': self.playerx, 'y': self.playery - 4})

        if self.smokes[0]['x'] < -15:
            self.smokes.pop(0)

        screen.blit(small_font.render('SCORE: %i'%self.score,False,pygame.Color(0,100,255)),(50,460))

        self.playerim = self.playeranim[self.score%3]

        isCrash = check_collide(self.playerx,self.playery,self.wall_image_x,self.wall_prime_x,self.prime_mask,
            self.wall_mask,self.playermask,self.blockmask,self.blocks)

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
        pygame.display.update()
        clock.tick(FPS)
        self.score += 1
        reward += 1
        return image_data, reward, terminal
    

def check_collide(x,y,wall_image_x,wall_prime_x, prime_mask, wall_mask, playermask, blockmask, blocks):
    """uses masks to see if non-transparent pixels overlap"""
    #check if the wall has collided:
    wall_offset_x = x - wall_image_x
    prime_offset_x = x - wall_prime_x
    offset_y = y
    if prime_mask.overlap(playermask,(prime_offset_x,offset_y)) or wall_mask.overlap(playermask,(wall_offset_x,offset_y)):
        return True
    #check if the blocks have collided:
    for block in blocks:
        offset_x = x - block['x']
        offset_y = y - block['y']
        overlap = blockmask.overlap(playermask,(offset_x,offset_y))
        if overlap: return True


def getRandomBlock():
    blockx = SCREEN_WIDTH + 1 #right out of view
    blocky = random.randint(100,300)
    return {'x': blockx, 'y': blocky}
