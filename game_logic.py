from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color, Triangle, Line
from kivy.core.window import Window
from kivy.properties import NumericProperty, BooleanProperty
from kivy.animation import Animation
import random

class Player(Image):
    velocity = NumericProperty(0)
    jump_strength = NumericProperty(700)
    on_ground = BooleanProperty(True)
    rotation = NumericProperty(0)
    moving_speed = NumericProperty(500)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gravity = -1500
        self.jump_strength = 800
        self.velocity = 0
        self.moving_speed = 500
        self.world_x = 0
        self.is_jumping = False
        self.on_ground = True
        self.rotation = 0
        self.jump_height = 0  # Track jump height for rotation calculation
        self.max_jump_height = 0  # Track maximum jump height
        self.opacity = 1
        self.original_source = kwargs.get('source', '')
        self.source = self.original_source

    def update(self, dt, obstacles=None, platforms=None, finish_line=None):
        # Update vertical position with physics
        self.velocity += self.gravity * dt
        
        # Terminal velocity to prevent falling too fast
        if self.velocity < -1000:
            self.velocity = -1000
            
        self.y += self.velocity * dt

        # Geometry Dash style rotation - always rotate clockwise during jumps
        if not self.on_ground:
            # Determine rotation speed based on jump arc
            # Higher speed at beginning and end of jump, slower at peak
            jump_height_factor = abs(self.velocity) / self.jump_strength
            base_rotation_speed = 360  # Degrees per second
            rotation_speed = base_rotation_speed * (0.5 + jump_height_factor)
            
            # Apply rotation
            self.rotation += rotation_speed * dt
            
            # Keep rotation between 0-360
            if self.rotation >= 360:
                self.rotation -= 360
        
        # Death condition
        if self.y < 0:
            return True

        # Check obstacle collisions
        if obstacles:
            for obstacle in obstacles:
                if isinstance(obstacle, Spike):
                    if obstacle.collide_with_player(self):
                        return True
                elif isinstance(obstacle, BoostPad) and self.collide_widget(obstacle):
                    # Boost effect - higher jump
                    self.velocity = self.jump_strength * 1.5
                    self.on_ground = False
                    self.is_jumping = True

        # Platform collision
        if platforms:
            on_platform = False
            for platform in platforms:
                if self.collide_widget(platform) and self.velocity < 0:  # Only check when falling
                    self.y = platform.top
                    self.velocity = 0
                    self.on_ground = True
                    self.is_jumping = False
                    
                    # Snap to nearest 90 degrees when landing
                    target_angle = round(self.rotation / 90) * 90
                    self.rotation = target_angle
                    on_platform = True
                    break

        # Check finish line
        if finish_line and isinstance(finish_line, FinishLine) and self.collide_widget(finish_line):
            return "finish"

        return False

    def jump(self):
        if self.on_ground:
            self.velocity = self.jump_strength
            self.on_ground = False
            self.is_jumping = True
            
            # Don't reset rotation to 0, continue from current angle
            # This makes multiple jumps look smoother
            
            self.opacity = 1
            self.source = self.original_source

    def die(self):
        anim = Animation(opacity=0, duration=0.5) + Animation(opacity=1, duration=0.5)
        anim.repeat = True
        anim.start(self)

    def reset_position(self):
        self.pos = self.orig_pos
        self.velocity = 0
        self.on_ground = True
        self.is_jumping = False
        self.rotation = 0
        self.is_rotating = False

    def stop(self):
        self.velocity = 0

    def on_death(self):
        # Create explosion effect
        for _ in range(10):
            particle = {'x': self.center_x, 
                       'y': self.center_y,
                       'dx': random.uniform(-5, 5),
                       'dy': random.uniform(2, 8),
                       'life': 1.0}
            self.explosion_particles.append(particle)
        
        # Trigger death animation
        self.opacity = 0
        self.rotation = 0

    def update_particles(self, dt):
        # Update explosion particles
        for particle in self.explosion_particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['dy'] -= 0.2  # Gravity
            particle['life'] -= dt
            
            if particle['life'] <= 0:
                self.explosion_particles.remove(particle)

