#!/usr/bin/python3

import sys
import pygame

width = 800
height = 600

#Initialise Pygame
def init():
    global width
    global height
    pygame.init()
    screen = pygame.display.set_mode((width, height))

#Load the parameters of the different objects used for the game
def load(ball,ball_coords,rackets,rackets_coord):
    ball = pygame.image.load("image/ball.png")
    ball_coords = ball.get_rect()

    rackets = [None,None]
    rackets_coords = [None,None]

class Ball:
	def __init__(self):
		self.x = width / 2
		self.y = random.randrange(height / 4,height * 3 / 4)
		self.direction = (random.randrange(-60, 60) + 360) % 360
		if random.randrange(2) > 0: 
			self.direction = (180 - self.direction + 360) % 360
		self.direction = radians(self.direction)
		self.speed = 4
		self.width = 20
		self.height = 20

	def update():
		self.x = self.x + speed * math.cos(self.direction)
		self.y = self.y + speed * math.sin(self.direction)
		if self.x < self.width / 2 or self.x >= width - self.width / 2:
			self.direction = -self.direction
		if self.y < self.height / 2 or self.y >= height - self.height / 2:
			math.pi - self.direction
