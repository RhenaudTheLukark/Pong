#!/usr/bin/python3

import sys
import pygame
import random
import math

width = 800
height = 600

#Load the parameters of the different objects used for the game
#Unused
def load(ball, rackets):
    ball = pygame.image.load("../resource/image/ball_new.png")
    rackets = [None,None]
    for i in range(2):
        rackets[i] = pygame.image.load("../resource/image/racket_new.png")

class BallServer:
	def __init__(self):
		self.x = width / 2
		self.y = random.randrange(height / 4,height * 3 / 4)
		# Direction: 
		# 0               = Left
		# math.pi / 2     = Down
		# math.pi         = Right
		# 3 * math.pi / 2 = Up
		self.direction = (random.randrange(-60, 60) + 360) % 360
		if random.randrange(2) > 0: 
			self.direction = (180 - self.direction + 360) % 360
		self.direction = math.radians(self.direction)
		self.speed = 2
		self.diam = 20

	def update(self):
		self.x = self.x + self.speed * math.cos(self.direction)
		self.y = self.y + self.speed * math.sin(self.direction)