class Spike(Widget):
    def __init__(self, pos, **kwargs):
        super().__init__(**kwargs)
        self.size = (30, 30)  # Keep original size
        self.pos = pos
        # Calculate triangle points
        self.triangle_points = self._calculate_triangle_points()
        
        with self.canvas:
            Color(1, 0, 0)  # Red color
            self.triangle = Triangle(points=self.triangle_points)
        self.bind(pos=self._update_shape, size=self._update_shape)

    def _calculate_triangle_points(self):
        # Create an isosceles triangle
        return [
            self.x + self.width * 0.5, self.y + self.height,  # Top point
            self.x + self.width * 0.1, self.y,                # Bottom left
            self.x + self.width * 0.9, self.y                 # Bottom right
        ]

    def _update_shape(self, *args):
        self.triangle_points = self._calculate_triangle_points()
        self.triangle.points = self.triangle_points

    def collide_with_player(self, player):
        # Get player hitbox (slightly smaller than visual size)
        px = player.x + player.width * 0.2  # 20% inset from left
        py = player.y + player.height * 0.2  # 20% inset from bottom
        pw = player.width * 0.6  # 60% of original width
        ph = player.height * 0.6  # 60% of original height
        
        # Check if any corner of the player hitbox is inside the triangle
        player_points = [
            (px, py),                # Bottom left
            (px + pw, py),          # Bottom right
            (px, py + ph),          # Top left
            (px + pw, py + ph)      # Top right
        ]
        
        # Check center point too
        player_points.append((px + pw/2, py + ph/2))
        
        for point in player_points:
            if self._point_in_triangle(point[0], point[1]):
                return True
        return False
    
    def _point_in_triangle(self, x, y):
        # Get triangle points
        x1, y1 = self.triangle_points[0], self.triangle_points[1]  # Top
        x2, y2 = self.triangle_points[2], self.triangle_points[3]  # Bottom left
        x3, y3 = self.triangle_points[4], self.triangle_points[5]  # Bottom right
        
        # Calculate barycentric coordinates
        def sign(x1, y1, x2, y2, x3, y3):
            return (x1 - x3) * (y2 - y3) - (x2 - x3) * (y1 - y3)
            
        d1 = sign(x, y, x1, y1, x2, y2)
        d2 = sign(x, y, x2, y2, x3, y3)
        d3 = sign(x, y, x3, y3, x1, y1)

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (has_neg and has_pos)

class BoostPad(Widget):
    def __init__(self, pos, **kwargs):
        super().__init__(**kwargs)
        self.size = (40, 20)
        self.pos = pos
        with self.canvas:
            Color(1, 1, 0)  # Yellow color
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos

from kivy.core.window import Window

class FinishLine(Widget):
    def __init__(self, pos, **kwargs):
        super().__init__(**kwargs)
        self.size = (50, Window.height)
        self.pos = pos
        with self.canvas:
            # More vibrant color
            Color(0, 1, 0.5, 0.7)  # Brighter green with higher opacity
            self.rect = Rectangle(pos=self.pos, size=self.size)
            
            # Add checkered pattern for better visibility
            Color(1, 1, 1, 0.9)  # White checkers
            checker_size = 25
            for y in range(0, int(Window.height), checker_size*2):
                for i in range(int(Window.height/checker_size/2)):
                    Rectangle(pos=(self.pos[0], y + i*checker_size*2), 
                            size=(checker_size, checker_size))
                    Rectangle(pos=(self.pos[0] + checker_size, y + checker_size + i*checker_size*2),
                            size=(checker_size, checker_size))
            
            # Bold border
            Color(0, 0, 0, 1)  # Black border
            Line(rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1]), width=3)
        
        self.bind(pos=self._update_rect, size=self._update_rect)
        
    def _update_rect(self, *args):
        # This will fail without resetting the canvas
        # Need to redraw all elements when position changes
        self.canvas.clear()
        with self.canvas:
            Color(0, 1, 0.5, 0.7)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            
            Color(1, 1, 1, 0.9)
            checker_size = 25
            for y in range(0, int(Window.height), checker_size*2):
                for i in range(int(Window.height/checker_size/2)):
                    Rectangle(pos=(self.pos[0], y + i*checker_size*2), 
                            size=(checker_size, checker_size))
                    Rectangle(pos=(self.pos[0] + checker_size, y + checker_size + i*checker_size*2),
                            size=(checker_size, checker_size))
            
            Color(0, 0, 0, 1)
            Line(rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1]), width=3)

    def check_collision(self, player):
        # Improved collision detection with overlap threshold
        collision_margin = 10  # pixels of overlap required
        if (player.right > self.x + collision_margin and 
            player.x < self.right - collision_margin):
            return True
        return False

class Floor(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (Window.width * 3, 100)  # พื้นยาว 3 เท่าของความกว้างจอ
        self.pos = (0, 0)

        with self.canvas:
            Color(0.3, 0.3, 0.3)  # สีเทาเข้ม
            self.rect = Rectangle(pos=self.pos, size=self.size)

class Platform(Widget):
    def __init__(self, pos, size, **kwargs):
        super().__init__(**kwargs)
        self.pos = pos
        self.size = size
        with self.canvas:
            Color(0.5, 0.5, 0.5)  # Grey color
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos