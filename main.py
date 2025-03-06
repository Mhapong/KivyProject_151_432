from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from home import HomePage
from stage_selection import StageSelectionScreen
from game_screen import GameScreen

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomePage(name='home'))
        sm.add_widget(StageSelectionScreen(name='stage_selection'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    MyApp().run()
