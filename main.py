from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.properties import NumericProperty, BooleanProperty
from kivy.lang import Builder

# Load the KV files
Builder.load_file('stage_selection.kv')
Builder.load_file('game.kv')

class StageSelectionScreen(Screen):
    pass

class GameScreen(Screen):
    pass

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

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StageSelectionScreen(name='stage_selection'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    MyApp().run()