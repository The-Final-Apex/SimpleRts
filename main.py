# Once again there are more errors

import pygame
import random
import math

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)

# Game setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple RTS Game")
clock = pygame.time.Clock()

# Game classes
class Unit:
    def __init__(self, x, y, team, unit_type="worker"):
        self.x = x
        self.y = y
        self.team = team  # "player" or "enemy"
        self.unit_type = unit_type
        self.selected = False
        self.target_x = x
        self.target_y = y
        self.speed = 2 if unit_type == "worker" else 1.5
        self.health = 50 if unit_type == "worker" else 100
        self.attack_cooldown = 0
        self.attack_range = 50 if unit_type == "soldier" else 0
        self.attack_damage = 10
        
    def draw(self, surface):
        color = BLUE if self.team == "player" else RED
        radius = 10 if self.unit_type == "worker" else 15
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), radius)
        
        if self.selected:
            pygame.draw.circle(surface, GREEN, (int(self.x), int(self.y)), radius + 5, 2)
        
        # Health bar
        bar_width = 20
        health_percent = self.health / (50 if self.unit_type == "worker" else 100)
        pygame.draw.rect(surface, RED, (self.x - bar_width//2, self.y - 20, bar_width, 5))
        pygame.draw.rect(surface, GREEN, (self.x - bar_width//2, self.y - 20, int(bar_width * health_percent), 5))
    
    def update(self, units, resources):
        # Movement
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 5:  # If not at target
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
        
        # Combat
        if self.attack_range > 0 and self.attack_cooldown <= 0:
            closest_enemy = None
            closest_distance = float('inf')
            
            for unit in units:
                if unit.team != self.team:
                    dist = math.sqrt((unit.x - self.x)**2 + (unit.y - self.y)**2)
                    if dist < self.attack_range and dist < closest_distance:
                        closest_enemy = unit
                        closest_distance = dist
            
            if closest_enemy:
                closest_enemy.health -= self.attack_damage
                self.attack_cooldown = 30  # 0.5 seconds at 60 FPS
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Resource gathering (for workers)
        if self.unit_type == "worker":
            for resource in resources:
                dist = math.sqrt((resource.x - self.x)**2 + (resource.y - self.y)**2)
                if dist < 20 and resource.amount > 0:
                    resource.amount -= 0.1
                    if self.team == "player":
                        global player_resources
                        player_resources += 0.1

class Resource:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.amount = random.randint(50, 150)
    
    def draw(self, surface):
        pygame.draw.circle(surface, GOLD, (int(self.x), int(self.y)), 8)
        # Display remaining amount
        font = pygame.font.SysFont(None, 20)
        text = font.render(str(int(self.amount)), True, WHITE)
        surface.blit(text, (self.x - 10, self.y - 25))

class Building:
    def __init__(self, x, y, team, building_type="base"):
        self.x = x
        self.y = y
        self.team = team
        self.building_type = building_type
        self.health = 500 if building_type == "base" else 300
        self.production_cooldown = 0
    
    def draw(self, surface):
        color = BLUE if self.team == "player" else RED
        width = 40 if self.building_type == "base" else 30
        pygame.draw.rect(surface, color, (self.x - width//2, self.y - width//2, width, width))
        
        # Health bar
        # TODO: This is also stupid
        
        bar_width = 30
        health_percent = self.health / (500 if self.building_type == "base" else 300)
        pygame.draw.rect(surface, RED, (self.x - bar_width//2, self.y - 30, bar_width, 5))
        pygame.draw.rect(surface, GREEN, (self.x - bar_width//2, self.y - 30, int(bar_width * health_percent), 5))
    
    def update(self, units):
        if self.building_type == "barracks" and self.production_cooldown <= 0:
            self.production_cooldown = 180  # 3 seconds at 60 FPS
            if self.team == "player" and player_resources >= 50:
                units.append(Unit(self.x + random.randint(-20, 20), 
                            self.y + random.randint(-20, 20), 
                            self.team, "soldier"))
                player_resources -= 50
            elif self.team == "enemy":
                units.append(Unit(self.x + random.randint(-20, 20), 
                            self.y + random.randint(-20, 20), 
                            self.team, "soldier"))
        
        if self.production_cooldown > 0:
            self.production_cooldown -= 1

# Game state
player_units = [Unit(100, 100, "player", "worker") for _ in range(3)]
enemy_units = [Unit(700, 500, "enemy", "worker") for _ in range(2)]
enemy_units.append(Unit(650, 450, "enemy", "soldier"))
all_units = player_units + enemy_units

player_buildings = [Building(100, 200, "player", "base"), Building(200, 200, "player", "barracks")]
enemy_buildings = [Building(700, 400, "enemy", "base"), Building(600, 400, "enemy", "barracks")]
all_buildings = player_buildings + enemy_buildings

resources = [Resource(random.randint(100, SCREEN_WIDTH-100), 
                     random.randint(100, SCREEN_HEIGHT-100)) for _ in range(10)]

player_resources = 100
selected_units = []
selection_start = None
selection_end = None

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = pygame.mouse.get_pos()
                selection_start = (mouse_x, mouse_y)
                
                # Check if clicked on a unit
                clicked_unit = None
                for unit in player_units:
                    dist = math.sqrt((unit.x - mouse_x)**2 + (unit.y - mouse_y)**2)
                    if dist < 15:
                        clicked_unit = unit
                        break
                
                if clicked_unit:
                    if not pygame.key.get_pressed()[pygame.K_LSHIFT]:
                        for unit in player_units:
                            unit.selected = False
                    clicked_unit.selected = True
                    if clicked_unit not in selected_units:
                        selected_units.append(clicked_unit)
                else:
                    for unit in player_units:
                        unit.selected = False
                    selected_units = []
            
            elif event.button == 3:  # Right click
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for unit in selected_units:
                    unit.target_x = mouse_x
                    unit.target_y = mouse_y
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                mouse_x, mouse_y = pygame.mouse.get_pos()
                selection_end = (mouse_x, mouse_y)
                
                if selection_start and selection_end:
                    # Box selection
                    x1, y1 = selection_start
                    x2, y2 = selection_end
                    left = min(x1, x2)
                    right = max(x1, x2)
                    top = min(y1, y2)
                    bottom = max(y1, y2)
                    
                    for unit in player_units:
                        if (left <= unit.x <= right and top <= unit.y <= bottom):
                            unit.selected = True
                            if unit not in selected_units:
                                selected_units.append(unit)
                        else:
                            if not pygame.key.get_pressed()[pygame.K_LSHIFT]:
                                unit.selected = False
                                if unit in selected_units:
                                    selected_units.remove(unit)
                
                selection_start = None
                selection_end = None
        # We live in a bad bad world : (
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b and player_resources >= 100:
                # Build barracks at average position of selected units
                if selected_units:
                    avg_x = sum(unit.x for unit in selected_units) / len(selected_units)
                    avg_y = sum(unit.y for unit in selected_units) / len(selected_units)
                    player_buildings.append(Building(avg_x, avg_y, "player", "barracks"))
                    all_buildings.append(player_buildings[-1])
                    player_resources -= 100
            
            elif event.key == pygame.K_w and player_resources >= 25:
                # Create worker
                if player_buildings:
                    spawn_point = random.choice(player_buildings)
                    player_units.append(Unit(spawn_point.x, spawn_point.y, "player", "worker"))
                    all_units.append(player_units[-1])
                    player_resources -= 25
            
            elif event.key == pygame.K_s and player_resources >= 50:
                # Create soldier
                if any(b.building_type == "barracks" for b in player_buildings):
                    barracks = [b for b in player_buildings if b.building_type == "barracks"][0]
                    player_units.append(Unit(barracks.x, barracks.y, "player", "soldier"))
                    all_units.append(player_units[-1])
                    player_resources -= 50
    
    # Update game state
    for unit in all_units[:]:
        unit.update(all_units, resources)
        if unit.health <= 0:
            if unit in player_units:
                player_units.remove(unit)
            if unit in enemy_units:
                enemy_units.remove(unit)
            if unit in all_units:
                all_units.remove(unit)
            if unit in selected_units:
                selected_units.remove(unit)
    
    for building in all_buildings[:]:
        building.update(all_units)
        if building.health <= 0:
            if building in player_buildings:
                player_buildings.remove(building)
            if building in enemy_buildings:
                enemy_buildings.remove(building)
            if building in all_buildings:
                all_buildings.remove(building)
    
    resources = [r for r in resources if r.amount > 0]
    
    # Spawn new resources occasionally
    if random.random() < 0.005 and len(resources) < 15:
        resources.append(Resource(random.randint(50, SCREEN_WIDTH-50), 
                               random.randint(50, SCREEN_HEIGHT-50)))
    
    # Enemy AI (very simple)
    if random.random() < 0.01 and enemy_units:
        worker = random.choice([u for u in enemy_units if u.unit_type == "worker"])
        if resources:
            target = random.choice(resources)
            worker.target_x = target.x
            worker.target_y = target.y
    
    # Draw everything
    screen.fill(BLACK)
    
    # Draw selection box
    if selection_start and pygame.mouse.get_pressed()[0]:
        current_pos = pygame.mouse.get_pos()
        rect = pygame.Rect(min(selection_start[0], current_pos[0]),
                          min(selection_start[1], current_pos[1]),
                          abs(current_pos[0] - selection_start[0]),
                          abs(current_pos[1] - selection_start[1]))
        pygame.draw.rect(screen, GREEN, rect, 1)
    
    # Draw resources
    for resource in resources:
        resource.draw(screen)
    
    # Draw buildings
    for building in all_buildings:
        building.draw(screen)
    
    # Draw units
    for unit in all_units:
        unit.draw(screen)
    
    # Draw UI
    font = pygame.font.SysFont(None, 36)
    resources_text = font.render(f"Resources: {int(player_resources)}", True, WHITE)
    screen.blit(resources_text, (10, 10))
    
    units_text = font.render(f"Units: {len(player_units)}", True, WHITE)
    screen.blit(units_text, (10, 50))
    
    controls_text = font.render("B: Build Barracks (100) | W: Train Worker (25) | S: Train Soldier (50)", True, WHITE)
    screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
