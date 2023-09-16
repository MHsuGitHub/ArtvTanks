"""
Artillery vs Tank 

simulation artillery barage on tanks


expansion ideas:
-make child class of tank to make ifv
-make child class of shell to make cluster munition
-moving tanks
-directional armor
-eliptical dispersion (only for unguided shells?)


limiting factors: advanced damage calculation using ballistics of fragments

@author: Mick
"""

import random
import pygame
import math
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy


class Entity:
    def __init__(self, entity_id, x, y, size, drawsize):
        self.id = entity_id
        self.x = x
        self.y = y
        self.size = size
        self.drawsize=drawsize
        self.state = 0
        

class Tank(Entity):
    def __init__(self, entity_id, x, y, size, drawsize, health, armor):
        super().__init__(entity_id, x, y, size, drawsize)
        self.health = health
        self.armor = armor
        self.damaged_subsystems = []
        self.maxhealth = health
        self.round_destroyed = None
        
        
    def evaluate_state(self, current_round):
        if self.health <= 0:
            self.state=2 #dead
            self.round_destroyed = current_round
        elif self.health <= self.maxhealth/2:
            self.state=3 #very damaged
        elif tank.damaged_subsystems:
           self.state=1 #damaged


class ArtilleryShell(Entity):
    def __init__(self, entity_id, x, y, size, drawsize, blast_radius, explosion_power):
        super().__init__(entity_id, x, y, size, drawsize)
        self.blast_radius = blast_radius
        self.explosion_power = explosion_power
        self.round_exploded = None


class Terrain:
    def __init__(self, width, height, surface):
        self.surface = surface
        self.width = width
        self.height = height
        self.craters = []
        self.explosions = []
        self.tanks = []
        
        self.x_scale = window_width / sim_width
        self.y_scale = window_height / sim_height
        self.r_scale = min(self.x_scale, self.y_scale)
        
        self.x_offset = max(0, (window_width - sim_width * self.r_scale) / 2)
        self.y_offset = max(0, (window_height - sim_height * self.r_scale) / 2)
        

    def add_crater(self, x, y, radius):
        self.craters.append((x, y, radius))

    def add_explosion(self, x, y, radius1, radius2):
        self.explosions.append((x, y, radius1, radius2))

    def add_tank(self, tank):
        self.tanks.append(tank)

    def clear_explosion(self):
        self.explosions = []
        
    def draw_scale_sprite(self, input_sprite, x, y, radius, new_size=0):
        window_x = x * self.r_scale + self.x_offset
        window_y = y * self.r_scale + self.y_offset
        window_radius = radius * self.r_scale
        if new_size==0:
            new_size=(int(window_radius*2), int(window_radius*2))

        scaled_sprite = pygame.transform.scale(input_sprite, (new_size[0], new_size[1]))
        self.surface.blit(scaled_sprite, (window_x - window_radius, window_y - window_radius))

    def draw_all(self):
        self.surface.fill((0,0,0))  # Fill with black color first to create the backdrop
        scaled_background = pygame.transform.scale(background_image, (window_width, window_height))
        self.surface.blit(scaled_background, (0, 0))
        
        for crater in self.craters:
            x, y, radius = crater
            self.draw_scale_sprite(crater_image,x,y,radius)
        
        for explosion in self.explosions:
            x, y, radius1, radius2 = explosion
            self.draw_scale_sprite(explosion_image,x,y,radius1)
            self.draw_scale_sprite(shockwave_image,x,y,radius2)
        
        for tank in self.tanks:
            new_tank_width = tank.drawsize * self.r_scale * 2
            new_tank_height = new_tank_width * (original_tank_height / original_tank_width)

            if tank.state==0:
                self.draw_scale_sprite(tank_image, tank.x, tank.y, tank.drawsize, (new_tank_width, new_tank_height))
            elif tank.state==2:
                self.draw_scale_sprite(dead_tank_image, tank.x, tank.y, tank.drawsize, (new_tank_width, new_tank_height))
            else:
                self.draw_scale_sprite(damaged_tank_image, tank.x, tank.y, tank.drawsize, (new_tank_width, new_tank_height))
                

