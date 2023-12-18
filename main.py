import pygame as py
py.init()
from Game import Game

Fenetre = py.display.set_mode((0,0),py.FULLSCREEN) #taille s'adaptant à la resolution de mon ecran
clock = py.time.Clock() #initialisé la clock pour les thics
 
the_game = Game(Fenetre,clock)
the_game.run()





