from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Line
import os

class SkinButton(Button):
    def __init__(self, skin_path, **kwargs):
        super().__init__(**kwargs)
        self.skin_path = skin_path
        self.size_hint = (None, None)
        self.size = (dp(150), dp(150))
        
        # Use the skin image as the button background
        self.background_normal = skin_path
        self.background_down = skin_path  # Same image when pressed
        
        # Adjust border to none so it's just the image
        self.border = (0, 0, 0, 0)
        
        # Track selection state
        self.selected = False
        
    def on_press(self):
        # Provide visual feedback with a subtle scale animation
        anim = Animation(size=(dp(145), dp(145)), duration=0.1)
        anim.start(self)
        
    def on_release(self):
        # Return to normal size
        anim = Animation(size=(dp(150), dp(150)), duration=0.2)
        anim.start(self)

class SkinSelectorScreen(Screen):
    selected_skin = StringProperty("assets/image/cube_1.png")  # Default skin
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.skin_buttons = []
        Clock.schedule_once(self._initialize_ui, 0.1)
        
    def _initialize_ui(self, dt):
        # Start preview rotation animation
        self._start_preview_rotation()
        
        # Create skin buttons dynamically
        self._create_skin_buttons()
    
    def _start_preview_rotation(self):
        # Create a smooth rotation animation for the preview
        if hasattr(self.ids, 'skin_preview'):
            # Set initial angle
            self.ids.skin_preview.angle = 0
            
            # Create rotation animation
            anim = Animation(angle=360, duration=8)
            anim.repeat = True
            anim.start(self.ids.skin_preview)
    
    def _create_skin_buttons(self):
        # Get all cube skins
        skin_files = sorted([f for f in os.listdir("assets/image/") if f.startswith("cube_") and f.endswith(".png")])
        
        # Clear existing buttons
        if hasattr(self.ids, 'skin_grid'):
            self.ids.skin_grid.clear_widgets()
            self.skin_buttons = []
            
            # Create a button for each skin
            for skin_file in skin_files:
                skin_path = f"assets/image/{skin_file}"
                
                # Create button with skin as background
                btn = SkinButton(skin_path=skin_path)
                
                # Add selection highlight initially for the currently selected skin
                if skin_path == self.selected_skin:
                    btn.selected = True
                    with btn.canvas.after:
                        Color(0.4, 0.6, 1, 1)
                        Line(rounded_rectangle=(btn.x, btn.y, btn.width, btn.height, dp(10)), width=dp(3))
                
                # Bind event
                btn.bind(on_release=lambda btn=btn: self.select_skin(btn.skin_path))
                self.ids.skin_grid.add_widget(btn)
                self.skin_buttons.append(btn)
    
    def select_skin(self, skin):
        # Update the preview
        self.selected_skin = skin
        
        # Visual feedback for selected skin
        for btn in self.skin_buttons:
            # Clear previous selection highlight
            btn.canvas.after.clear()
            
            # Add highlight to the selected button
            if btn.skin_path == skin:
                with btn.canvas.after:
                    Color(0.4, 0.6, 1, 1)  # Highlight color
                    Line(rounded_rectangle=(btn.x, btn.y, btn.width, btn.height, dp(10)), width=dp(3))
                btn.selected = True
            else:
                btn.selected = False
        
        # Update the game state
        app = App.get_running_app()
        app.player_skin = skin

        # Update the game screen if it exists
        game_screen = self.manager.get_screen('game')
        game_screen.player_skin = skin

        print(f"Selected skin: {self.selected_skin}")
        
    def on_size(self, *args):
        # Update button positions and selection highlights when screen size changes
        Clock.schedule_once(self._update_buttons, 0.1)
        
    def _update_buttons(self, dt):
        for btn in self.skin_buttons:
            if btn.selected:
                btn.canvas.after.clear()
                with btn.canvas.after:
                    Color(0.4, 0.6, 1, 1)
                    Line(rounded_rectangle=(btn.x, btn.y, btn.width, btn.height, dp(10)), width=dp(3))
