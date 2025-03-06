from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class HomePage(Screen):
    def __init__(self, **kwargs):
        super(HomePage, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=20, padding=50)


    def go_to_level_selection(self, instance):
        self.manager.current = 'stage_selection'
