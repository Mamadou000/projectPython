import pygame as pg

class food:
    def __init__(self,world,config):
        self.config = config
        self.world = world
        self.image = pg.image.load("assets\\food.png")
        # Creates a dictionary like a list of lists but now linear
        self.food = {(i, k):0 for i in range(self.config["MAP_WIDTH"]) for k in range(self.config["MAP_HEIGHT"])}
        self.food_counter = self.config["FOOD"]
        self.counter = self.config["FOOD"]
    
    def reset(self):
        self.food = {(i, k):0 for i in range(self.config["MAP_WIDTH"]) for k in range(self.config["MAP_HEIGHT"])}
        self.food_counter = self.config["FOOD"]
        
        self.world.spawn(self.food_counter)
    
    def update(self):
        self.food_counter = 0
        for x in range(self.config["MAP_WIDTH"]-1):
            for y in range(self.config["MAP_HEIGHT"]-1):
                if self.food[x,y] != 0:
                    self.food_counter += 1

    def eaten(self,x_cordinate,y_cordinate):
        if (self.food[x_cordinate,y_cordinate] > 0):
            self.food_counter =self.food_counter - (self.food[x_cordinate,y_cordinate]//self.config["FOOD_ENERGY"])
            #self.counter = self.counter - 1
            self.food[x_cordinate,y_cordinate] = 0 