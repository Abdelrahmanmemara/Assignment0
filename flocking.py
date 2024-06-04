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
    cohesion_weight: float = 0.5
    separation_weight: float = 0.5

    # These should be left as is.
    delta_time: float = 0.5                                   # To learn more https://gafferongames.com/post/integration_basics/ 
    mass: int = 20                                            

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)


class Bird(Agent):
    config: FlockingConfig

    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()
        #YOUR CODE HERE -----------
        # Retrieving the weights 
        a,c,s = self.config.weights()
        # Calculating the Allignment 
        self.allignment = self.pos - self.average_velocity()
        # Calculating the Seperation
        self.separation = self.average_distance()
        # Calculating the Cohesion
        self.cohesion = self.find_cohesion_force() - self.pos
        # Calculating the Ftotal
        self.ftotal = (a*self.allignment) + (c*self.cohesion) + (s*self.separation)


    def average_velocity(self):
        agents_velocity = list(self.in_proximity_accuracy())
        agents_total_velocity = sum(agent.move for agent, _ in agents_velocity)
        return agents_total_velocity/ len(agents_velocity)
    
    def average_distance(self):
        agents = list(self.in_proximity_accuracy())
        agents_distance = sum(dist for agent, dist in agents)
        return agents_distance/ len(agents)
    
    def find_cohesion_force(self):
        agents = list(self.in_proximity_accuracy())
        average_position = sum(agent.pos for agent, _ in agents) / len(agents)
        cohesion_force = average_position - self.pos
        return cohesion_force


    def get_allignment_weight(self)->float:
        return self.config.allignment_weight
    
    def get_cohesion_weight(self)->float:
        return self.config.cohesion_weight
    
    def get_separation_weight(self)->float:
        return self.config.separation_weight

        #END CODE -----------------


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
