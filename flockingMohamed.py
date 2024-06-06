from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize


@deserialize
@dataclass
class FlockingConfig(Config):
    # You can change these for different starting weights
    alignment_weight: float = 0.5
    cohesion_weight: float = 0.1
    separation_weight: float = 0.5
    initial_velocity = Vector2(0,0)
    max_velocity = Vector2(1,1)
    # These should be left as is.
    delta_time: float = 0.5                                   # To learn more https://gafferongames.com/post/integration_basics/ 
    mass: int = 20                                            

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)


class Bird(Agent):
    config: FlockingConfig
    
    def change_position(self):
        # Retrieving the weights 
        a, c, s = self.config.weights()
        mass = self.config.mass
        
        # Lists to store temporary data for calculations
        agents = list(self.in_proximity_accuracy())
        agents_total_velocity = Vector2(0, 0)
        separation_vector = Vector2(0, 0)
        average_position = Vector2(0, 0)
        
        # Check if there are any agents nearby
        if len(agents) > 0:
            for agent, dist in agents:
                # For Alignment
                agents_total_velocity += agent.move
                # For Separation (accumulate the difference in positions, considering inverse distance)
                separation_vector += (self.pos - agent.pos) / dist
                # For Cohesion
                average_position += agent.pos

            # Compute average values
            average_velocity = agents_total_velocity / len(agents)
            average_position /= len(agents)
            cohesion_force = average_position - self.pos
            
            # Calculate final steering forces
            alignment = (average_velocity - self.move)
            separation = separation_vector / len(agents)
            cohesion = cohesion_force
            
        else:
            alignment = Vector2(0, 0)
            separation = Vector2(0, 0)
            cohesion = Vector2(0, 0)

        # Total force
        ftotal = (a * alignment + c * cohesion + s * separation) / mass
        
        # Update the move
        self.move += ftotal

        # Clamp velocity to max_velocity
        if self.move.length() > self.config.max_velocity.length():
            self.move.scale_to_length(self.config.max_velocity.length())
        
        # Update the position
        self.pos += self.move * self.config.delta_time

        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()

class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class FlockingLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: FlockingConfig

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            self.config.alignment_weight += by
        elif self.selection == Selection.COHESION:
            self.config.cohesion_weight += by
        elif self.selection == Selection.SEPARATION:
            self.config.separation_weight += by

    def before_update(self):
        super().before_update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=0.1)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-0.1)
                elif event.key == pg.K_1:
                    self.selection = Selection.ALIGNMENT
                elif event.key == pg.K_2:
                    self.selection = Selection.COHESION
                elif event.key == pg.K_3:
                    self.selection = Selection.SEPARATION

        a, c, s = self.config.weights()
        print(f"A: {a:.1f} - C: {c:.1f} - S: {s:.1f}")


(
    FlockingLive(
        FlockingConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
        )
    )
    .batch_spawn_agents(50, Bird, images=["images/bird.png"])
    .run()
)
