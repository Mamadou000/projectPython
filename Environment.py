import pygame as pg
pg.init()
taille_tuile = 50
import random
from Camera import Camera
from config import BLACK,FOOD,BOBS,FOOD_ENERGY,SPAWN_ENERGY_NEW_BOB
from food import food
from Population import Cell
from d import *


class Environment:
    def __init__(self,largeur_grille,longueur_grille,largeur_fenetre,hauteur_fenetre):
        self.largeur_grille = largeur_grille
        self.longueur_grille = longueur_grille
        self.largeur_fenetre = largeur_fenetre
        self.hauteur_fenetre = hauteur_fenetre
        self.tuiles = self.charger_tuiles()
        #self.surface_grass= pg.Surface((self.largeur_fenetre,self.hauteur_fenetre))
        self.monde = self.create_environment()
        self.food = food(self)
        self.food_coordinates = []
       # self.spawn()
        #self.bobs = Cell(self)
        #self.bobs.spawn2() 
       
        self.population = []
        

         

    def create_environment(self):
        Environment = [] 
        for ligne in range(self.largeur_grille):
            row = []
            for colonne in range(self.longueur_grille):
                Case = self.cases(ligne,colonne)
                row.append(Case)
                position = Case["coordonnes_tuiles"]
                #self.surface_grass.blit(self.tuiles["grass"],(position[0] + self.largeur_fenetre//2,position[1] + self.hauteur_fenetre //4 ))
            Environment.append(row)
        return Environment


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
        sand = pg.image.load("C:\\ONEDRIVE\\Bureau\\projet_python m\\assets\\sand.png").convert_alpha()
        grass = pg.image.load("C:\\ONEDRIVE\\Bureau\\projet_python m\\assets\\grass.png").convert_alpha()
        water =  pg.image.load("C:\\ONEDRIVE\\Bureau\\projet_python m\\assets\\block2.png").convert_alpha()
        tree =  pg.image.load("C:\\ONEDRIVE\\Bureau\\projet_python m\\assets\\food.png").convert_alpha()
        #tree= pg.transform.scale(tree1, (tree1.get_width()*2, tree1.get_height()*2))
        return {"sand":sand,"grass":grass,"water":water,"tree":tree}
  

    def draw_sand(self,screen,camera):
        screen.fill((BLACK))
        # self.fenetre.blit(self.monde.surface_grass,(self.camera.deplacement.x,self.camera.deplacement.y)) #remplace la grass d'après (performance)
        for x in range(self.largeur_grille):
              for y in range(self.longueur_grille):
                     
                    #drawing the sand
                    position_tuiles = self.monde[x][y]["coordonnes_tuiles"]
                    x_pos = (position_tuiles[0])*camera.zoom + self.largeur_fenetre/2 + camera.deplacement.x 
                    y_pos=  (position_tuiles[1])*camera.zoom + self.hauteur_fenetre/4 + camera.deplacement.y 
                    
                    sand = self.tuiles["sand"]
                    tuile = pg.transform.scale(sand,(sand.get_width()*camera.zoom,sand.get_height()*camera.zoom))
                    screen.blit(tuile,(x_pos,y_pos))
                 
                    


    def spawn_bob(self):
        
        for i in range(BOBS):
            x=random.randint(0,self.largeur_grille - 1)
            y=random.randint(0,self.longueur_grille - 1)
            cell = Cell(self,x,y)
            self.population.append(cell)   
    
    def draw_bob(self,screen,camera):  #drawing bobs
        for cell in self.population:
            i,t = cell.x,cell.y
            position_tuiles = self.monde[i][t]["coordonnes_tuiles"]
            x_pos = (position_tuiles[0]+35)*camera.zoom + self.largeur_fenetre/2 + camera.deplacement.x 
            y_pos=  (position_tuiles[1]-25)*camera.zoom + self.hauteur_fenetre/4 + camera.deplacement.y 
                    
                    
            tuile = pg.transform.scale(cell.image,(cell.image.get_width()*camera.zoom,cell.image.get_height()*camera.zoom))
            screen.blit(tuile,(x_pos,y_pos))
    
    def reproduce(self,x,y):
        new_cell = Cell(self,x,y,SPAWN_ENERGY_NEW_BOB)
        self.population.append(new_cell)
    
    def spawn(self,n=FOOD):
        
        for i in range(n):
            x_cordinate = random.randint(0,self.largeur_grille  - 1)
            y_cordinate = random.randint(0,self.longueur_grille - 1)
            self.food.food[x_cordinate][y_cordinate] += FOOD_ENERGY
            self.food_coordinates.append((x_cordinate, y_cordinate))
    
    def draw_food(self,screen,camera):  #drawing the food randomly
                     
        for x,y in self.food_coordinates:
            
                if self.food.food[x][y] > 0:
                    position_tuiles = self.monde[x][y]["coordonnes_tuiles"]
                    x_pos = (position_tuiles[0])*camera.zoom + self.largeur_fenetre/2 +35+ camera.deplacement.x 
                    y_pos=  (position_tuiles[1])*camera.zoom + self.hauteur_fenetre/4 +10+ camera.deplacement.y 
                    
                     
                    tuile = pg.transform.scale(self.food.image,(self.food.image.get_width()*camera.zoom,self.food.image.get_height()*camera.zoom))
                    screen.blit(tuile,(x_pos,y_pos))

    def draw(self,screen,camera):
        self.draw_sand(screen,camera)
        self.draw_food(screen,camera)
        self.draw_bob(screen,camera)
       

