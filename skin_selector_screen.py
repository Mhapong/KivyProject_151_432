from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.app import App

class SkinSelectorScreen(Screen):
    selected_skin = StringProperty("assets/image/cube_5.png")  # Default skin

    def select_skin(self, skin):
        self.selected_skin = skin
        # Store the skin in the app for global access
        app = App.get_running_app()
        app.player_skin = skin
        
        # Update game screen's player_skin property
        game_screen = self.manager.get_screen('game')
        game_screen.player_skin = skin
        
        print(f"Selected skin: {self.selected_skin}")