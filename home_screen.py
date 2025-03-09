from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.animation import Animation
from kivy.properties import NumericProperty
from kivy.clock import Clock

# Load the KV file
Builder.load_file('kv/home.kv')

class HomePage(Screen):
    def __init__(self, **kwargs):
        super(HomePage, self).__init__(**kwargs)
        self.logo_anim = None
        
    def on_enter(self):
        """Animate elements when the screen is shown"""
        # Reset and start animations when entering the screen
        self.animate_elements()
    
    def animate_elements(self):
        # Main layout fade in animation
        main_layout = self.ids.main_layout
        main_layout.opacity = 0
        anim = Animation(opacity=1, duration=1.0)
        anim.start(main_layout)
        
        # Logo animation
        logo = self.ids.logo
        logo.opacity = 0
        logo.angle = 0  # Setting an attribute that might not exist
        
        # First animate the opacity
        anim1 = Animation(opacity=1, duration=0.8)
        
        # Then start the rotating animation
        def start_rotation(*args):
            if not hasattr(logo, 'angle'):
                logo.angle = 0  # This check exists but the attribute is already set above
            
            # Create a continuous rotation animation
            self.logo_anim = Animation(angle=360, duration=4)
            self.logo_anim.repeat = True
            self.logo_anim.start(logo)
        
        anim1.bind(on_complete=start_rotation)
        anim1.start(logo)

    def go_to_skin_selector(self, instance):
        self.manager.current = 'skin_selector'

    def go_to_level_selection(self, instance):
        self.manager.current = 'stage_selection'

    def go_to_settings(self, instance):
        print("Settings button pressed")

    def unlock_all_levels(self, instance):
        # Get reference to the stage selection screen
        stage_screen = self.manager.get_screen('stage_selection')
        
        # Find all level files and unlock them
        import os
        level_files = [f for f in os.listdir("assets/levels/") if f.endswith(".json")]
        
        # Extract level numbers and unlock all
        for level_file in level_files:
            level_name = level_file.replace(".json", "")
            level_number = int(''.join(filter(str.isdigit, level_name)))
            stage_screen.unlocked_levels.add(level_number)
        
        # Reload the level buttons with new unlock status
        stage_screen.load_levels()
        
        # Show confirmation message with animation
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        
        content = Label(
            text='All levels have been unlocked!',
            font_size='18sp'
        )
        popup = Popup(
            title='Levels Unlocked',
            content=content,
            size_hint=(0.6, 0.3),
            title_color=[0.1, 0.7, 0.3, 1],
            title_size='20sp',
            title_align='center'
        )
        
        # Animate the popup
        popup.opacity = 0
        popup.open()
        
        # Fade in animation
        anim = Animation(opacity=1, duration=0.3)
        anim.start(popup)
        
        # Auto-dismiss after 2 seconds
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)