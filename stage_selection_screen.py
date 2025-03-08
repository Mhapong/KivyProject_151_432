from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.lang import Builder
import os

Builder.load_file('kv/stage_selection.kv')

class StageSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.unlocked_levels = {1}  # Set of unlocked level numbers
        self.load_levels()

    def load_levels(self):
        level_buttons_layout = self.ids.level_buttons
        level_buttons_layout.clear_widgets()  # Clear existing buttons
        
        # Get all level files and sort them
        level_files = sorted([f for f in os.listdir("assets/levels/") if f.endswith(".json")])
        
        for level_file in level_files:
            level_name = level_file.replace(".json", "")
            level_number = int(''.join(filter(str.isdigit, level_name)))
            
            button = Button(
                text=f"Play {level_name.capitalize()}",
                size_hint_y=None,
                height=50,
                background_normal='',
                background_color=(0.4, 0.4, 0.4, 1) if level_number in self.unlocked_levels else (0.2, 0.2, 0.2, 1)
            )
            
            # Disable button if level is locked
            if level_number not in self.unlocked_levels:
                button.disabled = True
                button.text += " (Locked)"
            
            button.bind(on_press=lambda btn, lvl=level_file: self.start_game(lvl))
            level_buttons_layout.add_widget(button)

    def start_game(self, level_file):
        game_screen = self.manager.get_screen('game')
        game_screen.level_file = f"assets/levels/{level_file}"
        game_screen.setup_level()
        self.manager.current = 'game'
        
    def go_back(self):
        self.manager.current = 'home'

    def unlock_next_level(self, current_level):
        next_level = current_level + 1
        self.unlocked_levels.add(next_level)
        self.load_levels()  # Refresh buttons to update locked/unlocked status