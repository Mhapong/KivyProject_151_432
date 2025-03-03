from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, BooleanProperty
from kivy.factory import Factory

# 🔹 โหลดไฟล์ game.kv
Builder.load_file('game.kv')

class Player(Image):
    velocity = NumericProperty(0)
    x_velocity = NumericProperty(2)  # ✅ ความเร็วแนวราบ (ค่า 2 หมายถึงไปข้างหน้า)
    gravity = -0.5
    jump_strength = 15  
    on_ground = BooleanProperty(True)

    def jump(self):
        if self.on_ground:
            self.velocity = self.jump_strength
            self.on_ground = False

    def update(self, platforms, obstacles):
        self.velocity += self.gravity
        self.y += self.velocity
        self.x += self.x_velocity  # ✅ เคลื่อนที่ไปข้างหน้า

        # ตรวจสอบการชนกับ platform
        for platform in platforms:
            if self.collide_widget(platform) and self.velocity <= 0:
                self.y = platform.y + platform.height
                self.velocity = 0
                self.on_ground = True
                break
        else:
            self.on_ground = False

        # ตรวจสอบการชนกับ obstacle (Game Over)
        for obstacle in obstacles:
            if self.collide_widget(obstacle):
                print("Game Over!")  
                App.get_running_app().stop()
                break

        # ป้องกันตัวละครตกจากขอบล่าง
        if self.y <= 0:
            self.y = 0
            self.velocity = 0
            self.on_ground = True


class Platform(Image):
    pass

class Obstacle(Image):
    pass

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = self.ids.player
        self.platforms = [self.ids.platform1, self.ids.platform2]
        self.obstacles = [self.ids.obstacle1, self.ids.obstacle2]

        Clock.schedule_interval(self.update, 1/60)
        Window.bind(on_key_down=self.on_key_down)

    def on_key_down(self, instance, key, *args):
        if key == 32:  # Spacebar
            self.player.jump()
    
    def update(self, dt):
        self.player.update(self.platforms, self.obstacles)

class GeometryDashApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(GameScreen(name="game"))
        return sm

if __name__ == '__main__':
    GeometryDashApp().run()
