import random
from config import FOOD,FOOD_ENERGY
import pygame as pg

class food:
    def __init__(self,world):
        self.world = world
        self.image = pg.image.load("C:\\ONEDRIVE\\Bureau\\projet_python m\\assets\\food.png")
        self.food = [[0 for i in range(self.world.longueur_grille)] for k in range(self.world.largeur_grille) ]
        self.food_counter = FOOD
        self.counter = FOOD
    
        
    def reset(self):
        self.food = [[0 for i in range(self.world.longueur_grille)] for k in range(self.world.largeur_grille) ]
        self.food_counter = FOOD
        
        self.world.spawn(self.food_counter)
    
    def update(self):
        pass
    def eaten(self,x_cordinate,y_cordinate):
        if (self.food[x_cordinate][y_cordinate] > 0):
            self.food_counter =self.food_counter - (self.food[x_cordinate][y_cordinate]//FOOD_ENERGY)
            #self.counter = self.counter - 1
            self.food[x_cordinate][y_cordinate] = 0 