def load_image(path):
    """Load an image, set its color key, and return it along with its original dimensions."""
    image = pygame.image.load(path).convert()
    image.set_colorkey((255, 255, 255))  # Set white as transparent color
    original_width, original_height = image.get_size()
    return image, original_width, original_height

def calculate_distance(x1, y1, r1, x2, y2, r2=0):
    return max(0, math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) - r1 - r2)

def simulate_impact(tank, shell, current_round=0):
    """Simulate the impact of a shell on a tank."""
    #handle shell state    
    shell.state = 1 #set shell to exploded
    shell.round_exploded = current_round

    distance = calculate_distance(tank.x, tank.y, tank.size, shell.x, shell.y, shell.size )
    if distance <= shell.blast_radius:
        # Compute power of explosion at this distance with quadratic drop off
        power_at_distance = shell.explosion_power * ((1 - distance / shell.blast_radius) ** 2)

        # Check if the shell lands on top of the tank
        if distance == 0:
            tank.health -= 10
            return
        
        if power_at_distance >= tank.armor:
            tank.health -= 5  
            possible_subsystems = ["ENGINE", "CREW WOUNDED", "MAIN GUN", "TRACKS" ]
            damaged_subsystem = random.choice(possible_subsystems)
            if damaged_subsystem not in tank.damaged_subsystems:
                tank.damaged_subsystems.append(damaged_subsystem)
    
            damage_chance = power_at_distance/tank.armor
            damage_roll = random.uniform(0, 1)
            if damage_roll < damage_chance:
                # The tank is damaged, randomly select a subsystem to damage
                possible_subsystems = ["optics", "antenna", "gun sight", "external mg", "smoke launchers", "reactive armor" ]
                damaged_subsystem = random.choice(possible_subsystems)
                if damaged_subsystem not in tank.damaged_subsystems:
                    tank.damaged_subsystems.append(damaged_subsystem)

        tank.evaluate_state(current_round)

  
def fire_shell(target_area, target_accuracy):
        x = random.uniform(target_area[0], target_area[1])
        x = random.gauss(x, target_accuracy)
        y = random.uniform(target_area[2], target_area[3])
        y = random.gauss(y, target_accuracy)     
        return x, y
    
def run_simulation(tank_list_start, target_params, shell_params, shells_per_volley, num_rounds, num_simulations = 1):
    results = []
    for sim in range(num_simulations):
        # Resetting/Initializing the tanks and shells
        tank_list = deepcopy(tank_list_start)
        shell_volley = []

        current_round = 0
        for current_round in range(num_rounds):
            for nn in range(shells_per_volley):
                x, y = fire_shell(*target_params)  
                shell = ArtilleryShell(nn, x, y, *shell_params)
                shell_volley.append(shell)
            
            for shell in shell_volley:
                if shell.state==0:
                    for tank in tank_list:
                        simulate_impact(tank, shell, current_round)

            num_tanks_destroyed = sum(t.state == 2 or t.state == 3 for t in tank_list)
            #track rounds to destroy 3 tanks
            if num_tanks_destroyed >= 3: 
                results.append(current_round+1)
                break
            elif current_round == (num_rounds-1):
                results.append(current_round+1)
            
    return results, tank_list, shell_volley

#sim parameters
#random.seed(1)
window_width, window_height = 1000, 1000 # window size
sim_width, sim_height = 220, 220 # simulation size
num_rounds = 300
num_simulations = 1000
display_mode = 0

# tank parameters
tank_armor = 70 
tank_health = 10
tank_size = math.sqrt(3.6*6.95/math.pi) #equivalent circular area radius
tank_drawsize = 3/2 #width

# tank positions
formation_offset = np.arange(30,181,30)
formation_x = 110
tank_coordinates = [(formation_x, formation_offset[0]), (formation_x, formation_offset[1]), (formation_x, formation_offset[2]), (formation_x, formation_offset[3]), (formation_x, formation_offset[4]), (formation_x, formation_offset[5])]

# shell parameters
shells_per_volley = 6 #battery of 6 artillery pieces
target_accuracy = 150*1.48 #CEP converted to mu in gaussian; CEP: excalibur=4, PGK=20, conventional=110,150,250 
blast_radius = 100
explosion_power = 100
shell_size = 0
blast_draw_size = 3
target_area = (formation_x-2, formation_x+2, formation_offset[0]-2,  formation_offset[-1]+2) #(-x, +x, -y, +y)
shell_params = (shell_size, blast_draw_size, blast_radius, explosion_power)
target_params = (target_area, target_accuracy)


