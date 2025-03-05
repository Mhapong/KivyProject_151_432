import random
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
        self.spawn_spike()

    def on_leave(self):
        Clock.unschedule(self.update)
        Window.unbind(on_key_down=self.on_key_down)

    def update(self, dt):
        self.ids.player.update([self.ids.ground1, self.ids.ground2], [self.ids.spike])

    def on_key_down(self, window, key, *args):
        if key == 32:  # 32 is the keycode for the spacebar
            self.ids.player.jump()

    def spawn_spike(self, dt=None):
        # Randomly decide whether to spawn a spike based on the level
        if random.random() < 0.1:  # Adjust the probability based on the level
            self.ids.spike.x = Window.width
        Clock.schedule_once(self.spawn_spike, random.uniform(1, 3))  # Adjust the spawn rate based on the level

    def game_over(self):
        print("Game Over!")
        self.manager.current = 'stage_selection'

class Player(Image):
    velocity = NumericProperty(0)
    x_velocity = NumericProperty(4)  # Increase horizontal speed
    gravity = -0.5
    jump_strength = 12  # Reduce jump height
    on_ground = BooleanProperty(True)
    rotation = NumericProperty(0)  # Add rotation property

    def jump(self):
        if self.on_ground:
            self.velocity = self.jump_strength
            self.on_ground = False

    def update(self, platforms, obstacles):
        self.velocity += self.gravity
        self.y += self.velocity

        # Continuously rotate while in the air
        if not self.on_ground:
            self.rotation += 2  # Adjust the rotation speed to be slower

        # Move platforms to create the illusion of movement
        for platform in platforms:
            platform.x -= self.x_velocity

            # Reset platform position to create infinite map illusion
            if platform.right <= 0:
                platform.x = platform.width

        # Move obstacles to create the illusion of movement
        for obstacle in obstacles:
            obstacle.x -= self.x_velocity

            # Reset obstacle position if it moves off-screen
            if obstacle.right <= 0:
                obstacle.x = Window.width

        # ตรวจสอบการชนกับ platform
        for platform in platforms:
            if self.collide_widget(platform) and self.velocity <= 0:
                self.y = platform.y + platform.height
                self.velocity = 0
                self.on_ground = True
                self.rotation = 0  # Reset rotation when on ground
                break
        else:
            self.on_ground = False

        # ตรวจสอบการชนกับ obstacle
        for obstacle in obstacles:
            if self.collide_widget(obstacle):
                # Handle collision with spike (e.g., end game, reduce health, etc.)
                App.get_running_app().root.get_screen('game').game_over()

class Platform(Image):
    pass

class Spike(Widget):
    pass

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StageSelectionScreen(name='stage_selection'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    MyApp().run()
