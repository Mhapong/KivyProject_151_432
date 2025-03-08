from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from home_screen import HomePage
from stage_selection_screen import StageSelectionScreen
from game_screen import GameScreen
from skin_selector_screen import SkinSelectorScreen
from kivy.lang import Builder

# Load the KV files
Builder.load_file('kv/home.kv')
Builder.load_file('kv/stage_selection.kv')
Builder.load_file('kv/game.kv')
Builder.load_file('kv/skin_selector.kv')

class MyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player_skin = "assets/image/cube_5.png"  # Default skin
        
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomePage(name='home'))
        sm.add_widget(StageSelectionScreen(name='stage_selection'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(SkinSelectorScreen(name='skin_selector'))
        return sm

if __name__ == '__main__':
    MyApp().run()