import pygame as py
py.init()
import sys
from config import MAP_WIDTH,MAP_HEIGHT
from Environment import Environment
from Camera import Camera



class Game:
    def __init__(self,fenetre,clock):
        self.fenetre = fenetre
        self.clock = clock
        self.width,self.height = self.fenetre.get_size()
        self.monde = Environment(MAP_WIDTH,MAP_HEIGHT,self.width,self.height)
        self.camera = Camera(self.width,self.height)
        self.stat_window = py.surface.Surface((800,200))
        self.surface = py.surface.Surface((1000,800))
        
        self.monde.spawn()
        self.monde.spawn_bob()

        self.speed = 1
        self.time  = 0
        self.day = 1
        


    def events(self):
            for event in py.event.get():
                if event.type == py.KEYDOWN and event.key == py.K_ESCAPE:
                    py.quit()
                    sys.exit()
                if event.type == py.QUIT:
                    py.quit()
                    sys.exit()
            self.tick()
    def update(self):
         self.camera.update()#mis à jour de la position de la souris pour la camera pendant le jeu
         
         
        
    def draw(self):
        self.stat_render()
        self.monde.draw(self.fenetre,self.camera)
        py.display.flip()

    def tick(self):
        self.time += self.speed
        if self.time == 50:
            self.day += 1
            self.time = 0
            self.monde.food.reset()

        #Move every cell in one tick
        for cell in self.monde.population:
            if cell.alive:
                cell.update(self.monde,self)
            else:
                self.monde.population.remove(cell) 
    
    def stat_render(self):
        self.stat_window.fill((0,0,0))

        self.text_render(self.stat_window,"Day :",(0,0))
        self.text_render(self.stat_window,str(self.day),(60,0))

        self.text_render(self.stat_window,"Time :",(0,28))
        self.text_render(self.stat_window,str(self.time),(70,28))

        self.text_render(self.stat_window,"Food :",(0,56))
        self.text_render(self.stat_window,str(self.monde.food.food_counter),(70,56))

        self.text_render(self.stat_window,"Population :",(0,84))
        self.text_render(self.stat_window,str(len(self.monde.population)),(135,84))

        self.fenetre.blit(self.stat_window,(0,0))
        py.display.flip()

    def text_render(self,surface,text,cord = (0,0),background = (255,255,255)):
        py.font.init()
        font = py.font.SysFont('times new roman',28)
        text = font.render(text , True ,(255,0,255),background)
        surface.blit(text,cord)

    def run(self):
        self.running = True 
        while(self.running):
            self.clock.tick(20)#vitesse du jeu -limite 60FPS(60 images par seconde)
            self.events()
            self.update()
            self.draw()

   