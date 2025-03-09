from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from home_screen import HomePage
from stage_selection_screen import StageSelectionScreen
from game_screen import GameScreen
from skin_selector_screen import SkinSelectorScreen
from kivy.lang import Builder
from kivy.core.window import Window  # Add this import

# Load the KV files
Builder.load_file('kv/home.kv')
Builder.load_file('kv/stage_selection.kv')
Builder.load_file('kv/game.kv')
Builder.load_file('kv/skin_selector.kv')

class MyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set up global keyboard handler
        Window.bind(on_key_down=self.on_key_down)
        
    def on_key_down(self, window, key, *largs):
        # Print key code for debugging
        print(f"Global key handler: {key}")
        
        # Handle space key (32) at the application level
        if key == 32:  # Space key
            # If we're in the game screen, delegate to its handler
            if hasattr(self, 'root') and self.root.current == 'game':
                game_screen = self.root.get_screen('game')
                if hasattr(game_screen, 'player') and game_screen.player:
                    game_screen.player.jump()
                    return True  # Indicate that we've handled this key
        return False  # Let other handlers process this key
        
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomePage(name='home'))
        sm.add_widget(StageSelectionScreen(name='stage_selection'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(SkinSelectorScreen(name='skin_selector'))
        return sm

if __name__ == '__main__':
    MyApp().run()