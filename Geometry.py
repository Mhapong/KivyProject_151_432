from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.relativelayout import RelativeLayout

class Player(Image):
    velocity = NumericProperty(0)
    gravity = -0.5
    jump_strength = 10
    on_ground = BooleanProperty(True)
    
    def jump(self):
        if self.on_ground:
            self.velocity = self.jump_strength
            self.on_ground = False

    def update(self, platforms, obstacles):
        self.velocity += self.gravity
        self.y += self.velocity
        
        for platform in platforms:
            if self.collide_widget(platform) and self.velocity <= 0:
                self.y = platform.y + platform.height
                self.velocity = 0
                self.on_ground = True
                break
        else:
            self.on_ground = False
        
        for obstacle in obstacles:
            if self.collide_widget(obstacle):
                print("Game Over!")
                App.get_running_app().stop()
                break
        
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
        self.player = Player(source='cube_85.png', size_hint=(None, None), size=(50, 50), pos=(100, 100))
        self.add_widget(self.player)

        self.platforms = [
            Platform(source='platform.png', size_hint=(None, None), size=(200, 20), pos=(50, 50)),
            Platform(source='platform.png', size_hint=(None, None), size=(200, 20), pos=(300, 150)),
        ]
        for platform in self.platforms:
            self.add_widget(platform)

        self.obstacles = [
            Obstacle(source='spike.png', size_hint=(None, None), size=(50, 50), pos=(200, 70)),
            Obstacle(source='spike.png', size_hint=(None, None), size=(50, 50), pos=(400, 170)),
        ]
        for obstacle in self.obstacles:
            self.add_widget(obstacle)

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
