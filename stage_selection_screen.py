from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.lang import Builder
import os

Builder.load_file('kv/stage_selection.kv')

class LevelButton(Button):
    def __init__(self, level_file, level_number, locked=False, **kwargs):
        super().__init__(**kwargs)
        self.level_file = level_file
        self.level_number = level_number
        self.locked = locked
        self.size_hint_y = None
        self.height = dp(120)
        self.size_hint_x = 1
        
        # Set button appearance
        self.background_normal = ''
        
        if self.locked:
            self.background_color = (0.3, 0.3, 0.3, 1)
            self.text = f"Level {level_number}\n(Locked)"
            self.disabled = True
        else:
            difficulty = self._get_difficulty()
            self.text = f"Level {level_number}\n({difficulty})"
            
            # Color based on difficulty
            if difficulty == "Easy":
                self.background_color = (0.2, 0.6, 0.2, 1)
            elif difficulty == "Medium":
                self.background_color = (0.8, 0.8, 0.2, 1)
            else:  # Hard or any other
                self.background_color = (0.8, 0.2, 0.2, 1)
        
        self.font_size = dp(18)
        
    def _get_difficulty(self):
        # Try to extract difficulty from the level file
        try:
            import json
            with open(f"assets/levels/{self.level_file}", 'r') as f:
                level_data = json.load(f)
                if 'difficulty' in level_data:
                    return level_data['difficulty']
        except:
            pass
        
        return "Unknown"  # Default if difficulty can't be determined

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
            try:
                level_number = int(''.join(filter(str.isdigit, level_name)))
                
                # Create a custom button with more visual appeal
                button = LevelButton(
                    level_file=level_file,
                    level_number=level_number,
                    locked=level_number not in self.unlocked_levels
                )
                
                if not button.locked:
                    button.bind(on_press=lambda btn, lvl=level_file: self.start_game(lvl))
                
                level_buttons_layout.add_widget(button)
                
            except ValueError:
                print(f"Couldn't parse level number from {level_name}")

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
        print(f"Unlocked level {next_level}")

    def on_size(self, *args):
        # Recalculate layout when screen size changes
        if hasattr(self.ids, 'level_buttons'):
            # Adjust columns based on screen width
            self.ids.level_buttons.cols = max(1, min(3, int(self.width / dp(300))))