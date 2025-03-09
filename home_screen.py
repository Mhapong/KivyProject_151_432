from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App

# Load the KV file
Builder.load_file('kv/home.kv')

class HomePage(Screen):

    def go_to_skin_selector(self, instance):
        self.manager.current = 'skin_selector'

    def go_to_level_selection(self, instance):
        self.manager.current = 'stage_selection'

    def go_to_settings(self, instance):
        print("Settings button pressed")

    def unlock_all_levels(self, instance):
        # Get reference to the stage selection screen
        stage_screen = self.manager.get_screen('stage_selection')
        
        # Find all level files and unlock them
        import os
        level_files = [f for f in os.listdir("assets/levels/") if f.endswith(".json")]
        
        # Extract level numbers and unlock all
        for level_file in level_files:
            level_name = level_file.replace(".json", "")
            level_number = int(''.join(filter(str.isdigit, level_name)))
            stage_screen.unlocked_levels.add(level_number)
        
        # Reload the level buttons with new unlock status
        stage_screen.load_levels()
        
        # Show confirmation message
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        popup = Popup(
            title='Levels Unlocked',
            content=Label(text='All levels have been unlocked!'),
            size_hint=(0.6, 0.3)
        )
        popup.open()