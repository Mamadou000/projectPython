import random
from config import MAP_WIDTH,MAP_HEIGHT,SPAWN_ENERGY, MAX_ENERGY,ENERGY_COST,FOOD_ENERGY, movement,BOBS
import pygame as pg
class Population():
    def __init__(self) -> None:
        pass

class Cell():
    def __init__(self,world,spawn_x,spawn_y,energy=SPAWN_ENERGY,velocity=1,mass = 1):
        self.x=spawn_x
        self.y=spawn_y
        self.energy     = energy
        self.energy_max = MAX_ENERGY
        self.cost       = 1

        self.velocity   = velocity
        self.buffer     = 0

        self.mass = mass
        self.world = world
        self.image = pg.image.load("C:\\ONEDRIVE\\Bureau\\projet_python m\\assets\\face.png").convert_alpha()
       
        self.alive = True

     
     

    def move(self,direction):
        distance = int(self.velocity + self.buffer)
        self.buffer = self.velocity + self.buffer  - distance

        #Movement
        match (direction):
            case movement.LEFT.value:
                if self.x > 0:
                    self.x = self.x - distance
                else: 
                    direction = movement.STATION.value
            case movement.RIGHT.value:
                if self.x + 1 < MAP_WIDTH:
                    self.x = self.x + distance
                else: 
                    direction = movement.STATION.value
            case movement.UP.value:
                if self.y + 1 < MAP_HEIGHT:
                    self.y = self.y + distance
                else: 
                    direction = movement.STATION.value
            case movement.DOWN.value:
                if self.y > 0:
                    self.y = self.y - distance
                else: 
                    direction = movement.STATION.value

        #Energy lost
        match (direction):
            case movement.STATION.value:
                self.energy -= self.cost
            case _:
                self.energy -= self.mass*self.velocity*self.velocity

    def consume(self):
       self.energy += self.world.food.food[self.x][self.y]
       self.world.food.eaten(self.x,self.y)
       if (self.energy > self.energy_max):
            self.world.food.food[self.x][self.y] = self.energy - self.energy_max
            self.energy = self.energy_max


    def update(self,map,game):
        self.move(random.randint(0,4))
        self.consume()
        if (self.energy <= 0):
            self.alive = False
        if (self.energy == self.energy_max):
            self.energy = 150
            self.world.reproduce(self.x,self.y)