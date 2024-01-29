import random
from movement import movement

class Cell():
    def __init__(self,world,spawn_x,spawn_y,energy,velocity=-1,mass=-1,perception=-1,memory=-1,friendship=-1):
        self.x=spawn_x
        self.y=spawn_y

        self.px = spawn_x
        self.py = spawn_y

        self.energy     = energy
        self.energy_max = world.config["MAX_ENERGY"]
        self.cost       = 1

        self.velocity   = world.config["INIT_VELOCITY"] if velocity == -1 else velocity
        self.buffer     = 0

        self.mass = world.config["INIT_MASS"] if mass == -1 else mass

        self.perception = world.config["INIT_PERCEPTION"] if perception == -1 else perception

        self.memory = world.config["INIT_MEMORY"] if memory == -1 else memory
        self.memory_left = self.memory
        self.memorised_positions = []
        self.memorised_food = []

        self.friendship = world.config["INIT_FRIENDSHIP"] if friendship == -1 else friendship
        self.friendship_left = self.friendship
        self.friends = []

        # I'm removing this, and self.image (which has been moved to the Environment)
        # This was neccessary for pickling
        #self.world = world
        
        self.alive = True

        self.predator = False

    def move(self,direction,surroundings,config,world, bobs):
        self.px = self.x
        self.py = self.y

        distance = int(self.velocity + self.buffer)
        self.buffer = self.velocity + self.buffer  - distance

        best_food = surroundings["food"]
        for i in range(len(self.friends)):
            friends_surroundings = self.friends[i].get_viewable_bobs(world)[1:]
            f = self.friends[i].view_surroundings(world, friends_surroundings[0],friends_surroundings[1])["food"]
            if f[2] > best_food[2]:
                best_food = f

        # Check for a predator to run away from
        if surroundings["predator"] != None:
            predator = surroundings["predator"]
            self.predator = False
            if self.x < predator.x:
                direction = movement.LEFT.value
            elif self.x > predator.x:
                direction = movement.RIGHT.value
            elif self.y < predator.y:
                direction = movement.DOWN.value
            elif self.y > predator.y:
                direction = movement.UP.value

        # Check that a nearby food was found
        elif best_food[2] > 0:
            food = best_food
            self.predator = False
            if self.x < food[0]:
                direction = movement.RIGHT.value
            elif self.x > food[0]:
                direction = movement.LEFT.value
            elif self.y < food[1]:
                direction = movement.UP.value
            elif self.y > food[1]:
                direction = movement.DOWN.value
        
        # Check for prey instead
        elif surroundings["prey"] != None:
            prey = surroundings["prey"]
            self.predator = True
            if self.x < prey.x:
                direction = movement.RIGHT.value
            elif self.x > prey.x:
                direction = movement.LEFT.value
            elif self.y < prey.y:
                direction = movement.UP.value
            elif self.y > prey.y:
                direction = movement.DOWN.value
        
        # Remember any food
        elif len(self.memorised_food) > 0:
            # Keep looking for a valid food to find
            target_found = False
            i = 0
            while not target_found and i < len(self.memorised_food):
                if self.memorised_food[i][0] > config["MAP_WIDTH"]:
                    continue
                if self.memorised_food[i][1] > config["MAP_HEIGHT"]:
                    continue

                # Is it within distance?
                dx = abs(self.x - self.memorised_food[i][0])
                dy = abs(self.y - self.memorised_food[i][1])
                if dx + dy > self.perception:
                    # Since we can't see it, we haven't already check it
                    # by simply looking at it
                    target_found = True
                    break

                # Check next memorised food
                i += 1
            
            if target_found:
                food = self.memorised_food[i]
                if self.x < food[0]:
                    direction = movement.RIGHT.value
                elif self.x > food[0]:
                    direction = movement.LEFT.value
                elif self.y < food[1]:
                    direction = movement.UP.value
                elif self.y > food[1]:
                    direction = movement.DOWN.value

        #Movement
        match (direction):
            case movement.LEFT.value:
                if self.x > 0:
                    self.x = self.x - distance
                else: 
                    direction = movement.STATION.value
            case movement.RIGHT.value:
                if self.x + 1 < config["MAP_WIDTH"]:
                    self.x = self.x + distance
                else: 
                    direction = movement.STATION.value
            case movement.UP.value:
                if self.y + 1 < config["MAP_HEIGHT"]:
                    self.y = self.y + distance
                else: 
                    direction = movement.STATION.value
            case movement.DOWN.value:
                if self.y > 0:
                    self.y = self.y - distance
                else: 
                    direction = movement.STATION.value

        # Remember this position
        if self.memory_left > 0 and direction != movement.STATION.value:
            self.memory_left -= 0.5
            self.memorised_positions.append((self.x, self.y))

        return direction

    def consume(self, world, config, prey):
        # How much the cell can eat
        energy_capacity = config["MAX_ENERGY"] - self.energy

        # If the food here has that much food
        if energy_capacity <= world.food.food[self.x,self.y]:
           # Fill up
           self.energy += energy_capacity

           # Remove some energy
           world.food.food[self.x,self.y] -= energy_capacity
        
        # Not enough food
        else:
           # Eat remaining food
           self.energy += world.food.food[self.x,self.y]

           # Food is now all gone
           world.food.food[self.x,self.y] = 0

        # Check whether the cell still has room to eat
        energy_capacity = config["MAX_ENERGY"] - self.energy
        if energy_capacity == 0:
            return
        
        # Try to find a cell that is smaller in the same position
        for i in range(len(prey)):
            # Check that the cell is in the same position
            if prey[i].x != self.x:
                continue
            if prey[i].y != self.y:
                continue

            # After all that we have found a valid cell to eat (:
            self.energy += prey[i].energy * (1-prey[i].mass/self.mass) / 2
            prey[i].energy = 0

            if self.energy > config["MAX_ENERGY"]:
                self.energy = config["MAX_ENERGY"]

    def view_surroundings(self, world, prey, predator):
        surroundings = {}

        # Find cell with smallest mass
        smallest_cell = None
        for i in range(len(prey)):
            if smallest_cell == None:
                smallest_cell = prey[i]
                continue

            if prey[i].mass < smallest_cell.mass:
                smallest_cell = prey[i]

        surroundings["prey"] = smallest_cell

        # Find all food within range
        viewable_food = []

        # Look in a square around the cell
        for x in range(self.x-self.perception,self.x+self.perception+1):
            for y in range(self.y-self.perception,self.y+self.perception+1):

                if x >= world.config["MAP_WIDTH"]:
                    continue
                if x < 0:
                    continue
                if y >= world.config["MAP_HEIGHT"]:
                    continue
                if y < 0:
                    continue
                
                # Get rid of the cells too far away
                dx = abs(x - self.x)
                dy = abs(y - self.y)
                if dx + dy > self.perception:
                    continue

                # Only look for food with anything remaining
                if world.food.food[x,y] > 0:
                    viewable_food.append((x, y, world.food.food[x,y]))
        
        # Find the food source with largest amount of food
        biggest_food = (0, 0, 0)
        for i in range(len(viewable_food)):
              # Find space to remember this food
            if self.memory_left + len(self.memorised_positions) // 2 >= 1 and biggest_food[2] != 0:
                self.memory_left -= 1
                self.memorised_food.append(viewable_food[i])
                  # Get rid of as many memories as neccessary
                while self.memory_left < 0:
                    self.memorised_positions = self.memorised_positions[1:]
                    self.memory_left += 0.5
            if viewable_food[i][2] > biggest_food[2]:
                biggest_food = viewable_food[i]

        surroundings["food"] = biggest_food

        

        # Check for any predators
        # Find cell with closest cell
        closest_cell = None
        closest_distance = 0
        for i in range(len(predator)):
            if closest_cell == None:
                closest_cell = predator[i]
                continue
            
            dx = abs(self.x - predator[i].x)
            dy = abs(self.y - predator[i].y)
            if dx + dy < closest_distance:
                closest_distance = dx + dy
                closest_cell = predator[i]


        surroundings["predator"] = closest_cell

        return surroundings

    def mate(self, world):
        for i in range(len(world.population)):
            # Check in the same cell
            if world.population[i].x != self.x:
                continue
            if world.population[i].y != self.y:
                continue

            if world.population[i] == self:
                continue

            # Check neither are edible
            if self.mass * 1.5 < world.population[i].mass:
                continue
            if world.population[i].mass * 1.5 < self.mass:
                continue
            
            # It has enough energy
            if world.population[i].energy < 150:
                continue
            
            self.energy -= 100
            world.population[i].energy -= 100

            world.reproduce_with_parents(self, world.population[i])
            break

    def forget(self):
        indexes = []

        # Get rid of any remembered food that is now within sight
        for i in range(len(self.memorised_food)):
            # Is it within distance?
            dx = abs(self.x - self.memorised_food[i][0])
            dy = abs(self.y - self.memorised_food[i][1])
            if dx + dy <= self.perception:
                # We can see it, don't need to remember it
                indexes.append(i)
        
        # Gain the points back
        self.memory_left += len(indexes)

        # Only remember the useful memories
        new_memorised_food = []
        for i in range(len(self.memorised_food)):
            valid = True

            for j in range(len(indexes)):
                # Should be forgotten
                if i == indexes[j]:
                    valid = False
                    break
            
            # Should not be forgotten
            if valid:
                new_memorised_food.append(self.memorised_food[i])
        self.memorised_food = new_memorised_food
    
    def lose_friends(self):
        indexes = []

        # Get rid of any friends that is not within sight
        for i in range(len(self.friends)):
            # Is it within distance?
            dx = abs(self.x - self.friends[i].x)
            dy = abs(self.y - self.friends[i].y)
            if dx + dy > self.perception:
                # We can see it, don't need to remember it
                indexes.append(i)
        
        # Gain the points back
        self.friendship_left += len(indexes)

        # Keeps only visible friends
        new_friends = []
        for i in range(len(self.friends)):
            valid = True

            for j in range(len(indexes)):
                # Should be unfriended
                if i == indexes[j]:
                    valid = False
                    break
            
            # Should keep friendship
            if valid:
                new_friends.append(self.friends[i])
        self.friends = new_friends

    def bound(self,config):
        # Keeps the cell within the map after moving
        if self.x < 0:
            self.x = 0
        elif self.x > config["MAP_WIDTH"]-1:
            self.x = config["MAP_WIDTH"]-1
        if self.y < 0:
            self.y = 0
        elif self.y > config["MAP_HEIGHT"]-1:
            self.y = config["MAP_HEIGHT"]-1
    
    def find_friends(self, bobs):
        for i in range(len(bobs)):
            if self.friendship_left == 0:
                return

            # Could it eat this cell?
            if bobs[i].mass > self.mass * 1.5:
                continue

            # Could this cell eat it?
            if self.mass > bobs[i].mass * 1.5:
                continue

            # Friend candidate
            self.friends.append(bobs[i])
            self.friendship_left -= 1
    
    def get_viewable_bobs(self, world):
        close_points = world.qtree.query(self.x-self.perception, self.x+self.perception, self.y-self.perception, self.y+self.perception)

        bobs = []
        for i in range(len(close_points)):
            # In Range?
            dx = abs(self.x - close_points[i].x)
            dy = abs(self.y - close_points[i].y)
            if dx + dy > self.perception:
                continue

            # Not Self
            if self == close_points[i].ref:
                continue

            # Viewable
            bobs.append(close_points[i].ref)
        
        prey = []
        for i in range(len(bobs)):
            if self.mass >= bobs[i].mass * 1.5:
                prey.append(bobs[i])
        
        predator = []
        for i in range(len(bobs)):
            if bobs[i].mass >= self.mass * 1.5:
                predator.append(bobs[i])
        
        return (bobs, prey, predator)

    def update(self,world,game,config,mouse_pos):
        bobs, prey, predator = self.get_viewable_bobs(world)

        self.bound(config)

        self.find_friends(bobs)

        # Move the cell using it's surroundings to help, then lose energy accordingly
        match (self.move(random.randint(0,4), self.view_surroundings(world, prey, predator),config,world, bobs)):
            case movement.STATION.value:
                self.energy -= self.cost
            case _:
                self.energy -= (self.mass*self.velocity*self.velocity + (1/5)*self.perception + (1/5)*self.memory + (1/5)*self.friendship)

        self.bound(config)
        self.consume(world, config, prey)

        # Check if there is another cell here to mate with
        if self.energy > 150:
            self.mate(world)

        if (self.energy <= 0):
            self.energy = 0
            self.alive = False
        if (int(self.energy) >= self.energy_max):
            if config["SINGLE_REPRODUCTION"]:
                self.energy = 150
                world.reproduce(self.x,self.y,self.velocity,self.perception,self.memory,self.friendship)
        
        self.forget()
        self.lose_friends()