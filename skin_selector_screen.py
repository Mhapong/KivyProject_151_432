from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.core.window import Window
import os

class SkinButton(Button):
    def __init__(self, skin_path, **kwargs):
        super().__init__(**kwargs)
        self.skin_path = skin_path
        # Use responsive sizing based on window size
        button_size = min(dp(150), Window.width / 5)
        self.size_hint = (None, None)
        self.size = (button_size, button_size)
        
        # Use the skin image as the button background
        self.background_normal = skin_path
        self.background_down = skin_path  # Same image when pressed
        
        # Adjust border to none so it's just the image
        self.border = (0, 0, 0, 0)
        
        # Track selection state
        self.selected = False
        
    def on_press(self):
        # Provide visual feedback with a subtle scale animation
        anim = Animation(size=(self.width * 0.95, self.height * 0.95), duration=0.1)
        anim.start(self)
        
    def on_release(self):
        # Return to normal size
        button_size = min(dp(150), Window.width / 5)
        anim = Animation(size=(button_size, button_size), duration=0.2)
        anim.start(self)

class SkinSelectorScreen(Screen):
    selected_skin = StringProperty("assets/image/cube_1.png")  # Default skin
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.skin_buttons = []
        # Bind to window size changes for responsive updates
        Window.bind(on_resize=self.on_window_resize)
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
        try:
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
                        self._add_highlight_to_button(btn)
                    
                    # Bind event
                    btn.bind(on_release=lambda btn=btn: self.select_skin(btn.skin_path))
                    self.ids.skin_grid.add_widget(btn)
                    self.skin_buttons.append(btn)
                    
                # Update grid columns based on window width
                self._update_grid_columns()
        except Exception as e:
            print(f"Error creating skin buttons: {e}")
    
    def _add_highlight_to_button(self, btn):
        with btn.canvas.after:
            Color(0.4, 0.6, 1, 1)  # Highlight color
            Line(rounded_rectangle=(btn.x, btn.y, btn.width, btn.height, dp(10)), width=3)
    
    def select_skin(self, skin):
        # Update the preview
        self.selected_skin = skin
        
        # Visual feedback for selected skin
        for btn in self.skin_buttons:
            # Clear previous selection highlight
            btn.canvas.after.clear()
            
            # Add highlight to the selected button
            if btn.skin_path == skin:
                self._add_highlight_to_button(btn)
                btn.selected = True
            else:
                btn.selected = False
        
        # Update the game state
        app = App.get_running_app()
        app.player_skin = skin

        # Update the game screen if it exists
        if hasattr(self.manager, 'get_screen'):
            game_screen = self.manager.get_screen('game')
            game_screen.player_skin = skin

        print(f"Selected skin: {self.selected_skin}")
    
    def on_size(self, *args):
        # Update button positions and selection highlights when screen size changes
        Clock.schedule_once(self._update_ui_for_new_size, 0.1)
    
    def on_window_resize(self, instance, width, height):
        # Update UI when window is resized
        Clock.schedule_once(self._update_ui_for_new_size, 0.1)
    
    def _update_ui_for_new_size(self, dt):
        # Update preview image size
        if hasattr(self.ids, 'skin_preview'):
            preview_size = min(dp(150), self.width * 0.3)
            self.ids.skin_preview.size = (preview_size, preview_size)
        
        # Update button sizes
        for btn in self.skin_buttons:
            button_size = min(dp(150), Window.width / 5)
            btn.size = (button_size, button_size)
            
            # Update selection highlight
            if btn.selected:
                btn.canvas.after.clear()
                self._add_highlight_to_button(btn)
        
        # Update grid columns
        self._update_grid_columns()
    
    def _update_grid_columns(self):
        if hasattr(self.ids, 'skin_grid'):
            # Calculate optimal number of columns based on window width
            # For phones (narrow screens): 2-3 columns
            # For tablets: 4-5 columns
            # For desktop: 5-7 columns
            if Window.width < dp(600):  # Phone
                self.ids.skin_grid.cols = max(2, min(3, int(Window.width / dp(180))))
            elif Window.width < dp(1000):  # Tablet
                self.ids.skin_grid.cols = max(3, min(5, int(Window.width / dp(200))))
            else:  # Desktop
                self.ids.skin_grid.cols = max(5, min(7, int(Window.width / dp(220))))
            
            # Update spacing based on window size
            self.ids.skin_grid.spacing = [dp(8) + Window.width * 0.01, dp(8) + Window.width * 0.01]
