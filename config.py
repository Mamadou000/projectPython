from enum import Enum

MAP_WIDTH   = 100
MAP_HEIGHT  = 100

FOOD = 200
BOBS = 100

FOOD_ENERGY     = 100
SPAWN_ENERGY    = 100
SPAWN_ENERGY_NEW_BOB = 50
MAX_ENERGY      = 500
ENERGY_COST     = 1

#Color code

WHITE   = (255,255,255)
BLACK   = (0,0,0)
RED     = (255,0,0)

class movement(Enum):
    STATION = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4