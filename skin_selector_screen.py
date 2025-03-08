from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.app import App

class SkinSelectorScreen(Screen):
    selected_skin = StringProperty("default_skin.png")  # Default skin preview

    def select_skin(self, skin):
        self.selected_skin = skin  # Update the preview
        app = App.get_running_app()
        app.player_skin = skin

        game_screen = self.manager.get_screen('game')
        game_screen.player_skin = skin

        print(f"Selected skin: {self.selected_skin}")
