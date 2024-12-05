import pyglet
import random
import math

# Constants
WIDTH = 1200
HEIGHT = 900
GRID_SIZE = 50
SIDEBAR_WIDTH = 280
FPS = 0  # Initial FPS (paused)
MIN_FPS = 1
MAX_FPS = 60
NEST_CENTER_X = WIDTH // 4  # Center of the nest area
NEST_CENTER_Y = HEIGHT // 2
FOOD_STORAGE_RADIUS = 5 * GRID_SIZE
NURSERY_RADIUS = 3 * GRID_SIZE
SLEEPING_RADIUS = 4 * GRID_SIZE
CONTROL_PANEL_HEIGHT = 90
STATS_PANEL_HEIGHT = 220
LEGEND_PANEL_HEIGHT = 520
TOP_MARGIN = 15
PANEL_SPACING = 15

# Update Constants with refined sizes and spacing
SIDEBAR_WIDTH = 280        # Slightly wider for better text display
TOP_MARGIN = 15           # Slightly larger margin
PANEL_SPACING = 15        # Increased spacing between panels

# Panel heights
CONTROL_PANEL_HEIGHT = 90  # Reduced as it only contains FPS control
STATS_PANEL_HEIGHT = 220  # Increased for stats content
LEGEND_PANEL_HEIGHT = 520  # Increased for legend content

# Legend specific constants
LEGEND_ITEM_SPACING = 24   # Space between legend items
LEGEND_HEADER_SPACING = 30 # Space after headers
LEGEND_GROUP_SPACING = 15  # Additional space between groups
LEGEND_TEXT_SIZE = 10      # Text size
LEGEND_HEADER_SIZE = 12    # Header text size
LEGEND_ICON_SIZE = 16      # Icon size
LEGEND_TOP_PADDING = 50    # Space from top of panel to first item

# Constants for area positioning (add these near other constants)
QUADRANT_OFFSET = 300  # Increased distance between centers to prevent overlap

# Create a simple rectangle class for panel sections
class Panel:
    def __init__(self, x, y, width, height, title=""):
        self.width = width
        self.height = height
        self.title = title
        self.update_position(x, y)  # Separate position update
        
    def update_position(self, x, y):
        """Update panel position"""
        self.x = x
        self.y = y
        
    def draw(self):
        # Draw panel background
        pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height, 
                              color=(40, 40, 40)).draw()
        # Draw panel border
        pyglet.shapes.BorderedRectangle(self.x, self.y, self.width, self.height,
                                      border=2, color=(40, 40, 40), 
                                      border_color=(100, 100, 100)).draw()
        # Draw title if exists
        if self.title:
            pyglet.text.Label(self.title,
                            font_name='Arial',
                            font_size=12,
                            bold=True,
                            x=self.x + 10,
                            y=self.y + self.height - 20,
                            anchor_x='left',
                            anchor_y='center').draw()

# Create a simple slider class
class Slider:
    def __init__(self, x, y, width, min_value, max_value, initial_value):
        self.x = x
        self.y = y
        self.width = width
        self.height = 10
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.dragging = False
        
        # Calculate initial handle position
        self.handle_x = self.x + (self.value - self.min_value) / (self.max_value - self.min_value) * self.width
        self.handle_radius = 8
        
    def draw(self):
        # Draw slider track
        pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height, 
                              color=(100, 100, 100)).draw()
        # Draw handle
        pyglet.shapes.Circle(self.handle_x, self.y + self.height/2, 
                           self.handle_radius, color=(200, 200, 200)).draw()
        
    def hit_test(self, x, y):
        return (self.x <= x <= self.x + self.width and 
                self.y - self.handle_radius <= y <= self.y + self.height + self.handle_radius)
    
    def update_value(self, x):
        self.handle_x = min(max(x, self.x), self.x + self.width)
        normalized_value = (self.handle_x - self.x) / self.width
        self.value = round(self.min_value + normalized_value * (self.max_value - self.min_value))
        return self.value

# Create the window with resizable=False and fixed size
window = pyglet.window.Window(WIDTH, HEIGHT, "Creature Simulation", resizable=False)

# Load images for buttons
pause_unclicked_image = pyglet.resource.image('Assets/UI Icons/pause-play-unclick.png')
pause_clicked_image = pyglet.resource.image('Assets/UI Icons/pause-play-click.png')

play_unclicked_image = pyglet.resource.image('Assets/UI Icons/play-button-unclick.png')
play_clicked_image = pyglet.resource.image('Assets/UI Icons/play-button-click.png')

fast_forward_unclicked_image = pyglet.resource.image('Assets/UI Icons/fast-forward-button-unclick.png')
fast_forward_clicked_image = pyglet.resource.image('Assets/UI Icons/fast-forward-button-click.png')

# Create sprites for buttons with scaling
icon_scale = 0.075  # Adjusted scale factor

# Calculate the y position to be below the "Controls" label
buttons_y_position = HEIGHT - CONTROL_PANEL_HEIGHT + 20  # Reduced from 120 to 20 to move buttons higher

# Create panels before anything else
control_panel = Panel(
    WIDTH - SIDEBAR_WIDTH - TOP_MARGIN,
    HEIGHT - TOP_MARGIN - CONTROL_PANEL_HEIGHT,
    SIDEBAR_WIDTH,
    CONTROL_PANEL_HEIGHT,
    "Controls"
)

stats_panel = Panel(
    WIDTH - SIDEBAR_WIDTH - TOP_MARGIN,
    HEIGHT - TOP_MARGIN - CONTROL_PANEL_HEIGHT - PANEL_SPACING - STATS_PANEL_HEIGHT,
    SIDEBAR_WIDTH,
    STATS_PANEL_HEIGHT,
    "Stats"
)

legend_panel = Panel(
    WIDTH - SIDEBAR_WIDTH - TOP_MARGIN,
    HEIGHT - TOP_MARGIN - CONTROL_PANEL_HEIGHT - PANEL_SPACING - 
    STATS_PANEL_HEIGHT - PANEL_SPACING - LEGEND_PANEL_HEIGHT,
    SIDEBAR_WIDTH,
    LEGEND_PANEL_HEIGHT,
    "Legend"
)

# Create stats label
stats_label = pyglet.text.Label(
    "No creature selected",
    font_name='Arial',
    font_size=10,
    x=WIDTH - SIDEBAR_WIDTH - TOP_MARGIN + 15,
    y=stats_panel.y + stats_panel.height - 40,
    width=SIDEBAR_WIDTH - 30,
    multiline=True,
    anchor_x='left',
    anchor_y='top'
)

# THEN create the button sprites with pause initially clicked
pause_button = pyglet.sprite.Sprite(
    pause_clicked_image,  # Start with clicked image
    x=WIDTH - SIDEBAR_WIDTH + 15, 
    y=control_panel.y + control_panel.height - 75
)
pause_button.scale = icon_scale

