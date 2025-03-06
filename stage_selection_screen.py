from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.lang import Builder
import os

Builder.load_file('kv/stage_selection.kv')

class StageSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_levels()

    def load_levels(self):
        level_files = sorted(os.listdir("assets/levels/"))
        level_buttons_layout = self.ids.level_buttons
        for level_file in level_files:
            if level_file.endswith(".json"):
                level_name = level_file.replace(".json", "")
                button = Button(
                    text=f"Play {level_name.capitalize()}",
                    size_hint=(1, None),
                    height=50
                )
                button.bind(on_press=lambda btn, lvl=level_file: self.start_game(lvl))
                level_buttons_layout.add_widget(button)

    def start_game(self, level_file):
        game_screen = self.manager.get_screen('game')
        game_screen.level_file = f"assets/levels/{level_file}"
        game_screen.setup_level()
        self.manager.current = 'game'
        
    def go_back(self):
        self.manager.current = 'home'