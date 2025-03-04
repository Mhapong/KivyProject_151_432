from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, BooleanProperty
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window

# Load the KV files
Builder.load_file('stage_selection.kv')
Builder.load_file('game.kv')

class StageSelectionScreen(Screen):
    pass

class GameScreen(Screen):
    def set_background(self, background_image):
        self.ids.background.source = background_image

    def on_enter(self):
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        Window.bind(on_key_down=self.on_key_down)

    def on_leave(self):
        Clock.unschedule(self.update)
        Window.unbind(on_key_down=self.on_key_down)

    def update(self, dt):
        self.ids.player.update([self.ids.ground], [])

    def on_key_down(self, window, key, *args):
        if key == 32:  # 32 is the keycode for the spacebar
            self.ids.player.jump()

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

        # Move platforms to create the illusion of movement
        for platform in platforms:
            platform.x -= self.x_velocity

            # Reset platform position to create infinite map illusion
            if platform.right < 0:
                platform.x = Window.width

        # ตรวจสอบการชนกับ platform
        for platform in platforms:
            if self.collide_widget(platform) and self.velocity <= 0:
                self.y = platform.y + platform.height
                self.velocity = 0
                self.on_ground = True
                break
        else:
            self.on_ground = False

class Platform(Image):
    pass

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StageSelectionScreen(name='stage_selection'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    MyApp().run()