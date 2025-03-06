from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivy.properties import NumericProperty, BooleanProperty
from kivy.animation import Animation

class Player(Image):
    rotation = NumericProperty(0)
    velocity_y = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gravity = -700
        self.jump_speed = 700
        self.moving_speed = 500
        self.world_x = 0
        self.is_jumping = False
        
    def update(self, dt, obstacles=None):
        # อัพเดทการเคลื่อนที่
        self.velocity_y += self.gravity * dt
        self.y += self.velocity_y * dt
        
        if self.is_jumping:
            self.rotation += 360 * dt
        
        # เช็คการชนพื้น
        if self.y < 100:
            self.y = 100
            self.velocity_y = 0
            self.is_jumping = False
            self.rotation = 0
            
        # เช็คการชนกับสิ่งกีดขวาง
        if obstacles:
            for obstacle in obstacles:
                if self.collide_widget(obstacle):
                    if isinstance(obstacle, BoostPad):
                        self.velocity_y = self.jump_speed * 1.5  # เพิ่มความเร็วในการกระโดด
                        self.is_jumping = True
                    else:
                        return True
        return False
            
    def jump(self):
        if not self.is_jumping:
            self.velocity_y = self.jump_speed
            self.is_jumping = True

    def die(self):
        # เพิ่มเอฟเฟกต์การตาย
        anim = Animation(opacity=0, duration=0.5) + Animation(opacity=1, duration=0.5)
        anim.repeat = True
        anim.start(self)

class Spike(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (30, 30)
        with self.canvas:
            Color(0.7, 0.7, 0.7)  # Light gray color
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect)
        
    def _update_rect(self, *args):
        self.rect.pos = self.pos

class BoostPad(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (40, 20)
        with self.canvas:
            Color(1, 1, 0)  # Yellow color
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect)
        
    def _update_rect(self, *args):
        self.rect.pos = self.pos

class FinishLine(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (50, Window.height)
        with self.canvas:
            Color(0, 1, 0)  # Green color
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect)
        
    def _update_rect(self, *args):
        self.rect.pos = self.pos

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
