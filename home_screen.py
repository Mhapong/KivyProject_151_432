from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

# Load the KV file
Builder.load_file('kv/home.kv')

class HomePage(Screen):

    def go_to_skin_selector(self, instance):
        self.manager.current = 'skin_selector'

    def go_to_level_selection(self, instance):
        self.manager.current = 'stage_selection'

    def go_to_settings(self, instance):
        print("Settings button pressed")
