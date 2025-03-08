from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color, Triangle
from kivy.core.window import Window
from kivy.properties import NumericProperty, BooleanProperty
from kivy.animation import Animation

class Player(Image):
    velocity = NumericProperty(0)
    jump_strength = 12
    on_ground = BooleanProperty(True)
    rotation = NumericProperty(0)
    moving_speed = NumericProperty(200)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gravity = -1200
        self.jump_speed = 700
        self.moving_speed = 500
        self.world_x = 0
        self.is_jumping = False

    def update(self, dt, obstacles=None, platforms=None, finish_line=None):
        self.y += self.velocity
        self.velocity -= 0.5

        if self.is_jumping:
            self.rotation += 360 * dt  # เพิ่มการหมุนตัวละคร

        for obstacle in obstacles:
            if self.collide_widget(obstacle):
                if isinstance(obstacle, BoostPad):
                    self.velocity = self.jump_strength * 1.5
                    self.on_ground = False
                    self.is_jumping = True
                else:
                    return True

        if platforms:
            for platform in platforms:
                if self.collide_widget(platform):
                    if self.velocity < 0:  # ถ้ากำลังตกลงมา
                        self.y = platform.top
                        self.velocity = 0
                        self.on_ground = True
                        self.is_jumping = False
                        self.rotation = 0

        if finish_line and self.collide_widget(finish_line):
            return True

        if self.y < 100:
            self.y = 100
            self.velocity = 0
            self.on_ground = True
            self.is_jumping = False
            self.rotation = 0

        return False

    def jump(self):
        if self.on_ground:
            self.velocity = self.jump_strength
            self.on_ground = False
            self.is_jumping = True  # เริ่มการหมุนตัวละคร

    def die(self):
        anim = Animation(opacity=0, duration=0.5) + Animation(opacity=1, duration=0.5)
        anim.repeat = True
        anim.start(self)

    def reset_position(self):
        self.pos = (100, 100)
        self.velocity = 0

    def stop(self):
        self.velocity = 0

    def on_death(self):
        self.stop()
        anim = Animation(opacity=0, duration=1) + Animation(opacity=1, duration=1)
        anim.start(self)

class Spike(Widget):
    def __init__(self, pos, **kwargs):
        super().__init__(**kwargs)
        self.size = (30, 30)
        self.pos = pos
        with self.canvas:
            Color(1, 0, 0)  # Red color
            self.triangle = Triangle(points=[self.x, self.y, self.x + self.width / 2, self.y + self.height, self.x + self.width, self.y])
        self.bind(pos=self._update_shape, size=self._update_shape)

    def _update_shape(self, *args):
        self.triangle.points = [self.x, self.y, self.x + self.width / 2, self.y + self.height, self.x + self.width, self.y]

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

class FinishLine(Widget):
    def __init__(self, pos, **kwargs):
        super().__init__(**kwargs)
        self.size = (50, Window.height)
        self.pos = pos
        with self.canvas:
            Color(0, 1, 0)  # Green color
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def check_collision(self, player):
        if self.collide_widget(player):
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