play_button = pyglet.sprite.Sprite(
    play_unclicked_image, 
    x=WIDTH - SIDEBAR_WIDTH + 75, 
    y=control_panel.y + control_panel.height - 75
)
play_button.scale = icon_scale

fast_forward_button = pyglet.sprite.Sprite(
    fast_forward_unclicked_image, 
    x=WIDTH - SIDEBAR_WIDTH + 135, 
    y=control_panel.y + control_panel.height - 75
)
fast_forward_button.scale = icon_scale

# Variable to track if FPS input is active
fps_input_active = False

# Add this near the top with other global variables
current_speed_state = "pause"  # Start paused

# Update Constants section - add new indicator constants
INDICATOR_BORDER_WIDTH = 2
SELECTION_RING_SIZE = 4
STATUS_RING_SIZE = 2
INNER_CIRCLE_RATIO = 0.6  # Size of inner circle relative to main body

class Creature:
    def __init__(self, x, y, environment, health=100, energy=100):
        # Initialize all attributes first
        self.egg_laying_cooldown = 0
        self.egg_laying_cooldown_max = 100
        self.rest_threshold = 30
        self.wake_threshold = 80
        self.max_age = random.randint(500, 750)
        self.selected = False
        
        # Then set the basic attributes
        self.x = x
        self.y = y
        self.env = environment
        self.health = health
        self.energy = energy
        self.hunger = 100
        self.age = 0
        self.mature = False
        self.dead = False
        self.sleeping = False
        self.eating = False
        self.base_color = (0, 255, 0)  # Store base color for normal state
        self.color = self.base_color
        self.happiness = 100
        self.food_value = 100
        self.age_related_health_loss = False
        self.carrying_food = False
        self.target = None
        self.egg = False
        self.has_laid_egg = False
        self.dragging_target = None  # Add this new attribute

    def calculate_happiness(self):
        """Calculate creature happiness based on various factors"""
        happiness = 100
        
        if self.hunger < 50:
            happiness -= (50 - self.hunger)
        if self.energy < 50:
            happiness -= (50 - self.energy)
        if self.health < 50:
            happiness -= (50 - self.health)
        
        return max(0, min(100, happiness))

    def move(self, max_x, max_y):
        if self.dead:
            return
        
        # If we have a target that's a creature or egg, get its position
        target_x, target_y = self.x, self.y
        
        if isinstance(self.target, Creature) and self.target.dead:
            if self.carrying_food:
                # If carrying food, move towards food storage area
                food_center = self.env.get_area_center("food")
                target_x = int(food_center[0] / GRID_SIZE)
                target_y = int(food_center[1] / GRID_SIZE)
            else:
                # If not carrying yet, move towards the dead creature
                target_x, target_y = self.target.x, self.target.y
        elif isinstance(self.target, (Creature, Egg)):
            target_x, target_y = self.target.x, self.target.y
        elif self.target == "sleeping":
            center = self.env.get_area_center("sleeping")
            target_x = int(center[0] / GRID_SIZE)
            target_y = int(center[1] / GRID_SIZE)
        elif self.target == "nursery":
            center = self.env.get_area_center("nursery")
            target_x = int(center[0] / GRID_SIZE)
            target_y = int(center[1] / GRID_SIZE)
        elif self.target == "food":
            # First check if there's food adjacent to eat
            nearby_entities = self.env.get_nearby_entities(self.x, self.y)
            for entity in nearby_entities:
                if isinstance(entity, Creature) and entity.dead and entity.food_value > 0:
                    dx = abs(self.x - entity.x)
                    dy = abs(self.y - entity.y)
                    if dx + dy == 1:  # Adjacent but not diagonal
                        if self.eat(entity):
                            self.target = None
                            return
            
            # If no adjacent food, find nearest food source
            food_position = self.env.find_nearest_food(self.x, self.y)
            if food_position:
                target_x, target_y = food_position
            else:
                # If no food found, move randomly
                target_x = self.x + random.randint(-1, 1)
                target_y = self.y + random.randint(-1, 1)
        else:
            # Random movement with bias towards current direction
            if random.random() < 0.8:
                target_x = self.x + random.randint(-1, 1)
                target_y = self.y + random.randint(-1, 1)
            else:
                angle = random.uniform(0, 2 * 3.14159)
                target_x = self.x + round(math.cos(angle))
                target_y = self.y + round(math.sin(angle))
        
        # Ensure target is within bounds
        target_x = max(0, min(target_x, max_x - 1))
        target_y = max(0, min(target_y, max_y - 1))
        
        # Try to move towards target
        if self.env.try_move_towards(self, target_x, target_y):
            # If we successfully moved and we're carrying food to the food area
            if (self.carrying_food and 
                isinstance(self.target, Creature) and 
                self.target.dead and 
                self.env.is_in_area(self.target.x, self.target.y, "food")):
                # Release the food once it's in the storage area
                self.carrying_food = False
                self.target = None
                self.color = (0, 255, 0)  # Reset color

    def update(self):
        if self.dead:
            return  # Dead creatures don't update or move
            
        if not self.dead:
            # Always update basic stats first
            self.age += 1
            if self.age >= 20:
                self.mature = True
            
            # Age effects and death
            if self.age > self.max_age * 0.7:
                if random.random() < 0.1:
                    self.health = max(0, self.health - 1)
                    self.age_related_health_loss = True
            
            if self.age >= self.max_age:
                self.die()
                return

            # Always update hunger and energy - REDUCED RATES
            if random.random() < 0.2:  # Reduced from 0.5
                self.hunger = max(0, self.hunger - 1)
            energy_cost = 1 if self.eating or self.carrying_food else 0.5  # Reduced from 2/1
            self.energy = max(0, self.energy - energy_cost)

            # Health reduction from hunger - process this before other behaviors
            if self.hunger <= 0:
                self.health = max(0, self.health - 1)
                if self.health <= 0:
                    self.die()
                    return

            # Check for critical hunger - override sleep state
            if self.hunger <= 20:
                self.sleeping = False  # Wake up if starving
                self.target = "food"
                self.move(self.env.width, self.env.height)

            # Sleep behavior
            elif self.sleeping:
                if not self.env.is_in_area(self.x, self.y, "sleeping"):
                    self.move(self.env.width, self.env.height)
                else:
                    # Only sleep and recover energy if in sleep zone
                    recovery_rate = 3 if self.hunger > 50 else 1
                    self.energy = min(100, self.energy + recovery_rate)
                    
                    # Wake up conditions
                    if (self.energy >= self.wake_threshold or  # Enough energy
                        self.hunger <= 30 or                   # Getting hungry
                        self.health < 50):                     # Health issues
                        self.sleeping = False
                        self.color = (0, 255, 0)
                        self.target = None
                    else:
                        self.color = (100, 100, 255)  # Sleeping color

            # Check for sleep need - only if not critically hungry
            elif self.energy <= self.rest_threshold and self.hunger > 30:
                self.sleeping = True
                self.color = (100, 100, 255)
                self.target = "sleeping"

            # Awake behavior
            else:
                # Reset eating state but NOT carrying_food state
                self.eating = False
                if not self.carrying_food:
                    self.color = (0, 255, 0)

                # Move according to current state
                self.move(self.env.width, self.env.height)

                # Check egg laying conditions first
                if (not self.sleeping and not self.eating and 
                    not self.egg and self.mature and not self.has_laid_egg and
                    self.happiness >= 70 and 
                    self.energy >= 60 and    
                    self.hunger >= 60):      
                    
                    if self.env.is_in_area(self.x, self.y, "nursery"):
                        # Try to lay egg in adjacent spot
                        adjacent_spots = [
                            (self.x + dx, self.y + dy)
                            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                            if (self.env.is_valid_position(self.x + dx, self.y + dy) and
                                not self.env.is_position_occupied(self.x + dx, self.y + dy) and
                                self.env.is_in_area(self.x + dx, self.y + dy, "nursery"))
                        ]
                        
                        if adjacent_spots:
                            egg_x, egg_y = random.choice(adjacent_spots)
                            self.energy -= 50
                            new_egg = Egg(egg_x, egg_y)
                            self.env.eggs.append(new_egg)
                            self.env.grid[(egg_x, egg_y)] = new_egg
                            self.has_laid_egg = True
                            self.target = None
                    else:
                        # Move towards nursery if ready to lay egg
                        self.target = "nursery"
                        self.color = (255, 200, 200)
                        return  # Return here to prioritize egg laying

                # Prioritize eating over moving bodies
                if not self.sleeping and not self.eating:
                    nearby_entities = self.env.get_nearby_entities(self.x, self.y)
                    found_food = False
                    
                    # First check if we can eat something adjacent
                    if self.hunger < 70:
                        for entity in nearby_entities:
                            if isinstance(entity, Creature) and entity.dead and entity.food_value > 0:
                                dx = abs(self.x - entity.x)
                                dy = abs(self.y - entity.y)
                                if dx + dy == 1:  # Adjacent but not diagonal
                                    if self.eat(entity):
                                        self.color = (255, 200, 0)
                                        found_food = True
                                        self.target = None
                                        self.carrying_food = False
                                        break
                    
                    # If we didn't find adjacent food to eat, look for dead creatures to move
                    if not found_food and not self.carrying_food:
                        for entity in nearby_entities:
                            if (isinstance(entity, Creature) and 
                                entity.dead and 
                                entity.food_value > 0 and 
                                not self.env.is_in_area(entity.x, entity.y, "food") and
                                not any(c.target == entity for c in self.env.creatures if c != self and not c.dead)):
                                # Check if adjacent to the dead creature
                                if abs(self.x - entity.x) + abs(self.y - entity.y) == 1:
                                    self.target = entity
                                    self.carrying_food = True
                                    self.color = (200, 150, 50)  # Brown while carrying
                                    break

            # Update happiness and visual state at the end
            self.happiness = self.calculate_happiness()
            self.update_visual_state()

    def update_visual_state(self):
        """Update the creature's visual appearance based on its state"""
        if self.dead:
            self.color = (255, 0, 0)  # Red for dead
            return

        # Start with base color
        r, g, b = self.base_color

        # Health indicator - reduce green as health decreases
        health_factor = self.health / 100
        g = int(g * health_factor)

        # Energy indicator - add blue tint when tired
        if self.energy < self.rest_threshold + 20 and not self.sleeping:
            b = min(255, b + int((1 - self.energy / 100) * 255))

        # Hunger indicator - add red tint when hungry
        if self.hunger < 50:
            r = min(255, r + int((1 - self.hunger / 100) * 255))

        # Special states override the gradual changes
        if self.sleeping and self.env.is_in_area(self.x, self.y, "sleeping"):
            self.color = (100, 100, 255)  # Blue only when sleeping in sleep area
        elif self.eating:
            self.color = (255, 200, 0)    # Yellow while eating
        elif self.carrying_food:
            self.color = (200, 150, 50)   # Brown while carrying
        elif self.target == "nursery":
            self.color = (255, 200, 200)  # Pink while ready to lay egg
        else:
            self.color = (r, g, b)

    def lay_egg(self):
        """Lay an egg in the current position if in nursery"""
        if self.energy >= 90 and not self.egg:
            # Try to lay egg in current position
            if not self.env.is_position_occupied(self.x, self.y + 1):
                self.energy -= 90
                new_egg = Egg(self.x, self.y + 1)
                self.env.eggs.append(new_egg)
                self.env.grid[(self.x, self.y + 1)] = new_egg
                self.has_laid_egg = True
            elif not self.env.is_position_occupied(self.x + 1, self.y):
                self.energy -= 90
                new_egg = Egg(self.x + 1, self.y)
                self.env.eggs.append(new_egg)
                self.env.grid[(self.x + 1, self.y)] = new_egg
                self.has_laid_egg = True

    def die(self):
        """Mark the creature as dead instead of removing it."""
        self.dead = True
        self.color = (255, 0, 0)  # Red color for dead creatures
        self.health = 0
        self.food_value = 300  # Doubled from 100 to 200 - dead creatures provide more food
        
        # Determine cause of death
        if self.age >= self.max_age:
            self.death_cause = "Old Age"
        elif self.hunger <= 0:
            self.death_cause = "Starvation"
        else:
            self.death_cause = "Unknown"

    def __str__(self):
        if self.dead:
            return f"""DEAD CREATURE
Cause: {self.death_cause}
Remaining Food: {self.food_value}%
Position: ({self.x}, {self.y})"""
        else:
            status = []
            if self.sleeping:
                status.append("Sleeping")
            if self.eating:
                status.append("Eating")
            if self.has_laid_egg:
                status.append("Has unhatched egg")
            if self.age > self.max_age * 0.7:
                status.append("(!) Elderly")  # Changed from emoji to standard characters
            
            age_percent = (self.age / self.max_age) * 100
            
            return f"""Health: {self.health}%
Energy: {self.energy}%
Hunger: {self.hunger}%
Happiness: {round(self.happiness)}%
Age: {self.age} ({round(age_percent, 1)}% of lifespan)
Max Age: {self.max_age}
Mature: {'Yes' if self.mature else 'No'}
Status: {', '.join(status) if status else 'Active'}
Position: ({self.x}, {self.y})"""

    def eat(self, food_source):
        """Consume some food from a dead creature when adjacent to it"""
        if (not self.dead and food_source.dead and food_source.food_value > 0 and
            not self.sleeping and self.hunger < 100):
            # Check if we're adjacent to the food source
            dx = abs(self.x - food_source.x)
            dy = abs(self.y - food_source.y)
            if dx + dy == 1:  # Must be exactly one space away (no diagonals)
                self.eating = True
                food_amount = min(40, food_source.food_value)
                food_source.food_value -= food_amount
                self.hunger = min(100, self.hunger + food_amount * 1.5)
                self.color = (255, 200, 0)  # Yellow while eating
                return True
        return False

    def draw(self, batch):
        """Draw the creature with improved indicators"""
        shapes = []
        center_x = self.x * GRID_SIZE + GRID_SIZE // 2
        center_y = self.y * GRID_SIZE + GRID_SIZE // 2
        base_radius = GRID_SIZE // 2

        # 1. Selection indicator (white ring, outermost)
        if self.selected:
            shapes.append(pyglet.shapes.Circle(
                center_x, center_y,
                base_radius + SELECTION_RING_SIZE,
                color=(255, 255, 255, 180),
                batch=batch
            ))

        # 2. Critical status indicator (red ring)
        if not self.dead and (self.hunger < 30 or self.energy < 30 or self.health < 30):
            shapes.append(pyglet.shapes.Circle(
                center_x, center_y,
                base_radius + STATUS_RING_SIZE,
                color=(255, 0, 0, 200),
                batch=batch
            ))

        # 3. Main body
        if self.dead:
            # Base circle for dead creature
            shapes.append(pyglet.shapes.Circle(
                center_x, center_y,
                base_radius,
                color=(100, 0, 0),  # Dark red base
                batch=batch
            ))
            
            # Food value indicator (arc)
            if self.food_value > 0:
                food_percentage = self.food_value / 300
                shapes.append(pyglet.shapes.Arc(
                    center_x, center_y,
                    base_radius * 0.8,  # Slightly smaller than main body
                    color=(0, 255, 0),
                    batch=batch,
                    angle=food_percentage * 6.28319  # 2*pi for full circle
                ))
        else:
            # Living creature main body
            shapes.append(pyglet.shapes.Circle(
                center_x, center_y,
                base_radius,
                color=self.color,
                batch=batch
            ))

            # 4. Age indicator (inner circle)
            if self.mature:
                age_factor = self.age / self.max_age
                inner_radius = base_radius * INNER_CIRCLE_RATIO
                
                # Color transitions from green to yellow to red with age
                if age_factor < 0.5:
                    # Young adult: green to yellow
                    green = 255
                    red = int(255 * (age_factor * 2))
                else:
                    # Elder: yellow to red
                    red = 255
                    green = int(255 * (2 - age_factor * 2))
                    
                shapes.append(pyglet.shapes.Circle(
                    center_x, center_y,
                    inner_radius,
                    color=(red, green, 0, 230),
                    batch=batch
                ))

        return shapes