#Init tanks to simulate
tank_list = []
for i, (x, y) in enumerate(tank_coordinates):
    tank = Tank(i+1, x, y, tank_size, tank_drawsize, tank_health, tank_armor)
    tank_list.append(tank)
    
if display_mode==0:
    #init pygame screen
    pygame.init()
    clock = pygame.time.Clock()
    window = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Artillery vs Tanks Simulation")
    
    # Load images 
    image_path ='AvT_Sprites'
    background_image, _, _ = load_image(image_path+'\\background3.png')
    tank_image, original_tank_width, original_tank_height = load_image(image_path+'\\tank_t72.png')
    damaged_tank_image, _, _ = load_image(image_path+'\\tank_t72_damaged.png')
    dead_tank_image, _, _ = load_image(image_path+'\\tank_t72_destroyed.png')
    explosion_image, _, _ = load_image(image_path+'\\explosion.png')
    crater_image, _, _ = load_image(image_path+'\\crater.png')
    shockwave_image, _, _ = load_image(image_path+'\\shockwave2.png')

    #Init terrain to draw
    terrain = Terrain(sim_width, sim_height, window)
    for tank in tank_list:
        terrain.add_tank(tank)
    
    running = True
    volley_number = 1
    current_round = 0
    shell_volley = []
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
        window.fill((0, 0, 0))
        
        if current_round == 0:
            terrain.draw_all()
            pygame.display.flip()
            pygame.time.delay(1000)
        
        num_tanks_destroyed = sum(t.state == 2 or t.state == 3 for t in tank_list)
        if num_tanks_destroyed >= 3: 
             pass
        else:
            if current_round < num_rounds:
                volley_number += 1
                for nn in range(shells_per_volley):
                    x, y = fire_shell(target_area, target_accuracy)  
                    shell = ArtilleryShell(nn, x, y, shell_size, blast_draw_size, blast_radius, explosion_power)
                    shell_volley.append(shell)
                    
                    
                    terrain.add_explosion(shell.x, shell.y, shell.drawsize, shell.blast_radius)
                    terrain.add_crater(shell.x, shell.y, shell.drawsize)
        
            for shell in shell_volley:
                if shell.state==0:
                    for tank in tank_list:
                        simulate_impact(tank, shell, current_round)
    
        terrain.draw_all()
        pygame.display.flip()
        clock.tick(10) #fps
            
        if current_round < num_rounds:
            current_round += 1
            terrain.clear_explosion()

            
    pygame.quit()
    
    #print results
    print(f'Simulation complete.\nFired {volley_number} vollys using {volley_number*shells_per_volley} shells in total.')
    for tank in tank_list:
        if tank.state == 2:
            print(f'Tank {tank.id}: Destroyed')
        elif tank.state==1:
            damaged_systems_str = ', '.join(tank.damaged_subsystems)
            print(f'Tank {tank.id}: Damaged - {damaged_systems_str}')
        elif tank.state==3:
                damaged_systems_str = ', '.join(tank.damaged_subsystems)
                print(f'Tank {tank.id}: Very Damaged - {damaged_systems_str}')
        else:
            print(f'Tank {tank.id}: Intact')

    
elif display_mode==1:
    results, tank_list_sim, shell_volley_sim = run_simulation(tank_list, target_params, shell_params, shells_per_volley, num_rounds, num_simulations)
    
    plt.close('all')
    
    plt.hist(results, bins=max(results)-min(results), edgecolor='black')
    #plt.hist(results, bins=[1,2,3,4,5,6], edgecolor='black')
    #plt.title('Excalibur: CEP = 4 m')
    #plt.title('PGK: CEP = 20 m')
    plt.title('Unguided: CEP = 150 m')
    plt.xlabel(f'Number of volleys ({shells_per_volley} shells per volley)')
    plt.ylabel('Frequency')
    plt.show()
    
    results.sort()
    print(np.mean(results))
    print(results[79999])
    