from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from home_screen import HomePage
from stage_selection_screen import StageSelectionScreen
from game_screen import GameScreen
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.properties import NumericProperty
from kivy.animation import Animation

# Load the KV files
Builder.load_file('kv/home.kv')
Builder.load_file('kv/stage_selection.kv')

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomePage(name='home'))
        sm.add_widget(StageSelectionScreen(name='stage_selection'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    MyApp().run()
