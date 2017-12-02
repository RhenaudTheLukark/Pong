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

