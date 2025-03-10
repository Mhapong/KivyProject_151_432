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
        # Geometry Dash-like physics constants
        self.gravity = -2800        # Increased gravity for snappier falls
        self.jump_strength = 880    # Higher jump strength for proper jump height
        self.velocity = 0
        self.moving_speed = 500     # Constant move speed
        self.world_x = 0
        self.is_jumping = False
        self.on_ground = True
        self.rotation = 0
        self.opacity = 1
        self.original_source = kwargs.get('source', '')
        self.source = self.original_source
        self.jump_time = 0          # Track time since last jump
        self.total_jump_time = 0.55 # Approximate time for a full jump

    def update(self, dt, obstacles=None, platforms=None, finish_line=None):
        # Store previous position for collision resolution
        old_x = self.x
        old_y = self.y
        
        # Apply gravity - more aggressive for snappier falls like GD
        self.velocity += self.gravity * dt
        
        # Track jump time for rotation calculation
        if not self.on_ground:
            self.jump_time += dt
        
        # Terminal velocity - geometry dash has a fairly hard cap
        if (self.velocity < -1200):
            self.velocity = -1200
        
        # Update position
        self.y += self.velocity * dt
        
        # Platform collision handling
        if platforms:
            for platform in platforms:
                # Basic collision detection with wider tolerance on sides
                x_overlap = (self.x + self.width * 0.8 > platform.x and 
                             self.x + self.width * 0.2 < platform.x + platform.width)
                
                y_above_platform = old_y >= platform.top - 5
                y_intersect_platform = self.y < platform.top + 10
                
                # Top collision - only activate when falling
                if x_overlap and y_above_platform and y_intersect_platform and self.velocity < 0:
                    self.y = platform.top  # Place player on top of platform
                    self.velocity = 0
                    self.on_ground = True
                    self.is_jumping = False
                    self.jump_time = 0
                    
                    # Snap to nearest 90 degrees when landing - Geometry Dash style
                    target_angle = round(self.rotation / 90) * 90
                    self.rotation = target_angle
                
                # Side collision - make player die when hitting platform side
                elif (not y_above_platform and 
                      self.y + self.height * 0.3 > platform.y and 
                      self.y < platform.y + platform.height * 0.7):
                    
                    # Skip side collision at game start
                    if platform.x < 400 and self.world_x < 200:
                        pass
                    else:
                        # Check if player is trying to move into a platform from the side
                        if (self.x + self.width > platform.x and 
                            self.x + self.width < platform.x + 20):  # Left side collision
                            return True  # Hit platform from side = death
                        
                        elif (self.x < platform.x + platform.width and 
                              self.x > platform.x + platform.width - 20):  # Right side collision
                            return True  # Hit platform from side = death
        
        # Geometry Dash style rotation - smooth 360 degree rotate during jump
        if not self.on_ground:
            # Calculate rotation based on jump progress
            jump_progress = min(1.0, self.jump_time / self.total_jump_time)
            
            # Rotate based on jump curve - non-linear to match the arc
            # First half of jump is slower rotation, second half is faster
            if jump_progress <= 0.5:
                # Slower rotation during ascent (0-180 degrees)
                self.rotation = jump_progress * 180 * 2
            else:
                # Faster rotation during descent (180-360 degrees)
                self.rotation = 180 + (jump_progress - 0.5) * 180 * 2
            
            # Keep rotation between 0-360
            while self.rotation >= 360:
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
                    # Boost effect with GD physics
                    self.velocity = self.jump_strength * 1.5
                    self.on_ground = False
                    self.is_jumping = True
                    self.jump_time = 0  # Reset jump time for proper rotation

        # Check finish line
        if finish_line and isinstance(finish_line, FinishLine) and finish_line.check_collision(self):
            return "finish"

        return False

    def jump(self):
        print(f"Jump called. On ground: {self.on_ground}")
        
        # Only jump if on the ground
        if self.on_ground:
            print("Jumping!")
            self.velocity = self.jump_strength
            self.on_ground = False
            self.is_jumping = True
            self.jump_time = 0  # Reset jump timer
            self.opacity = 1
            self.source = self.original_source
        else:
            print("Cannot jump - not on ground")

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
        self.initial_x = pos[0]  # Store initial x position
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

