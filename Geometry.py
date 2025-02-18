from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen

class Player(Image):
    velocity = NumericProperty(0)
    gravity = -0.5
    jump_strength = 10
    on_ground = BooleanProperty(True)
    
    def jump(self):
        if self.on_ground:
            self.velocity = self.jump_strength
            self.on_ground = False

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        
        if self.y <= 0:
            self.y = 0
            self.velocity = 0
            self.on_ground = True

class GameScreen(Screen):  # เปลี่ยนจาก RelativeLayout เป็น Screen
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player(source='cube_85.png', size_hint=(None, None), size=(50, 50), pos=(100, 100))
        self.add_widget(self.player)
        Clock.schedule_interval(self.update, 1/60)
        Window.bind(on_key_down=self.on_key_down)
    
    def on_key_down(self, instance, key, *args):
        if key == 32:  # Spacebar
            self.player.jump()
    
    def update(self, dt):
        self.player.update()

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Label Title
        title = Label(
            text="Geometry at home",
            font_size="40sp",
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(400, 100),
            pos_hint={"center_x": 0.5, "top": 1}
        )
        self.add_widget(title)
        
        # Play Button
        play_button = Button(
            text="Play",
            font_size="24sp",
            size_hint=(None, None),
            size=(200, 60),
            background_color=(0.2, 0.6, 1, 1),  # ฟ้าสด
            color=(1, 1, 1, 1)  # ขาว
        )
        play_button.bind(on_press=self.start_game)
        play_button.pos_hint = {"center_x": 0.5, "center_y": 0.4}
        self.add_widget(play_button)
    
    def start_game(self, instance):
        self.manager.current = "game"

class GeometryDashApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(GameScreen(name="game"))  # เปลี่ยนเป็น Screen
        return sm

if __name__ == '__main__':
    GeometryDashApp().run()
