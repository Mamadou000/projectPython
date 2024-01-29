import pygame as py
py.init()
from Game import Game
import pickle

Fenetre = py.display.set_mode((0,0),py.FULLSCREEN) #taille s'adaptant à la resolution de mon ecran
clock = py.time.Clock() #initialisé la clock pour les thics

config = pickle.load(open("save_data\\config.txt", "rb"))

the_game = Game(Fenetre,clock,config)
the_game.run()