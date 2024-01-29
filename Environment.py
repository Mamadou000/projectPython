import pygame as pg
pg.init()
taille_tuile = 50
import random
from colors import BLACK
from food import food
from Population import Cell
import math
import pickle
from quadtree import QuadTree, Point

def get_new_size(og_size, zoom, mass, energy):
    return int(og_size*zoom*math.cbrt(mass+energy/100))

class Environment:
    def __init__(self,largeur_fenetre,hauteur_fenetre,config):
        self.config = config
        self.largeur_fenetre = largeur_fenetre
        self.hauteur_fenetre = hauteur_fenetre
        self.tuiles = self.charger_tuiles()
        #self.surface_grass= pg.Surface((self.largeur_fenetre,self.hauteur_fenetre))
        self.monde = self.create_environment()
        self.imgs = self.img_environment()
        self.tree_positions = self.place_trees()
        self.food = food(self,self.config)
        self.food_coordinates = []
       # self.spawn()
        #self.bobs = Cell(self)
        #self.bobs.spawn2() 

        self.population = []
        self.qtree = QuadTree(0, self.config["MAP_WIDTH"], 0, self.config["MAP_HEIGHT"])
        self.kill_indexes = []

        self.bob_image = pg.image.load("assets\\face.png").convert_alpha()
        self.bob_predator_image = pg.image.load("assets\\predator.png").convert_alpha()

    def create_environment(self):
        Environment = {}
        for ligne in range(self.config["MAP_WIDTH"]):
            for colonne in range(self.config["MAP_HEIGHT"]):
                Case = self.cases(ligne,colonne)
                Environment[(ligne,colonne)] = Case
                position = Case["coordonnes_tuiles"]
                #self.surface_grass.blit(self.tuiles["grass"],(position[0] + self.largeur_fenetre//2,position[1] + self.hauteur_fenetre //4 ))
        return Environment

    def choose_tile_img(self):
        tiles = ["sand", "grass", "water"]
        chances = [0.2, 0.8, 1]

        p = 0
        for i in range(len(chances)):
            if random.random() < chances[i]:
                p = i
                return tiles[p]

    def img_environment(self):
        Environment = {}
        
        for ligne in range(self.config["MAP_WIDTH"]):
            for colonne in range(self.config["MAP_HEIGHT"]):
                Environment[(ligne,colonne)] = self.choose_tile_img()
                
        return Environment

    def place_trees(self):
        # Trees are calculated seperately to tiles
        positions = []
        for ligne in range(self.config["MAP_WIDTH"]):
            for colonne in range(self.config["MAP_HEIGHT"]):
                if random.random() < 0.01:
                    positions.append((ligne, colonne))
        return positions

    def cases(self,position_x,position_y):
        case = [(position_x*taille_tuile,position_y*taille_tuile),#coin superieur gauche
                (position_x*taille_tuile+taille_tuile,position_y*taille_tuile),#coin superieur droit
                (position_x*taille_tuile+taille_tuile,position_y*taille_tuile+taille_tuile),#coin inferieur droit
                (position_x*taille_tuile ,position_y*taille_tuile+taille_tuile)#coin inferieur gauche
                ]
        #isometric = [self.cart_to_iso(x, y) for x, y in case]
        isometric = []
        for x,y in case:
            isometric.append(self.conversion_en_isometric(x,y))
        min_x= min([x for x,y in isometric])
        min_y = min([y for x,y in isometric])



        r = random.randint(1,50)
        if r <= 8:
            tile = "tree"
        else :
            tile = ""

        sortie = {
            "grille": [position_x, position_y],
            "cases": case,
            "coordonnes_isometric": isometric,
            "coordonnes_tuiles":[min_x,min_y],
            "tile":tile
            
        }

        return sortie

    def conversion_en_isometric(self, x, y):
        iso_x = x - y
        iso_y = (x + y)/2
        return iso_x, iso_y #retourne le type de cordonnés x et y en iso
         
    def charger_tuiles(self):
        sand = pg.image.load("assets\\sand.png").convert_alpha()
        grass = pg.image.load("assets\\grass.png").convert_alpha()
        water =  pg.image.load("assets\\water.png").convert_alpha()
        tree =  pg.image.load("assets\\tree.png").convert_alpha()
        #tree= pg.transform.scale(tree1, (tree1.get_width()*2, tree1.get_height()*2))
        return {"sand":sand,"grass":grass,"water":water,"tree":tree}
  

    def draw_land(self,screen,camera):
        screen.fill((0, 64, 128))
        # self.fenetre.blit(self.monde.surface_grass,(self.camera.deplacement.x,self.camera.deplacement.y)) #remplace la grass d'après (performance)
        for x in range(self.config["MAP_WIDTH"]):
            for y in range(self.config["MAP_HEIGHT"]):
                     
                #drawing the sand
                position_tuiles = self.monde[x,y]["coordonnes_tuiles"]
                x_pos = (position_tuiles[0])*camera.zoom + self.largeur_fenetre/2 + camera.deplacement.x 
                y_pos=  (position_tuiles[1])*camera.zoom + self.hauteur_fenetre/4 + camera.deplacement.y 

                if x_pos > screen.get_width():
                    continue
                if x_pos < -200:
                    continue
                if y_pos > screen.get_height():
                    continue
                if y_pos < -100:
                    continue
                
                img = self.tuiles[self.imgs[x,y]]
                tuile = pg.transform.scale(img,(img.get_width()*camera.zoom,img.get_height()*camera.zoom))
                screen.blit(tuile,(x_pos,y_pos))
        
        for i in range(len(self.tree_positions)):
            #drawing the tree
            if self.tree_positions[i][0] >= self.config["MAP_WIDTH"]:
                continue
            if self.tree_positions[i][1] >= self.config["MAP_HEIGHT"]:
                continue

            position_tuiles = self.cases(self.tree_positions[i][0], self.tree_positions[i][1])["coordonnes_tuiles"]
            x_pos = (position_tuiles[0]-15)*camera.zoom + self.largeur_fenetre/2 + camera.deplacement.x 
            y_pos=  (position_tuiles[1]-105)*camera.zoom + self.hauteur_fenetre/4 + camera.deplacement.y 
            
            img = self.tuiles["tree"]
            tuile = pg.transform.scale(img,(img.get_width()*camera.zoom,img.get_height()*camera.zoom))
            screen.blit(tuile,(x_pos,y_pos))

    def spawn_bob(self):
        self.qtree = QuadTree(0, self.config["MAP_WIDTH"], 0, self.config["MAP_HEIGHT"])
        for i in range(self.config["BOBS"]):
            x=random.randint(0,self.config["MAP_WIDTH"] - 1)
            y=random.randint(0,self.config["MAP_HEIGHT"] - 1)
            cell = Cell(self,x,y,self.config["SPAWN_ENERGY"])
            self.population.append(cell)
            self.qtree.insert(Point(x, y, cell))

    
    def draw_bob(self,screen,camera,mouse_pos,Game):  #drawing bobs
        ratio = 1-Game.frames_left/Game.frame_per_tick

        for cell in self.population:
            if cell.predator:
                img = self.bob_predator_image
            else:
                img = self.bob_image

            i,t = cell.px,cell.py
            if i >= self.config["MAP_WIDTH"]:
                i = self.config["MAP_WIDTH"]-1
            if t >= self.config["MAP_HEIGHT"]:
                t = self.config["MAP_HEIGHT"]-1

            di, dt = cell.x, cell.y
            p1 = self.monde[i,t]["coordonnes_tuiles"]
            p2 = self.monde[di,dt]["coordonnes_tuiles"]

            position_tuiles = (p1[0]+(p2[0]-p1[0])*ratio, p1[1]+(p2[1]-p1[1])*ratio)

            x_pos = (position_tuiles[0]+35)*camera.zoom + self.largeur_fenetre/2 + camera.deplacement.x
            y_pos = (position_tuiles[1]-25)*camera.zoom + self.hauteur_fenetre/4 + camera.deplacement.y

            if x_pos > screen.get_width():
                continue
            if x_pos < -100:
                continue
            if y_pos > screen.get_height():
                continue
            if y_pos < -100:
                continue

            img_width = get_new_size(img.get_width(), camera.zoom, cell.mass, cell.energy/100)
            img_height = get_new_size(img.get_height(), camera.zoom, cell.mass, cell.energy/100)

            x_pos -= (img_width-31*camera.zoom)//2
            y_pos -= (img_height-63*camera.zoom)

            tuile = pg.transform.scale(img,(img_width,img_height))

            if self.config["VELOCITY_COLORING"]:
                vc = -25.51*cell.velocity + 255.1
                if vc <= 0:
                    vc = 1
                tuile.set_alpha(vc)

            screen.blit(tuile,(x_pos,y_pos))

            if pg.Rect(x_pos-img_width*3,y_pos-img_height*3,img_width*6,img_height*6).collidepoint(mouse_pos):
                self.draw_info_card(cell,mouse_pos,screen,Game)
    
    def draw_info_card(self, cell, mouse_pos, screen, Game):
        pg.draw.rect(screen, BLACK, pg.Rect(mouse_pos[0],mouse_pos[1],150,150))
        Game.text_render(screen, "Energy: " + str(cell.energy), Game.fonts["bobStats"], (mouse_pos[0], mouse_pos[1]))
        Game.text_render(screen, "Velocity: " + str(cell.velocity), Game.fonts["bobStats"], (mouse_pos[0], mouse_pos[1]+20))
        Game.text_render(screen, "Mass: " + str(cell.mass), Game.fonts["bobStats"], (mouse_pos[0], mouse_pos[1]+40))
        Game.text_render(screen, "Perception: " + str(cell.perception), Game.fonts["bobStats"], (mouse_pos[0], mouse_pos[1]+60))
        Game.text_render(screen, "Memory: " + str(cell.memory), Game.fonts["bobStats"], (mouse_pos[0], mouse_pos[1]+80))
        Game.text_render(screen, "Friendship: " + str(cell.friendship), Game.fonts["bobStats"], (mouse_pos[0], mouse_pos[1]+100))

    def reproduce(self,x,y,velocity,perception,memory,friendship):
        if not self.config["SINGLE_REPRODUCTION"]:
            return

        new_velocity = round(velocity + random.uniform(-self.config["MUTATION_VELOCITY"], self.config["MUTATION_VELOCITY"]),2)
        new_mass = round(velocity + random.uniform(-self.config["MUTATION_MASS"], self.config["MUTATION_MASS"]),2)
        new_perception = perception + random.randint(-self.config["MUTATION_PERCEPTION"], self.config["MUTATION_PERCEPTION"])
        new_memory = memory + random.randint(-self.config["MUTATION_MEMORY"],self.config["MUTATION_MEMORY"])
        new_friendship = friendship + random.randint(-self.config["MUTATION_FRIENDSHIP"],self.config["MUTATION_FRIENDSHIP"])

        if new_velocity < 0:
            new_velocity = 0
        if new_mass <= 0:
            new_mass = 0.1
        if new_perception < 0:
            new_perception = 0
        if new_memory < 0:
            new_memory = 0
        if new_friendship < 0:
            new_friendship = 0

        new_cell = Cell(self,x,y,self.config["SPAWN_ENERGY_NEW_BOB"],new_velocity,new_mass,new_perception,new_memory,new_friendship)
        self.population.append(new_cell)
    
    def reproduce_with_parents(self, parent1, parent2):
        if not self.config["DOUBLE_REPRODUCTION"]:
            return

        # Get the averages then do mutation
        new_velocity = round((parent1.velocity+parent2.velocity)/2 + random.uniform(-self.config["MUTATION_VELOCITY"], self.config["MUTATION_VELOCITY"]), 2)
        new_mass = round((parent1.mass+parent2.mass)/2 + random.uniform(-self.config["MUTATION_MASS"], self.config["MUTATION_MASS"]), 2)
        new_perception = (parent1.perception+parent2.perception)//2 + random.randint(-self.config["MUTATION_PERCEPTION"], self.config["MUTATION_PERCEPTION"])
        new_memory = (parent1.memory+parent2.memory)//2 + random.randint(-self.config["MUTATION_MEMORY"],self.config["MUTATION_MEMORY"])
        new_friendship = (parent1.friendship+parent2.friendship)//2 + random.randint(-self.config["MUTATION_FRIENDSHIP"],self.config["MUTATION_FRIENDSHIP"])

        if new_velocity < 0:
            new_velocity = 0
        if new_mass <= 0:
            new_mass = 0.1
        if new_perception < 0:
            new_perception = 0
        if new_memory < 0:
            new_memory = 0
        if new_friendship < 0:
            new_friendship = 0

        # Since parents have same position it doesn't matter which x and y you use
        new_cell = Cell(self,parent1.x,parent1.y,self.config["SPAWN_ENERGY_BORN_BOB"],new_velocity,new_mass,new_perception,new_memory)
        self.population.append(new_cell)
    
    def spawn(self,n):
        for i in range(n):
            x_cordinate = random.randint(0,self.config["MAP_WIDTH"]  - 1)
            y_cordinate = random.randint(0,self.config["MAP_HEIGHT"] - 1)
            self.food.food[x_cordinate,y_cordinate] += self.config["FOOD_ENERGY"]
            self.food_coordinates.append((x_cordinate, y_cordinate))
    
    def draw_food(self,screen,camera):  #drawing the food randomly
        for x,y in self.food_coordinates:

            if x >= self.config["MAP_WIDTH"]:
                continue
            if y >= self.config["MAP_HEIGHT"]:
                continue
            
            if self.food.food[x,y] > 0:
                position_tuiles = self.monde[x,y]["coordonnes_tuiles"]
                x_pos = (position_tuiles[0]+35)*(camera.zoom) + self.largeur_fenetre/2 + camera.deplacement.x 
                y_pos=  (position_tuiles[1]+10)*(camera.zoom) + self.hauteur_fenetre/4+ camera.deplacement.y

                if x_pos > screen.get_width():
                    continue
                if x_pos < -100:
                    continue
                if y_pos > screen.get_height():
                    continue
                if y_pos < -100:
                    continue
                
                    
                tuile = pg.transform.scale(self.food.image,(self.food.image.get_width()*camera.zoom,self.food.image.get_height()*camera.zoom))
                screen.blit(tuile,(x_pos,y_pos))

    def save(self, time, day):
        with open("save_data\\food.txt", "wb") as file:
            pickle.dump(self.food.food, file)
        with open("save_data\\bobs.txt", "wb") as file:
            pickle.dump(self.population, file)
        with open("save_data\\time.txt", "wb") as file:
            pickle.dump((time, day), file)
        with open("save_data\\config.txt", "wb") as file:
            pickle.dump(self.config, file)
    
    def load(self,controls):
        with open("save_data\\food.txt", "rb") as file:
            self.food.food = pickle.load(file)
        with open("save_data\\bobs.txt", "rb") as file:
            self.population = pickle.load(file)
        with open("save_data\\config.txt", "rb") as file:
            self.config = pickle.load(file)
            for i in range(len(controls)):
                if controls[i].is_button:
                    continue
                controls[i].value = self.config[controls[i].config_key]
        with open("save_data\\time.txt", "rb") as file:
            return pickle.load(file)
    
    def kull_bobs(self):
        dif = 0
        for i in range(len(self.population)):
            if self.population[i-dif].x >= self.config["MAP_WIDTH"]:
                self.population.remove(self.population[i-dif])
                dif += 1
            elif self.population[i-dif].y >= self.config["MAP_HEIGHT"]:
                self.population.remove(self.population[i-dif])
                dif += 1
    
    def rebuild_quadtree(self):
        new_population = []
        for i in range(len(self.population)):
            valid = True
            for j in range(len(self.kill_indexes)):
                if i == self.kill_indexes[j]:
                    valid = False
                    break
            
            if valid:
                new_population.append(self.population[i])
        self.population = new_population
        self.kill_indexes = []

        self.qtree = QuadTree(0, self.largeur_fenetre, 0, self.hauteur_fenetre)

        for i in range(len(self.population)):
            self.qtree.insert(Point(self.population[i].x, self.population[i].y, self.population[i]))

    def draw(self,screen,camera,Game):
        self.draw_land(screen,camera)
        self.draw_food(screen,camera)
        self.draw_bob(screen,camera,pg.mouse.get_pos(),Game)
       

