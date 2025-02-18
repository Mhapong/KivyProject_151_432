from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, BooleanProperty

# 🏆 Level Data (Background images for each level)
level_data = {
    1: {"bg_image": "map_1.jpg"},
    2: {"bg_image": "map_1.jpg"},
    3: {"bg_image": "map_3.jpg"},
}

# 🎮 Player Class
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

# 🎯 Game Screen (Changes Background per Level)
class GameScreen(Screen):
    def __init__(self, level=1, **kwargs):
        super().__init__(**kwargs)
        self.level = level

        # Background
        self.bg = Image(source=level_data[self.level]["bg_image"], allow_stretch=True, keep_ratio=False)
        self.bg.size = Window.size  # Stretch background to fit window size
        self.add_widget(self.bg)

        # Player (Upscaled size)
        self.player = Player(source="cube_85.png", size_hint=(None, None), size=(100, 100), pos=(200, 200))
        self.add_widget(self.player)

        # Back to Level Select Button (Now Visible and Larger)
        self.back_button = Button(
            text="Back",
            size_hint=(None, None),
            size=(200, 80),  # Increased size
            pos_hint={"right": 0.98, "top": 0.98},
            background_color=(1, 0, 0, 1)
        )
        self.back_button.bind(on_press=self.go_back)
        self.add_widget(self.back_button)

        # Update Game
        Clock.schedule_interval(self.update, 1/60)
        Window.bind(on_key_down=self.on_key_down)

    def on_key_down(self, instance, key, *args):
        if key == 32:  # Spacebar
            self.player.jump()
    
    def update(self, dt):
        self.player.update()

    def go_back(self, instance):
        self.manager.current = "level_select"

# 🏁 Level Selection Screen (Larger Buttons)
class LevelSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        title = Label(
            text="Select Level",
            font_size="60sp",  # Larger font size
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(600, 150),
            pos_hint={"center_x": 0.5, "top": 1}
        )
        self.add_widget(title)

        # Buttons for Level Selection (Larger)
        for i in range(1, 4):  
            btn = Button(text=f"Level {i}", size_hint=(None, None), size=(300, 120))  # Larger buttons
            btn.pos_hint = {"center_x": 0.5, "center_y": 0.6 - (i * 0.2)}
            btn.bind(on_press=lambda instance, lvl=i: self.start_game(lvl))
            self.add_widget(btn)

        # Back to Menu Button (Larger)
        back_button = Button(
            text="Back",
            size_hint=(None, None),
            size=(200, 80),
            pos_hint={"right": 0.98, "top": 0.98}
        )
        back_button.bind(on_press=self.go_to_menu)
        self.add_widget(back_button)

    def start_game(self, level):
        game_screen = GameScreen(name=f"game{level}", level=level)
        self.manager.add_widget(game_screen)
        self.manager.current = f"game{level}"

    def go_to_menu(self, instance):
        self.manager.current = "menu"

# 🏠 Main Menu Screen (Larger Font and Buttons)
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        title = Label(
            text="Geometry Dash Clone",
            font_size="60sp",  # Larger font size
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(600, 150),
            pos_hint={"center_x": 0.5, "top": 1}
        )
        self.add_widget(title)

        # Play Button (Larger)
        play_button = Button(
            text="Play",
            font_size="36sp",  # Larger font size
            size_hint=(None, None),
            size=(300, 120),
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1)
        )
        play_button.pos_hint = {"center_x": 0.5, "center_y": 0.4}
        play_button.bind(on_press=self.go_to_level_select)
        self.add_widget(play_button)

    def go_to_level_select(self, instance):
        self.manager.current = "level_select"

# 🚀 Main App
class GeometryDashApp(App):
    def build(self):
        Window.size = (1200, 800)  # Upscaled window size
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(LevelSelectScreen(name="level_select"))
        return sm

if __name__ == '__main__':
    GeometryDashApp().run()