# The environment where creatures live
class Environment:
    def __init__(self, width, height):
        # Adjust width to account for sidebar
        self.width = (WIDTH - SIDEBAR_WIDTH) // GRID_SIZE  # Use adjusted width
        self.height = height
        # Pass self (environment) to creature constructor
        self.creatures = [
            Creature(random.randint(0, self.width-1), 
                    random.randint(0, self.height-1),
                    self)  # Pass self here
        ]
        
        self.eggs = []  # List to track eggs
        self.grid = {}  # Add a grid to track occupied positions
        # Add initial creatures to the grid
        for creature in self.creatures:
            self.grid[(creature.x, creature.y)] = creature
            
        self.creatures_to_remove = []  # Track creatures to remove after being eaten
        self.cell_size = GRID_SIZE * 2  # Size of each partition cell
        self.spatial_grid = {}  # Spatial partitioning grid
        self.sleeping_area_scale = 1.0
        self.food_area_scale = 1.0
        self.nursery_area_scale = 1.0
        
    def is_position_occupied(self, x, y):
        """Check if a position is occupied by any entity"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True  # Consider out-of-bounds as occupied
        return (x, y) in self.grid

    def get_adjacent_positions(self, x, y):
        """Get all valid adjacent positions."""
        positions = [
            (x, y+1),    # up
            (x, y-1),    # down
            (x-1, y),    # left
            (x+1, y),    # right
        ]
        # Filter out positions that are out of bounds or in the sidebar
        return [(x, y) for x, y in positions if 
                0 <= x < self.width and 
                0 <= y < self.height]

    def find_open_adjacent_spot(self, x, y):
        """Find an unoccupied adjacent position."""
        adjacent_positions = self.get_adjacent_positions(x, y)
        for pos_x, pos_y in adjacent_positions:
            if not self.is_position_occupied(pos_x, pos_y):
                return pos_x, pos_y
        return None

    def update(self, dt):
        """Update the environment, including moving creatures and handling interactions."""
        self.update_area_scales()
        
        # Clear and rebuild grid at the start of update
        self.grid.clear()
        for creature in self.creatures:
            self.grid[(creature.x, creature.y)] = creature
        for egg in self.eggs:
            self.grid[(egg.x, egg.y)] = egg
        
        # Update creatures
        for creature in self.creatures:
            if not creature.dead:
                old_x, old_y = creature.x, creature.y
                creature.update()  # This will now call move()
                
                # Update grid if position changed
                if (creature.x, creature.y) != (old_x, old_y):
                    self.grid.pop((old_x, old_y), None)
                    self.grid[(creature.x, creature.y)] = creature
            else:
                # Remove dead creatures with no food value
                if creature.food_value <= 0:
                    self.creatures_to_remove.append(creature)
        
        # Update eggs
        for egg in self.eggs[:]:  # Create a copy of the list to safely modify it
            egg.update()
            if egg.ready_to_hatch:
                # Create new creature at egg's position
                new_creature = Creature(egg.x, egg.y, self)
                self.creatures.append(new_creature)
                self.grid[(egg.x, egg.y)] = new_creature
                # Remove the hatched egg
                self.eggs.remove(egg)
                self.grid.pop((egg.x, egg.y), None)
        
        # Remove creatures marked for removal
        self.creatures = [c for c in self.creatures if c not in self.creatures_to_remove]
        self.creatures_to_remove.clear()

    def draw(self, screen):
        batch = pyglet.graphics.Batch()
        shapes = []
        
        # Draw colony areas first
        areas = [
            ("food", FOOD_STORAGE_RADIUS * self.food_area_scale, (100, 50, 50), "Food Zone"),
            ("nursery", NURSERY_RADIUS * self.nursery_area_scale, (50, 100, 50), "Nursery Zone"),
            ("sleeping", SLEEPING_RADIUS * self.sleeping_area_scale, (50, 50, 100), "Sleeping Zone")
        ]

        for area_type, radius, color, label in areas:
            center = self.get_area_center(area_type)
            
            # Explicitly unpack RGB values and set very low opacity
            r, g, b = color
            # Draw very transparent circle for the zone
            zone_circle = pyglet.shapes.Circle(
                center[0], center[1], radius,
                color=(r, g, b, 20),  # Even more transparent (alpha=20)
                batch=batch
            )
            shapes.append(zone_circle)
            
            # Draw subtle border for the zone
            border_circle = pyglet.shapes.Circle(
                center[0], center[1], radius + 2,
                color=(255, 255, 255, 30),
                batch=batch
            )
            shapes.append(border_circle)
            
            # Calculate label position, ensuring it stays within window bounds
            label_x = min(max(center[0], 100), WIDTH - SIDEBAR_WIDTH - 100)
            label_y = min(max(center[1] - radius - 25, 30), HEIGHT - 30)
            
            # Draw label with semi-transparent background
            label_width = len(label) * 8
            pyglet.shapes.Rectangle(
                label_x - label_width/2 - 5,
                label_y - 10,
                label_width + 10,
                20,
                color=(0, 0, 0, 100)
            ).draw()
            
            # Draw the text
            pyglet.text.Label(
                label,
                font_name='Arial',
                font_size=14,
                bold=True,
                x=label_x,
                y=label_y,
                anchor_x='center',
                anchor_y='center',
                color=(255, 255, 255, 200)
            ).draw()

        # Draw eggs
        for egg in self.eggs:
            if egg.selected:
                shapes.append(pyglet.shapes.Circle(
                    egg.x * GRID_SIZE + GRID_SIZE // 2,
                    egg.y * GRID_SIZE + GRID_SIZE // 2,
                    (GRID_SIZE // 3) + 2,
                    color=(255, 255, 255),
                    batch=batch
                ))
            
            shapes.append(pyglet.shapes.Circle(
                egg.x * GRID_SIZE + GRID_SIZE // 2,
                egg.y * GRID_SIZE + GRID_SIZE // 2,
                GRID_SIZE // 3,
                color=(255, 200, 0),
                batch=batch
            ))

        # Draw creatures using their new draw method
        for creature in self.creatures:
            shapes.extend(creature.draw(batch))

        # Draw everything in one call
        batch.draw()

    def is_position_blocked(self, x, y):
        """Check if a position is blocked by a living creature"""
        if (x, y) in self.grid:
            entity = self.grid[(x, y)]
            # Allow movement through dead creatures (to prevent gridlock)
            if isinstance(entity, Creature) and not entity.dead:
                return True
        return False

    def find_nearest_food(self, x, y):
        """Find the nearest dead creature with improved accessibility check"""
        food_sources = []
        
        for creature in self.creatures:
            if creature.dead and creature.food_value > 0:
                # Calculate base distance
                distance = abs(x - creature.x) + abs(y - creature.y)
                
                # Check if there's too many creatures already targeting this food
                nearby_creatures = sum(1 for c in self.creatures 
                                     if not c.dead and 
                                     abs(c.x - creature.x) + abs(c.y - creature.y) <= 1)
                
                # Add penalty to distance based on nearby creatures
                distance += nearby_creatures * 2
                
                food_sources.append((creature.x, creature.y, distance))
        
        if food_sources:
            # Sort by adjusted distance and add small random factor to prevent perfect alignment
            food_sources.sort(key=lambda x: x[2] + random.uniform(0, 0.5))
            return (food_sources[0][0], food_sources[0][1])
            
        return None

    def remove_dead_creature(self, creature):
        """Mark a dead creature for removal after being fully consumed"""
        if creature.food_value <= 0:
            self.creatures_to_remove.append(creature)

    def count_nearby_creatures(self, x, y):
        """Count number of creatures in adjacent cells"""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_x = x + dx
                check_y = y + dy
                if (check_x, check_y) in self.grid:
                    entity = self.grid[(check_x, check_y)]
                    if isinstance(entity, Creature) and not entity.dead:
                        count += 1
        return count

    def get_nearby_entities(self, x, y, radius=3):
        """Get entities in nearby cells"""
        nearby = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                check_x = x + dx
                check_y = y + dy
                if (check_x, check_y) in self.grid:
                    nearby.append(self.grid[(check_x, check_y)])
        return nearby

    def update_spatial_grid(self):
        """Update spatial partitioning grid"""
        self.spatial_grid.clear()
        for creature in self.creatures:
            cell = (creature.x // self.cell_size, creature.y // self.cell_size)
            if cell not in self.spatial_grid:
                self.spatial_grid[cell] = []
            self.spatial_grid[cell].append(creature)

    def get_area_center(self, area_type):
        """Get the center coordinates for different colony areas with fixed positions"""
        if area_type == "food":
            # Food storage in bottom-left quadrant
            return (NEST_CENTER_X - QUADRANT_OFFSET, NEST_CENTER_Y - QUADRANT_OFFSET)
        elif area_type == "nursery":
            # Nursery in top-right quadrant
            return (NEST_CENTER_X + QUADRANT_OFFSET, NEST_CENTER_Y + QUADRANT_OFFSET)
        elif area_type == "sleeping":
            # Sleeping area in bottom-right quadrant
            return (NEST_CENTER_X + QUADRANT_OFFSET, NEST_CENTER_Y - QUADRANT_OFFSET)
        return (NEST_CENTER_X, NEST_CENTER_Y)

    def is_in_area(self, x, y, area_type):
        """Check if position is within a specific colony area"""
        # Convert grid coordinates to pixel coordinates for center calculation
        px = x * GRID_SIZE + GRID_SIZE // 2
        py = y * GRID_SIZE + GRID_SIZE // 2
        
        center = self.get_area_center(area_type)
        distance = ((px - center[0])**2 + (py - center[1])**2)**0.5
        
        # Scale only affects the radius, not the center position
        if area_type == "food":
            return distance <= FOOD_STORAGE_RADIUS * self.food_area_scale
        elif area_type == "nursery":
            return distance <= NURSERY_RADIUS * self.nursery_area_scale
        elif area_type == "sleeping":
            return distance <= SLEEPING_RADIUS * self.sleeping_area_scale
        return False

    def find_nursery_spot(self):
        """Find an open spot in the nursery area"""
        center = self.get_area_center("nursery")
        center_x = int(center[0] / GRID_SIZE)
        center_y = int(center[1] / GRID_SIZE)
        
        for radius in range(1, int(NURSERY_RADIUS / GRID_SIZE)):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    x = center_x + dx
                    y = center_y + dy
                    if (self.is_in_area(x, y, "nursery") and 
                        not self.is_position_occupied(x, y)):
                        return x, y
        return None

    def move_entity(self, entity, new_x, new_y):
        """Safely move an entity to a new position"""
        if not self.is_valid_position(new_x, new_y):
            return False
        
        if (new_x, new_y) in self.grid:
            return False
        
        # Remove from old position
        self.grid.pop((entity.x, entity.y), None)
        
        # Update position
        entity.x = new_x
        entity.y = new_y
        
        # Add to new position
        self.grid[(new_x, new_y)] = entity
        return True

    def try_move_towards(self, entity, target_x, target_y):
        """Try to move entity towards target, handling collisions and obstacles"""
        if entity.dead:
            return False

        # Calculate movement towards target
        dx = target_x - entity.x
        dy = target_y - entity.y
        
        # If already at target, no need to move
        if dx == 0 and dy == 0:
            return True

        # Get all possible moves, ordered by priority
        possible_moves = []
        
        # Direct moves (primary direction)
        if abs(dx) > abs(dy):
            # Prioritize horizontal movement
            if dx != 0:
                possible_moves.append((dx // abs(dx), 0))  # Horizontal
                if dy != 0:
                    possible_moves.append((dx // abs(dx), dy // abs(dy)))  # Diagonal
                    possible_moves.append((0, dy // abs(dy)))  # Vertical
            else:
                possible_moves.append((0, dy // abs(dy)))  # Vertical
        else:
            # Prioritize vertical movement
            if dy != 0:
                possible_moves.append((0, dy // abs(dy)))  # Vertical
                if dx != 0:
                    possible_moves.append((dx // abs(dx), dy // abs(dy)))  # Diagonal
                    possible_moves.append((dx // abs(dx), 0))  # Horizontal
            else:
                possible_moves.append((dx // abs(dx), 0))  # Horizontal

        # Add alternative moves for obstacle avoidance
        if dx != 0:
            possible_moves.append((dx // abs(dx), 1))   # Side step up
            possible_moves.append((dx // abs(dx), -1))  # Side step down
        if dy != 0:
            possible_moves.append((1, dy // abs(dy)))   # Side step right
            possible_moves.append((-1, dy // abs(dy)))  # Side step left

        # Add perpendicular moves as last resort
        possible_moves.extend([
            (0, 1), (0, -1), (1, 0), (-1, 0),  # Cardinal directions
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonal directions
        ])

        # If carrying a dead creature, handle special movement
        if entity.carrying_food and isinstance(entity.target, Creature):
            dead_creature = entity.target
            
            # Check if we're adjacent to the dead creature
            if abs(entity.x - dead_creature.x) + abs(entity.y - dead_creature.y) > 1:
                # Lost contact with dead creature, drop it
                entity.carrying_food = False
                entity.target = None
                return False

            # Try each possible move
            for move_x, move_y in possible_moves:
                new_carrier_x = entity.x + move_x
                new_carrier_y = entity.y + move_y
                
                if not (self.is_valid_position(new_carrier_x, new_carrier_y) and
                       not self.is_position_occupied(new_carrier_x, new_carrier_y)):
                    continue
                
                # Find best position for dead creature
                best_dead_pos = None
                min_distance = float('inf')
                
                # Check all adjacent positions for the dead creature
                for dead_dx, dead_dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_dead_x = new_carrier_x + dead_dx
                    new_dead_y = new_carrier_y + dead_dy
                    
                    if (self.is_valid_position(new_dead_x, new_dead_y) and
                        not self.is_position_occupied(new_dead_x, new_dead_y)):
                        # Calculate distance to target considering both positions
                        dist = (abs(new_dead_x - target_x) + abs(new_dead_y - target_y) +
                               abs(new_carrier_x - target_x) + abs(new_carrier_y - target_y))
                        if dist < min_distance:
                            min_distance = dist
                            best_dead_pos = (new_dead_x, new_dead_y)
                
                # If we found valid positions for both, move them
                if best_dead_pos is not None:
                    # Remove both entities from their current positions
                    self.grid.pop((entity.x, entity.y), None)
                    self.grid.pop((dead_creature.x, dead_creature.y), None)
                    
                    # Update positions
                    entity.x = new_carrier_x
                    entity.y = new_carrier_y
                    dead_creature.x = best_dead_pos[0]
                    dead_creature.y = best_dead_pos[1]
                    
                    # Add both entities back to grid at their new positions
                    self.grid[(entity.x, entity.y)] = entity
                    self.grid[(dead_creature.x, dead_creature.y)] = dead_creature
                    
                    return True
            
            return False

        # Normal movement for non-carrying entities
        # Try each possible move in order of priority
        for move_x, move_y in possible_moves:
            new_x = entity.x + move_x
            new_y = entity.y + move_y
            
            if (self.is_valid_position(new_x, new_y) and
                not self.is_position_occupied(new_x, new_y)):
                return self.move_entity(entity, new_x, new_y)
        
        return False

    def try_move_dead_creature(self, dead_creature):
        """Remove this method or make it do nothing since dead creatures shouldn't move"""
        return False

    def is_valid_position(self, x, y):
        """Check if a position is within bounds and not behind the sidebar"""
        return 0 <= x < self.width - (SIDEBAR_WIDTH // GRID_SIZE) and 0 <= y < self.height

    def find_valid_egg_spot(self, x, y):
        """Find a valid spot for an egg near the given position"""
        # Check immediate adjacent spots first
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x = x + dx
            new_y = y + dy
            if (self.is_valid_position(new_x, new_y) and
                not self.is_position_occupied(new_x, new_y) and
                self.is_in_area(new_x, new_y, "nursery")):
                return new_x, new_y
            
        # If no immediate spots, check slightly further
        for d in range(2, 4):
            for dx in range(-d, d+1):
                for dy in range(-d, d+1):
                    if dx == 0 and dy == 0:
                        continue
                    new_x = x + dx
                    new_y = y + dy
                    if (self.is_valid_position(new_x, new_y) and
                        not self.is_position_occupied(new_x, new_y) and
                        self.is_in_area(new_x, new_y, "nursery")):
                        return new_x, new_y
        return None

    def update_area_scales(self):
        """Update the scales of the areas based on specific needs"""
        num_creatures = len(self.creatures)
        num_dead = sum(1 for c in self.creatures if c.dead)
        num_eggs = len(self.eggs)
        
        # Calculate scales based on different needs
        sleeping_need = num_creatures
        food_need = num_dead
        nursery_need = num_eggs
        
        # Calculate base scales (more conservative maximum to prevent touching)
        max_scale = 1.5  # Ensure zones do not touch
        
        # Base scale is 1.0, maximum scale prevents touching
        self.sleeping_area_scale = min(max_scale, 1.0 + (sleeping_need / max(1, num_creatures)) * 0.3)
        self.food_area_scale = min(max_scale, 1.0 + (food_need / max(1, num_creatures)) * 0.3)
        self.nursery_area_scale = min(max_scale, 1.0 + (nursery_need / max(1, num_creatures)) * 0.3)

# The egg class to handle egg incubation
class Egg:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 0
        self.selected = False
        self.ready_to_hatch = False  # New flag to indicate hatching

    def update(self):
        """Increment the egg's timer and check if ready to hatch."""
        if self.timer < 100:
            self.timer += 1
        if self.timer >= 100:
            self.ready_to_hatch = True

    def __str__(self):
        return f"Egg Timer: {min(self.timer, 100)}"

    def draw(self, batch):
        """Draw the egg with selection indicator if selected"""
        shapes = []

        # Add selection indicator (white border) if selected
        if self.selected:
            shapes.append(pyglet.shapes.Circle(
                self.x * GRID_SIZE + GRID_SIZE // 2,
                self.y * GRID_SIZE + GRID_SIZE // 2,
                (GRID_SIZE // 3) + 4,  # Make border larger than the egg
                color=(255, 255, 255, 128),  # Semi-transparent white
                batch=batch
            ))

        # Draw the egg
        shapes.append(pyglet.shapes.Circle(
            self.x * GRID_SIZE + GRID_SIZE // 2,
            self.y * GRID_SIZE + GRID_SIZE // 2,
            GRID_SIZE // 3,
            color=(255, 200, 0),
            batch=batch
        ))

        return shapes

# Handle mouse clicks
selected_creature = None  # No creature is selected initially
selected_egg = None  # No egg is selected initially

@window.event
def on_mouse_press(x, y, button, modifiers):
    global selected_creature, selected_egg, current_speed_state
    if x < WIDTH - SIDEBAR_WIDTH:  # Check if the click is within the grid area
        grid_x = x // GRID_SIZE
        grid_y = y // GRID_SIZE
        creature_found = False
        egg_found = False

        # First check if we clicked on a creature
        for creature in env.creatures:
            if creature.x == grid_x and creature.y == grid_y:
                creature_found = True
                # Only select if it's not already selected
                if selected_creature != creature:
                    # Deselect previous selections
                    if selected_creature:
                        selected_creature.selected = False
                    if selected_egg:
                        selected_egg.selected = False
                        selected_egg = None
                    # Select new creature
                    selected_creature = creature
                    selected_creature.selected = True
                break

        # Then check if we clicked on an egg
        if not creature_found:  # Only check eggs if we didn't click a creature
            for egg in env.eggs:
                if egg.x == grid_x and egg.y == grid_y:
                    egg_found = True
                    # Only select if it's not already selected
                    if selected_egg != egg:
                        # Deselect previous selections
                        if selected_creature:
                            selected_creature.selected = False
                            selected_creature = None
                        if selected_egg:
                            selected_egg.selected = False
                        # Select new egg
                        selected_egg = egg
                        selected_egg.selected = True
                    break

        # Deselect everything if clicking empty space
        if not creature_found and not egg_found:
            if selected_creature:
                selected_creature.selected = False
                selected_creature = None
            if selected_egg:
                selected_egg.selected = False
                selected_egg = None

        update_stats()

    else:
        # Calculate button dimensions (use original size * scale)
        button_width = 38  # Fixed width for hit detection
        button_height = 38  # Fixed height for hit detection
        
        # Pause button
        pause_area = {
            'x1': pause_button.x,
            'x2': pause_button.x + button_width,
            'y1': pause_button.y,
            'y2': pause_button.y + button_height
        }
        
        # Pause button
        if (pause_area['x1'] <= x <= pause_area['x2'] and 
            pause_area['y1'] <= y <= pause_area['y2']):
            if current_speed_state != "pause":
                current_speed_state = "pause"
                update_fps(0)  # Pause
                pause_button.image = pause_clicked_image
                play_button.image = play_unclicked_image
                fast_forward_button.image = fast_forward_unclicked_image
        
        # Play button
        elif (play_button.x <= x <= play_button.x + button_width and 
              play_button.y <= y <= play_button.y + button_height):
            if current_speed_state != "play":
                current_speed_state = "play"
                update_fps(1)  # Normal speed
                play_button.image = play_clicked_image
                pause_button.image = pause_unclicked_image
                fast_forward_button.image = fast_forward_unclicked_image
        
        # Fast forward button
        elif (fast_forward_button.x <= x <= fast_forward_button.x + button_width and 
              fast_forward_button.y <= y <= fast_forward_button.y + button_height):
            if current_speed_state != "fast":
                current_speed_state = "fast"
                update_fps(20)  # Fast speed
                fast_forward_button.image = fast_forward_clicked_image
                pause_button.image = pause_unclicked_image
                play_button.image = play_unclicked_image

def update_fps(new_fps):
    """Update the FPS and reschedule the update function"""
    global FPS
    FPS = new_fps
    pyglet.clock.unschedule(update)
    if FPS > 0:  # Only schedule if FPS is greater than 0
        pyglet.clock.schedule_interval(update, 1.0 / FPS)

def format_stats(creature):
    """Format creature stats in a more readable way"""
    if not creature:
        return "No creature selected"
    
    return str(creature)  # Use the creature's string representation

def update_stats():
    """Update the stats with formatted text"""
    if selected_creature:
        stats_label.text = format_stats(selected_creature)
    elif selected_egg:
        stats_label.text = f"Selected Egg:\nIncubation: {selected_egg.timer}%\nPosition: ({selected_egg.x}, {selected_egg.y})"
    else:
        stats_label.text = "No creature or egg selected"

# Create the environment with only one creature
env = Environment((WIDTH - SIDEBAR_WIDTH) // GRID_SIZE, HEIGHT // GRID_SIZE)

# Update the legend labels to include groups and headers
legend_labels = [
    # Group 1: Basic States
    ("Basic States", "header"),
    ("Normal Creature", (0, 255, 0)),
    ("Dead Creature (with food)", "dead_with_food"),
    ("Dead Creature (depleted)", (100, 0, 0)),
    ("Egg", (255, 200, 0)),
    
    # Group 2: Age Indicators
    ("Age Indicators", "header"),
    ("Young Adult (green core)", "young_adult"),
    ("Middle Age (yellow core)", "middle_age"),
    ("Elder (red core)", "elder"),
    
    # Group 3: Status Indicators
    ("Status Indicators", "header"),
    ("Selected (white ring)", "selected"),
    ("Critical Status (red ring)", "critical"),
    ("Sleeping", (100, 100, 255)),
    ("Carrying Food", (200, 150, 50)),
    ("Ready to Lay Egg", (255, 200, 200))
]

def update_ui_positions():
    """Update all UI element positions with refined spacing"""
    # Calculate positions from top-right
    start_y = HEIGHT - TOP_MARGIN
    
    # Update panel positions
    control_panel.update_position(
        WIDTH - SIDEBAR_WIDTH - TOP_MARGIN,
        start_y - CONTROL_PANEL_HEIGHT
    )
    
    stats_panel.update_position(
        WIDTH - SIDEBAR_WIDTH - TOP_MARGIN,
        start_y - CONTROL_PANEL_HEIGHT - PANEL_SPACING - STATS_PANEL_HEIGHT
    )
    
    legend_panel.update_position(
        WIDTH - SIDEBAR_WIDTH - TOP_MARGIN,
        start_y - CONTROL_PANEL_HEIGHT - PANEL_SPACING - 
        STATS_PANEL_HEIGHT - PANEL_SPACING - LEGEND_PANEL_HEIGHT
    )
    
    # Update buttons to be below the "Controls" label
    pause_button.x = WIDTH - SIDEBAR_WIDTH + 15
    pause_button.y = control_panel.y + control_panel.height - 75
    
    play_button.x = WIDTH - SIDEBAR_WIDTH + 75
    play_button.y = control_panel.y + control_panel.height - 75
    
    fast_forward_button.x = WIDTH - SIDEBAR_WIDTH + 135
    fast_forward_button.y = control_panel.y + control_panel.height - 75
    
    # Update stats label with more space from top of panel
    stats_label.x = WIDTH - SIDEBAR_WIDTH - TOP_MARGIN + 15
    stats_label.y = stats_panel.y + stats_panel.height - 40

@window.event
def on_draw():
    window.clear()
    
    # Draw panels background area
    pyglet.shapes.Rectangle(
        WIDTH - SIDEBAR_WIDTH - TOP_MARGIN, 0, 
        SIDEBAR_WIDTH + TOP_MARGIN, HEIGHT,
        color=(30, 30, 30)
    ).draw()
    
    # Draw panels
    control_panel.draw()
    stats_panel.draw()
    legend_panel.draw()
    
    # Draw legend with adjusted starting position
    legend_start_y = legend_panel.y + legend_panel.height - LEGEND_TOP_PADDING
    y_offset = legend_start_y
    
    for label_text, color in legend_labels:
        if color == "header":
            # Add extra space before headers (except the first one)
            if y_offset < legend_start_y:
                y_offset -= LEGEND_GROUP_SPACING
            
            pyglet.text.Label(
                label_text,
                font_name='Arial',
                font_size=LEGEND_HEADER_SIZE,
                bold=True,
                x=WIDTH - SIDEBAR_WIDTH - TOP_MARGIN + 15,
                y=y_offset,
                anchor_x='left',
                anchor_y='center',
                color=(200, 200, 200, 255)
            ).draw()
            y_offset -= LEGEND_HEADER_SPACING
            continue
            
        # Draw indicators with refined positioning
        x_pos = WIDTH - SIDEBAR_WIDTH - TOP_MARGIN + 20 + LEGEND_ICON_SIZE//2
        if color == "dead_with_food":
            # Dead creature with food indicator
            pyglet.shapes.Circle(x_pos, y_offset, 
                               LEGEND_ICON_SIZE//2, color=(100, 0, 0)).draw()
            # Draw green arc to show remaining food
            pyglet.shapes.Arc(x_pos, y_offset, 
                            LEGEND_ICON_SIZE//2 * 0.8,  # Slightly smaller radius
                            color=(0, 255, 0),
                            start_angle=0,  # Start from right
                            angle=4.71239,  # About 3/4 of a circle
                            batch=None).draw()
        elif color == "selected":
            # Selection indicator with creature inside
            pyglet.shapes.Circle(x_pos, y_offset, 
                               LEGEND_ICON_SIZE//2 + 4, color=(255, 255, 255, 180)).draw()
            pyglet.shapes.Circle(x_pos, y_offset, 
                               LEGEND_ICON_SIZE//2, color=(0, 255, 0)).draw()
            # Add inner circle to match actual creature appearance
            pyglet.shapes.Circle(x_pos, y_offset, 
                               LEGEND_ICON_SIZE//2 * INNER_CIRCLE_RATIO, 
                               color=(0, 255, 0, 230)).draw()
        elif color == "critical":
            # Critical status indicator with creature inside
            pyglet.shapes.Circle(x_pos, y_offset, 
                               LEGEND_ICON_SIZE//2 + 2, color=(255, 0, 0, 200)).draw()
            pyglet.shapes.Circle(x_pos, y_offset, 
                               LEGEND_ICON_SIZE//2, color=(0, 255, 0)).draw()
            # Add inner circle to match actual creature appearance
            pyglet.shapes.Circle(x_pos, y_offset, 
                               LEGEND_ICON_SIZE//2 * INNER_CIRCLE_RATIO, 
                               color=(0, 255, 0, 230)).draw()
        elif color in ["young_adult", "middle_age", "elder"]:
            # Age indicator examples with outer and inner circles
            pyglet.shapes.Circle(x_pos, y_offset, 
                               LEGEND_ICON_SIZE//2, color=(0, 255, 0)).draw()
            # Different inner colors based on age
            if color == "young_adult":
                inner_color = (0, 255, 0)
            elif color == "middle_age":
                inner_color = (255, 255, 0)
            else:  # elder
                inner_color = (255, 0, 0)
            pyglet.shapes.Circle(x_pos, y_offset, 
                               LEGEND_ICON_SIZE//2 * INNER_CIRCLE_RATIO, 
                               color=inner_color + (230,)).draw()  # Add alpha channel
        elif isinstance(color, tuple):
            # Regular color indicators (sleeping, carrying food, etc.)
            pyglet.shapes.Circle(x_pos, y_offset, 
                               LEGEND_ICON_SIZE//2, color=color).draw()
            # Add inner circle for consistency if it's a living creature color
            if color != (255, 200, 0):  # Not an egg
                pyglet.shapes.Circle(x_pos, y_offset, 
                                   LEGEND_ICON_SIZE//2 * INNER_CIRCLE_RATIO, 
                                   color=color + (230,)).draw()
        
        # Draw label with refined positioning
        label = pyglet.text.Label(
            label_text,
            font_name='Arial',
            font_size=LEGEND_TEXT_SIZE,
            x=WIDTH - SIDEBAR_WIDTH - TOP_MARGIN + 45,
            y=y_offset,
            width=SIDEBAR_WIDTH - 55,
            multiline=True,
            anchor_x='left',
            anchor_y='center'
        )
        label.draw()
        
        y_offset -= LEGEND_ITEM_SPACING
    
    env.draw(window)
    stats_label.draw()
    pause_button.draw()
    play_button.draw()
    fast_forward_button.draw()

# Initial UI position update
update_ui_positions()

# Update method (called on every frame)
def update(dt):
    env.update(dt)  # Update creatures and eggs
    update_stats()  # Update the stats each frame

# Make sure to schedule the initial update
if FPS > 0:
    pyglet.clock.schedule_interval(update, 1.0 / FPS)  # Add this line before pyglet.app.run()

# Run the pyglet application
pyglet.app.run()