class RotatingSpike(Widget):
    def __init__(self, pos, angle=180, **kwargs):
        super().__init__(**kwargs)
        self.size = (30, 30)  # Same size as regular spike
        self.pos = pos
        self.angle = angle  # Default to 180 degrees (upside down)
        self.initial_x = pos[0]  # Store initial x position
        # Calculate triangle points based on angle
        self.triangle_points = self._calculate_triangle_points()
        
        with self.canvas:
            Color(1, 0.5, 0)  # Orange color to distinguish from regular spikes
            self.triangle = Triangle(points=self.triangle_points)
        self.bind(pos=self._update_shape, size=self._update_shape)

    def _calculate_triangle_points(self):
        # Create a triangle with the specified rotation
        if self.angle == 180:  # Upside down spike
            return [
                self.x + self.width * 0.5, self.y,                # Bottom point
                self.x + self.width * 0.1, self.y + self.height,  # Top left
                self.x + self.width * 0.9, self.y + self.height   # Top right
            ]
        elif self.angle == 90:  # Pointing right
            return [
                self.x + self.width, self.y + self.height * 0.5,  # Right point
                self.x, self.y + self.height * 0.1,               # Bottom left
                self.x, self.y + self.height * 0.9                # Top left
            ]
        elif self.angle == 270:  # Pointing left
            return [
                self.x, self.y + self.height * 0.5,               # Left point
                self.x + self.width, self.y + self.height * 0.1,  # Bottom right
                self.x + self.width, self.y + self.height * 0.9   # Top right
            ]
        else:  # Default - pointing up (0 degrees)
            return [
                self.x + self.width * 0.5, self.y + self.height,  # Top point
                self.x + self.width * 0.1, self.y,                # Bottom left
                self.x + self.width * 0.9, self.y                 # Bottom right
            ]

    def _update_shape(self, *args):
        self.triangle_points = self._calculate_triangle_points()
        self.triangle.points = self.triangle_points

    def collide_with_player(self, player):
        # Same collision detection as regular spike
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
        x1, y1 = self.triangle_points[0], self.triangle_points[1]
        x2, y2 = self.triangle_points[2], self.triangle_points[3]
        x3, y3 = self.triangle_points[4], self.triangle_points[5]
        
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
        self.initial_x = pos[0]  # Store initial x position
        with self.canvas:
            Color(1, 1, 0)  # Yellow color
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect)

    def _update_rect(self, *args):
        # This will fail without resetting the canvas
        # Need to redraw all elements when position changes
        self.canvas.clear()
        with self.canvas:
            # Redraw everything
            Color(1, 1, 0)  # Yellow color
            self.rect = Rectangle(pos=self.pos, size=self.size)

from kivy.core.window import Window

class FinishLine(Widget):
    def __init__(self, pos, **kwargs):
        super().__init__(**kwargs)
        self.size = (100, Window.height)  # Wider and full height
        self.pos = pos
        
        # Create with more visible appearance
        self.redraw_canvas()
        self.bind(pos=self._update_rect)
    
    def redraw_canvas(self):
        with self.canvas:
            # More visible colors
            Color(0, 1, 0, 0.9)  # Very bright green with high opacity
            Rectangle(pos=self.pos, size=self.size)
            
            # Larger checkered pattern for better visibility
            Color(1, 1, 1, 1.0)  # Pure white
            checker_size = 50  # Larger checkers
            rows = int(Window.height / checker_size)
            cols = int(self.size[0] / checker_size)
            
            for row in range(rows):
                for col in range(cols):
                    if (row + col) % 2 == 0:
                        Rectangle(
                            pos=(self.pos[0] + col * checker_size, 
                                 self.pos[1] + row * checker_size),
                            size=(checker_size, checker_size)
                        )
            
            # Bolder border
            Color(0, 0, 0, 1)
            Line(rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1]), width=6)

    def _update_rect(self, *args):
        # Clear and redraw when position changes
        self.canvas.clear()
        self.redraw_canvas()

    def check_collision(self, player):
        # More lenient collision detection specifically for level 3
        if player.x > self.x - 50 and player.x < self.x + self.width + 50:
            print("FINISH LINE COLLISION DETECTED!")
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

class SpeedPortal(Widget):
    def __init__(self, pos, speed_multiplier=1.5, **kwargs):
        super().__init__(**kwargs)
        self.size = (40, 60)
        self.pos = pos
        self.speed_multiplier = speed_multiplier
        self.initial_x = pos[0]
        
        # Color based on speed
        if speed_multiplier < 1.0:
            portal_color = (0, 0, 1)  # Blue for slower
        elif speed_multiplier < 2.0:
            portal_color = (1, 1, 0)  # Yellow for medium
        else:
            portal_color = (1, 0, 0)  # Red for faster
        
        with self.canvas:
            Color(*portal_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            # Add some details to make it look like a portal
            Color(1, 1, 1, 0.5)  # White with transparency
            Line(ellipse=(self.x + 5, self.y + 5, self.width - 10, self.height - 10), width=2)
            
        self.bind(pos=self._update_rect)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos