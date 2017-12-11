#!/usr/bin/python3

import sys
import pygame
import random
import math

width = 800
height = 600

#Load the parameters of the different objects used for the game
#Unused
def load(ball, ball_coords, rackets, rackets_coord):
    ball = pygame.image.load("../resource/image/ball.png")
    ball_coords = ball.get_rect()

    rackets = [None,None]
    rackets_coords = [None,None]
    for i in range(2):
        rackets[i] = pygame.image.load("../resource/image/racket.png")
        racket_coords[i] = rackets[i].get_rect()
        if i == 1:
            racket_coords[i] = racket_coords[i].move((width, 0))

class BallServer:
	def __init__(self):
		self.x = width / 2
		self.y = random.randrange(height / 4,height * 3 / 4)
		self.direction = (random.randrange(-60, 60) + 360) % 360
		if random.randrange(2) > 0: 
			self.direction = (180 - self.direction + 360) % 360
		self.direction = math.radians(self.direction)
		self.speed = 2
		self.width = 20
		self.height = 20

	def update(self):
		self.x = self.x + self.speed * math.cos(self.direction)
		self.y = self.y + self.speed * math.sin(self.direction)
		if self.x < self.width / 2 or self.x >= width - self.width / 2:
			self.direction = -self.direction
		if self.y < self.height / 2 or self.y >= height - self.height / 2:
			math.pi - self.direction
