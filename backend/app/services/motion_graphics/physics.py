"""
Physics simulation module for the OMNIVID Motion Graphics Engine.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from dataclasses import dataclass


@dataclass
class Particle:
    """Particle in a physics simulation"""
    position: np.ndarray  # [x, y, z]
    velocity: np.ndarray  # [vx, vy, vz]
    mass: float = 1.0
    radius: float = 0.05
    color: Optional[Tuple[float, float, float]] = None
    life: float = 1.0  # 0.0 to 1.0
    
    def update(self, dt: float, gravity: np.ndarray, damping: float = 0.99):
        """Update particle state"""
        # Apply gravity
        self.velocity += gravity * dt
        
        # Update position
        self.position += self.velocity * dt
        
        # Apply damping
        self.velocity *= damping
        
        # Decrease life
        self.life -= dt * 0.1
        
        # Bounce off ground (z=0)
        if self.position[2] < 0:
            self.position[2] = 0
            self.velocity[2] *= -0.8  # Bounce with some energy loss
            
        # Bounce off walls (x=±10, y=±10)
        for i in range(2):  # x and y axes
            if abs(self.position[i]) > 10:
                self.position[i] = 10 * np.sign(self.position[i])
                self.velocity[i] *= -0.8


class PhysicsSimulator:
    """Physics-based animation simulator"""
    
    def __init__(self, gravity: Tuple[float, float, float] = (0, -9.8, 0)):
        self.gravity = np.array(gravity, dtype=np.float32)
        self.particles: List[Particle] = []
        self.time = 0.0
    
    def create_particle_burst(self, 
                            position: Tuple[float, float, float], 
                            count: int = 100,
                            speed: float = 5.0,
                            color: Optional[Tuple[float, float, float]] = None):
        """Create an explosion of particles"""
        for _ in range(count):
            # Random direction
            theta = np.random.uniform(0, 2 * np.pi)
            phi = np.random.uniform(0, np.pi)
            
            # Convert to cartesian
            vx = speed * np.sin(phi) * np.cos(theta)
            vy = speed * np.sin(phi) * np.sin(theta)
            vz = speed * np.cos(phi)
            
            # Add some randomness
            vx += np.random.uniform(-1, 1)
            vy += np.random.uniform(-1, 1)
            vz += np.random.uniform(0, 2)
            
            self.particles.append(Particle(
                position=np.array(position, dtype=np.float32),
                velocity=np.array([vx, vy, vz], dtype=np.float32),
                mass=np.random.uniform(0.5, 1.5),
                radius=np.random.uniform(0.02, 0.1),
                color=color,
                life=1.0
            ))
    
    def update(self, dt: float):
        """Update physics simulation"""
        self.time += dt
        
        # Update all particles
        for particle in self.particles[:]:
            particle.update(dt, self.gravity)
            
            # Remove dead particles
            if particle.life <= 0:
                self.particles.remove(particle)
        
        # Simple collision detection (naive O(n²) for demo)
        for i, p1 in enumerate(self.particles):
            for p2 in self.particles[i+1:]:
                self._handle_collision(p1, p2)
    
    def _handle_collision(self, p1: Particle, p2: Particle):
        """Handle collision between two particles"""
        dist = np.linalg.norm(p1.position - p2.position)
        min_dist = p1.radius + p2.radius
        
        if dist < min_dist and dist > 0:
            # Calculate collision normal
            normal = (p2.position - p1.position) / dist
            
            # Calculate relative velocity
            rel_velocity = p2.velocity - p1.velocity
            
            # Calculate impulse
            impulse = np.dot(rel_velocity, normal) * normal * 2 * p1.mass * p2.mass / (p1.mass + p2.mass)
            
            # Apply impulse
            p1.velocity += impulse / p1.mass * 0.5
            p2.velocity -= impulse / p2.mass * 0.5
            
            # Separate particles to avoid sticking
            overlap = min_dist - dist
            p1.position -= normal * overlap * 0.5
            p2.position += normal * overlap * 0.5
    
    def get_particle_data(self) -> List[Dict[str, Any]]:
        """Get particle data for rendering"""
        return [{
            'position': p.position.tolist(),
            'radius': p.radius,
            'color': p.color or [1.0, 1.0, 1.0],
            'opacity': p.life
        } for p in self.particles]
