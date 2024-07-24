#Run the code in Pycharm
import pygame
import random
import math
import matplotlib.pyplot as plt

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Light-Seeking Organism")

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Define organism properties
organism_size = 15
organism_speed = 2
organism_energy = 100  # New attribute for energy

# Function to generate color based on intensity
def color_from_intensity(intensity):
    base_color = min(intensity * 2, 255)
    return (base_color, base_color, 0)  # Yellow shade

# Define specific light sources with known intensities
light_sources = [
    {'position': (100, 150), 'intensity': 40},
    {'position': (400, 300), 'intensity': 70},
    {'position': (700, 450), 'intensity': 50}
]

# Update the light sources with their colors
for light in light_sources:
    light['color'] = color_from_intensity(light['intensity'])

# Initialize a single organism
organism = pygame.Rect(random.randint(0, width), random.randint(0, height), organism_size, organism_size)

# Energy decay and gain constants
energy_decay = 1
energy_gain = 0.5

# Initialize weights with a bias towards intensity
weights = {tuple(light['position']): light['intensity'] for light in light_sources}

# Data collection lists
energy_levels = []
distances_to_lights = {tuple(light['position']): [] for light in light_sources}
visits_to_lights = {tuple(light['position']): 0 for light in light_sources}
energy_gain_from_lights = {tuple(light['position']): 0 for light in light_sources}
movement_paths = []
light_selections = {tuple(light['position']): 0 for light in light_sources}

# Learning rate
learning_rate = 0.1
# Before the main loop
weight_history = {tuple(light['position']): [] for light in light_sources}

# Main simulation loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    movement_paths.append((organism.centerx, organism.centery))
    energy_levels.append(organism_energy)

    if organism_energy > 0:
        # Calculate the weighted distance for each light
        weighted_distances = {
            tuple(light['position']): ((organism.centerx - light['position'][0]) ** 2 + (organism.centery - light['position'][1]) ** 2) / weights[tuple(light['position'])]
            for light in light_sources
        }
        # Select the light with the smallest weighted distance
        closest_light = min(light_sources, key=lambda light: weighted_distances[tuple(light['position'])])
        dx = closest_light['position'][0] - organism.centerx
        dy = closest_light['position'][1] - organism.centery
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            organism_energy -= energy_decay
            organism.centerx += (dx / distance) * organism_speed
            organism.centery += (dy / distance) * organism_speed
            if distance < closest_light['intensity']:
                organism_energy += closest_light['intensity'] * energy_gain
                # Increase the weight for the light source that was successfully reached
                weights[tuple(closest_light['position'])] += learning_rate * closest_light['intensity']
                light_selections[tuple(closest_light['position'])] += 1
                for light_pos in weights:
                    weight_history[light_pos].append(weights[light_pos])


    if organism_energy <= 0:
        organism_energy = 0
        organism_speed = 0

    screen.fill((0, 0, 0))
    for light in light_sources:
        pygame.draw.circle(screen, light['color'], light['position'], light['intensity'])

    energy_color = max(0, min(255, int(organism_energy * 2.55)))
    organism_color = (255 - energy_color, energy_color, 0)
    pygame.draw.ellipse(screen, organism_color, organism)

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()

# Plotting the data after simulation
plt.figure()
plt.plot(energy_levels, label='Energy Over Time')
plt.xlabel('Time Steps')
plt.ylabel('Energy')
plt.title('Energy Levels Over Time')
plt.legend()
plt.show()

plt.figure()
for light_pos, distances in distances_to_lights.items():
    plt.plot(distances, label=f'Distance to light at {light_pos}')
plt.xlabel('Time Steps')
plt.ylabel('Distance')
plt.title('Distance to Light Sources Over Time')
plt.legend()
plt.show()

plt.figure()
x, y = zip(*movement_paths)
plt.plot(x, y, marker='o', label='Movement Path')
for light in light_sources:
    plt.scatter(light['position'][0], light['position'][1], color='yellow', s=100)  # Mark light positions
plt.title('Movement Path of the Organism')
plt.xlabel('X Position')
plt.ylabel('Y Position')
plt.legend()
plt.show()

# Plot histogram of light selections
light_positions_labels = [f"({light['position'][0]}, {light['position'][1]})" for light in light_sources]
selection_counts = [light_selections[tuple(light['position'])] for light in light_sources]
plt.figure(figsize=(10, 6))
plt.bar(range(len(light_positions_labels)), selection_counts, tick_label=light_positions_labels)
plt.xlabel('Light Source Position')
plt.ylabel('Selection Count')
plt.title('Organism Light Source Selections')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Plot the weight history for each light source
for light_pos, weights in weight_history.items():
    plt.plot(weights, label=f'Weight of light at {light_pos}')
plt.xlabel('Time Steps')
plt.ylabel('Weights')
plt.title('Weights of Light Sources Over Time')
plt.legend()
plt.show()

