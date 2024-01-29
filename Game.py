import pygame as py
py.init()
import sys
from Environment import Environment
from Camera import Camera
from Control import *
from colors import *

class Game:
    def __init__(self,fenetre,clock,config):
        self.config = config

        self.fenetre = fenetre
        self.clock = clock
        self.width,self.height = self.fenetre.get_size()
        self.monde = Environment(self.width,self.height,self.config)
        self.camera = Camera(self.width,self.height)
        self.stat_window = py.surface.Surface((220,150))
        self.surface = py.surface.Surface((1000,800))

        self.frame_per_tick = 5
        self.frames_left = 5

        self.fonts = {
            "toggle":py.font.SysFont('times new roman',22),
            "numDescription":py.font.SysFont('times new roman',20),
            "bobStats":py.font.SysFont('times new roman',20),
            "numValue":py.font.SysFont('times new roman',30),
            "button":py.font.SysFont('times new roman',45),
            "stats":py.font.SysFont('times new roman',28)
        }

        # Where all the controls will be kept
        self.control_window = py.surface.Surface((1170,490))
        self.control_position = (
            self.width//2 - self.control_window.get_width()//2,
            self.height//2 - self.control_window.get_height()//2
        )

        # Make the windows slightly see through
        self.stat_window.set_alpha(128)
        self.control_window.set_alpha(196)

        self.show_menu = True
        self.show_graphics = True

        self.controls = [
            # First row
            Toggle(10,10,self.config["SINGLE_REPRODUCTION"],"SINGLE_REPRODUCTION"),
            NumericControl(300,10,self.config["MUTATION_VELOCITY"],    0.01,0,  1,   "MUTATION_VELOCITY"),
            NumericControl(590,10,self.config["MUTATION_MASS"],        0.01,0,  1,   "MUTATION_MASS"),
            NumericControl(880,10,self.config["MUTATION_PERCEPTION"],  1,   0,  10,  "MUTATION_PERCEPTION"),

            # Second row
            NumericControl(10,90,self.config["MUTATION_MEMORY"],      1,   0,  10,  "MUTATION_MEMORY"),
            NumericControl(300,90,self.config["MAX_ENERGY"],           10,  100,5000,"MAX_ENERGY",True),
            NumericControl(590,90,self.config["ENERGY_COST"],          0.1, 0,  10,  "ENERGY_COST"),
            Button(880,90,RED,sys.exit,"QUIT"),

            # Third row
            NumericControl(10,170,self.config["SPAWN_ENERGY_BORN_BOB"],10,  10, 500, "SPAWN_ENERGY_BORN_BOB",True),
            NumericControl(300,170,self.config["SPAWN_ENERGY_NEW_BOB"], 10,  10, 500, "SPAWN_ENERGY_NEW_BOB",True),
            NumericControl(590,170,self.config["FPS"],                  1,   1,  200, "FPS",True),
            NumericControl(880,170,self.config["MAP_WIDTH"],            1,   2,  500, "MAP_WIDTH",True),

            # Forth row
            NumericControl(10,250,self.config["FOOD"],                 1,   0,  1000,"FOOD",True),
            NumericControl(300,250,self.config["BOBS"],                 1,   0,  1000,"BOBS",True),
            NumericControl(590,250,self.config["MAP_HEIGHT"],           1,   2,  500, "MAP_HEIGHT",True),
            Button(880,250,BLUE,self.reset,"RESTART"),

            # Fifth row
            Toggle(10,330,self.config["DOUBLE_REPRODUCTION"],"DOUBLE_REPRODUCTION"),
            NumericControl(300,330,self.config["MUTATION_FRIENDSHIP"],      1,   0,  10,  "MUTATION_FRIENDSHIP"),
            NumericControl(590,330,self.config["INIT_VELOCITY"],                 0.1,   0.1,  10,"INIT_VELOCITY",False),
            NumericControl(880,330,self.config["INIT_MASS"],                 0.1,   0.1,  10,"INIT_MASS",False),

            # Sixth row
            NumericControl(10,410,self.config["INIT_PERCEPTION"],           1,   0,  10, "INIT_PERCEPTION",True),
            NumericControl(300,410,self.config["INIT_MEMORY"],                 1,   0,  10,"INIT_MEMORY",True),
            NumericControl(590,410,self.config["INIT_FRIENDSHIP"],                 1,   0,  10,"INIT_FRIENDSHIP",True),
            Toggle(880,410,False,"VELOCITY_COLORING"),
        ]

        self.is_clicking = False
        self.pressed_keys = {
            "s":False, # Save
            "l":False, # Load
            "m":False, # Menu
            "p":False, # Pause
            "g":False, # Graphics
            "1":False,
            "2":False,
            "3":False,
            "4":False,
            "5":False,
            "6":False,
            "7":False,
            "8":False,
            "9":False,
            "0":False,
            ".":False,
            "BACKSPACE":False,
        }

        self.monde.spawn(self.config["FOOD"])
        self.monde.spawn_bob()

        self.speed = 1
        self.time  = 0
        self.day = 1

        self.paused = True

    def events(self):
        for event in py.event.get():
            if event.type == py.KEYDOWN and event.key == py.K_ESCAPE:
                py.quit()
                sys.exit()
            if event.type == py.QUIT:
                py.quit()
                sys.exit()
        self.tick()
        if self.show_graphics:
            py.display.flip()
        
    def tick(self):
        self.check_keys()
        self.check_click()
        self.camera.update()#mis à jour de la position de la souris pour la camera pendant le jeu
        
    def draw(self):
        self.monde.draw(self.fenetre,self.camera,self)
        self.stat_render()
        self.control_render()

    def update(self):
        self.time += self.speed
        if self.time == 50:
            self.day += 1
            self.time = 0
            self.monde.food.reset()
        
        # Count the amount of food
        self.monde.food.update()
    
    def update_bobs(self):
        #Move every cell in one tick
        for i in range(len(self.monde.population)):
            cell = self.monde.population[i]
            cell.update(self.monde, self, self.config, pygame.mouse.get_pos())
            if not cell.alive:
                self.monde.kill_indexes.append(i)
        
        self.monde.rebuild_quadtree()
    
    def check_click(self):
        # Did they left click?
        if pygame.mouse.get_pressed()[0]:
            if not self.is_clicking:
                mouse_pos = pygame.mouse.get_pos()
                pos = (
                    mouse_pos[0]-self.control_position[0],
                    mouse_pos[1]-self.control_position[1]
                )
                if self.show_menu:
                    cache_world_size = (self.config["MAP_WIDTH"], self.config["MAP_HEIGHT"])
                    for i in range(len(self.controls)):
                        if self.controls[i].check_click(pos):
                            self.config[self.controls[i].config_key] = self.controls[i].value
                    if (self.config["MAP_WIDTH"], self.config["MAP_HEIGHT"]) != cache_world_size:
                        self.monde.imgs = self.monde.img_environment()
                        self.monde.monde = self.monde.create_environment()
                        self.monde.place_trees()
                        self.monde.food.reset()
                        self.monde.qtree.min_x = 0
                        self.monde.qtree.max_x = self.config["MAP_WIDTH"]
                        self.monde.qtree.min_y = 0
                        self.monde.qtree.max_y = self.config["MAP_HEIGHT"]
                        self.monde.kull_bobs()

            self.is_clicking = True
        
        else:
            self.is_clicking = False

    def check_keys(self):
        keys = py.key.get_pressed()

        # Save data to file
        if keys[py.K_s]:
            if not self.pressed_keys["s"]:
                self.pressed_keys["s"] = True
                self.monde.save(self.time, self.day)
        else:
            self.pressed_keys["s"] = False
        
        # Load data from file
        if keys[py.K_l]:
            if not self.pressed_keys["l"]:
                self.pressed_keys["l"] = True
                self.time, self.day = self.monde.load(self.controls)
        else:
            self.pressed_keys["l"] = False
        
        if keys[py.K_m]:
            if not self.pressed_keys["m"]:
                self.pressed_keys["m"] = True
                self.show_menu = not self.show_menu
                self.paused = self.show_menu
        else:
            self.pressed_keys["m"] = False

        if keys[py.K_p]:
            if not self.pressed_keys["p"]:
                self.pressed_keys["p"] = True
                self.pause()
        else:
            self.pressed_keys["p"] = False
        
        if keys[py.K_g]:
            if not self.pressed_keys["g"]:
                self.pressed_keys["g"] = True
                self.show_graphics = not self.show_graphics
                self.fenetre.fill((0, 0, 0))
                pygame.display.flip()
        else:
            self.pressed_keys["g"] = False
        
        if not self.show_menu:
            return

        if keys[py.K_0]:
            if not self.pressed_keys["0"]:
                self.pressed_keys["0"] = True
                for i in range(len(self.controls)):
                    self.controls[i].handle_key(0)
        else:
            self.pressed_keys["0"] = False
        
        if keys[py.K_1]:
            if not self.pressed_keys["1"]:
                self.pressed_keys["1"] = True
                for i in range(len(self.controls)):
                    self.controls[i].handle_key(1)
        else:
            self.pressed_keys["1"] = False
        
        if keys[py.K_2]:
            if not self.pressed_keys["2"]:
                self.pressed_keys["2"] = True
                for i in range(len(self.controls)):
                    self.controls[i].handle_key(2)
        else:
            self.pressed_keys["2"] = False
        
        if keys[py.K_3]:
            if not self.pressed_keys["3"]:
                self.pressed_keys["3"] = True
                for i in range(len(self.controls)):
                    self.controls[i].handle_key(3)
        else:
            self.pressed_keys["3"] = False
        
        if keys[py.K_4]:
            if not self.pressed_keys["4"]:
                self.pressed_keys["4"] = True
                for i in range(len(self.controls)):
                    self.controls[i].handle_key(4)
        else:
            self.pressed_keys["4"] = False
        
        if keys[py.K_5]:
            if not self.pressed_keys["5"]:
                self.pressed_keys["5"] = True
                for i in range(len(self.controls)):
                    self.controls[i].handle_key(5)
        else:
            self.pressed_keys["5"] = False
        
        if keys[py.K_6]:
            if not self.pressed_keys["6"]:
                self.pressed_keys["6"] = True
                for i in range(len(self.controls)):
                    self.controls[i].handle_key(6)
        else:
            self.pressed_keys["6"] = False
        
        if keys[py.K_7]:
            if not self.pressed_keys["7"]:
                self.pressed_keys["7"] = True
                for i in range(len(self.controls)):
                    self.controls[i].handle_key(7)
        else:
            self.pressed_keys["7"] = False
        
        if keys[py.K_8]:
            if not self.pressed_keys["8"]:
                self.pressed_keys["8"] = True
                for i in range(len(self.controls)):
                    self.controls[i].handle_key(8)
        else:
            self.pressed_keys["8"] = False
        
        if keys[py.K_9]:
            if not self.pressed_keys["9"]:
                self.pressed_keys["9"] = True
                for i in range(len(self.controls)):
                    self.controls[i].handle_key(9)
        else:
            self.pressed_keys["9"] = False
        
        if keys[py.K_COMMA]:
            if not self.pressed_keys["."]:
                self.pressed_keys["."] = True
                for i in range(len(self.controls)):
                    self.controls[i].handle_key(".")
        else:
            self.pressed_keys["."] = False
        
        if keys[py.K_BACKSPACE]:
            if not self.pressed_keys["BACKSPACE"]:
                self.pressed_keys["BACKSPACE"] = True
                for i in range(len(self.controls)):
                    self.controls[i].handle_key("BACKSPACE")
        else:
            self.pressed_keys["BACKSPACE"] = False
    
    def stat_render(self):
        self.stat_window.fill((0,0,0))

        self.text_render(self.stat_window,"Day :",self.fonts["stats"],(0,0))
        self.text_render(self.stat_window,str(self.day),self.fonts["stats"],(60,0))

        self.text_render(self.stat_window,"Time :",self.fonts["stats"],(0,28))
        self.text_render(self.stat_window,str(self.time),self.fonts["stats"],(70,28))

        self.text_render(self.stat_window,"Food :",self.fonts["stats"],(0,56))
        self.text_render(self.stat_window,str(self.monde.food.food_counter),self.fonts["stats"],(70,56))

        self.text_render(self.stat_window,"Population :",self.fonts["stats"],(0,84))
        self.text_render(self.stat_window,str(len(self.monde.population)),self.fonts["stats"],(135,84))

        self.text_render(self.stat_window,"FPS :",self.fonts["stats"],(0,112))
        self.text_render(self.stat_window,str(self.clock.get_fps()),self.fonts["stats"],(60,112))

        self.fenetre.blit(self.stat_window,(0,0))
        #py.display.flip()
    
    def control_render(self):
        if not self.show_menu:
            return

        self.control_window.fill((0,0,0))

        for i in range(len(self.controls)):
            self.controls[i].draw(self, self.fonts)
        
        self.fenetre.blit(self.control_window, self.control_position)

    def text_render(self,surface,text,font,cord = (0,0),background = (0,0,0)):
        text = font.render(text , True ,(255,255,255),background)
        surface.blit(text,cord)
    
    def reset(self):
        self.monde = Environment(self.width,self.height,self.config)

        self.is_clicking = False
        self.pressed_keys = {"s":False,"l":False,"m":False}

        self.monde.spawn(self.config["FOOD"])
        self.monde.spawn_bob()

        self.speed = 1
        self.time  = 0
        self.day = 1
    
    def pause(self):
        self.paused = not self.paused

    def run(self):
        self.running = True 
        while(self.running):
            self.clock.tick(self.config["FPS"])#vitesse du jeu -limite 60FPS(60 images par seconde)
            self.events()
            self.draw()
            if self.paused:
                continue

            self.update()
            self.frames_left -= 1
            if self.frames_left < 0:
                self.frames_left = self.frame_per_tick
                self.update_bobs()

   