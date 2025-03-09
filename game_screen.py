from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.image import Image  # Add this import
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.audio import SoundLoader
from kivy.properties import StringProperty, NumericProperty, BooleanProperty  # Add these imports
from kivy.animation import Animation  # Add this import
from game_logic import Player, Floor, Platform, Spike, BoostPad, FinishLine
import json
import os  # Add this import

class GameScreen(Screen):
    # Add these properties
    player_skin = StringProperty('assets/image/default_skin.png')  # Default skin
    attempt_count = NumericProperty(1)
    paused = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Create game world
        self.game_world = self.ids.game_world
        
        # Get player from kv file
        self.player = self.ids.player
        
        # Initialize lists
        self.obstacles = []
        self.platforms = []
        self.finish_lines = []
        self.speed_portals = []  # Add this line
        
        # Setup keyboard and mouse
        Window.bind(on_key_down=self._on_key_down)
        Window.bind(on_mouse_down=self._on_mouse_down)
        
        # Load sounds
        self.death_sound = SoundLoader.load('assets/sounds/death.mp3')
        self.background_music = SoundLoader.load('assets/sounds/loop_dash.mp3')
        self.complete_sound = SoundLoader.load('assets/sounds/complete.mp3')
        
        if self.background_music:
            self.background_music.loop = True
        
        # Remove automatic game loop start
        self.game_loop = None
    
    # Rest of your methods remain unchanged
    def update(self, dt):
        # Move objects
        for platform in self.platforms[:]:  # Use slice to avoid modification during iteration
            platform.x -= self.player.moving_speed * dt
            if platform.right < 0:
                self.platforms.remove(platform)
                self.game_world.remove_widget(platform)
        
        # Move obstacles with custom positioning
        for obstacle in self.obstacles[:]:
            obstacle.x -= self.player.moving_speed * dt
            
            # Remove obstacles that move off-screen
            if obstacle.right < 0:
                self.obstacles.remove(obstacle)
                self.game_world.remove_widget(obstacle)
        
        # Move speed portals and check for collision
        for portal in self.speed_portals[:]:
            portal.x -= self.player.moving_speed * dt
            
            # Check for collision with player
            if self.player.collide_widget(portal):
                print(f"Player entered speed portal: {portal.speed_multiplier}x")
                self.player.moving_speed = 500 * portal.speed_multiplier  # Base speed * multiplier
            
            if portal.right < 0:
                self.speed_portals.remove(portal)
                self.game_world.remove_widget(portal)
        
        # Move finish lines with better debugging
        for finish_line in self.finish_lines[:]:
            old_x = finish_line.x
            finish_line.x -= self.player.moving_speed * dt
            
            # Additional debugging for level 3 - FIXED VERSION
            if "level3.json" in self.level_file and len(self.finish_lines) > 0:
                # Use a counter attribute instead of frames
                if not hasattr(self, 'frame_counter'):
                    self.frame_counter = 0
                self.frame_counter += 1
                
                if self.frame_counter % 60 == 0:  # Print every ~1 second (assuming 60fps)
                    print(f"Level 3 finish line at x={finish_line.x}, player at x={self.player.x}")
            
            # Debug when finish line is approaching
            if finish_line.x < Window.width * 2 and finish_line.x > -500:
                print(f"Finish line approaching: x={finish_line.x}, window_width={Window.width}")
            
            # Check if player reached finish line with improved detection
            if finish_line.check_collision(self.player):
                print("FINISH LINE REACHED!")
                self.level_complete()
                return
                
        # Rest of your update logic
        on_platform = self.check_platform_collisions()
        if not on_platform:
            self.player.on_ground = False

        if self.player.update(dt, self.obstacles, self.platforms):
            self.game_over()
            return
    
    def _on_key_down(self, instance, keyboard, keycode, text, modifiers):
        # Print more detailed debug info to help diagnose keyboard issues
        print(f"Game screen key handler: {keycode}, text: {text}, modifiers: {modifiers}")
        
        # Handle both tuple and direct code formats
        if isinstance(keycode, tuple):
            code, key = keycode
        else:
            code = keycode
            key = None
        
        # Check for Escape key to toggle pause
        if code == 27 or key == 'escape':
            print("ESC key detected, toggling pause")
            self.toggle_pause()
            return True
        
        return False  # Let other handlers process this key

    def _on_mouse_down(self, instance, x, y, button, modifiers):
        print(f"Mouse click detected at {x}, {y}, button: {button}")
        if button == 'left':
            print(f"Player state: on_ground={self.player.on_ground}")
            # Only call jump if the game is active
            if self.game_loop and self.player:
                self.player.jump()
    
    def game_over(self):
        print("Game Over!")
        self.stop_game()
        # Reset player visibility
        self.player.opacity = 1
        self.player.source = self.player_skin
        self.show_game_over_popup()
        
    def stop_game(self):
        if self.game_loop:
            self.game_loop.cancel()
            self.game_loop = None
        Clock.unschedule(self.update)
        if self.background_music:
            self.background_music.stop()
        if self.death_sound:
            self.death_sound.play()
        
    def level_complete(self):
        if self.background_music:
            self.background_music.stop()
        if self.complete_sound:
            self.complete_sound.play()
        print("Level Complete!")
        self.stop_game()
        
        try:
            # Get current level number and unlock next level
            level_file_name = os.path.basename(self.level_file)
            current_level = int(''.join(filter(str.isdigit, level_file_name)))
            stage_screen = self.manager.get_screen('stage_selection')
            stage_screen.unlock_next_level(current_level)
            
            self.show_level_complete_popup()
        except Exception as e:
            print(f"Error in level_complete: {e}")
            self.manager.current = 'stage_selection'
        
    def show_game_over_popup(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text="Game Over!")
        
        retry_button = Button(text="Retry", size_hint=(1, 0.2))
        retry_button.bind(on_release=self.retry_level)  # Use on_release instead of on_press
        
        back_button = Button(text="Back to Stage Selection", size_hint=(1, 0.2))
        back_button.bind(on_release=self.go_to_stage_selection)  # Use on_release
        
        layout.add_widget(label)
        layout.add_widget(retry_button)
        layout.add_widget(back_button)
        
        self.popup = Popup(title="Game Over", content=layout, size_hint=(0.5, 0.5), auto_dismiss=False)
        self.popup.open()
        
    def show_level_complete_popup(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text="Level Complete!")
        
        next_button = Button(text="Next Level", size_hint=(1, 0.2))
        next_button.bind(on_release=self.go_to_next_level)  # Use on_release
        
        back_button = Button(text="Back to Stage Selection", size_hint=(1, 0.2))
        back_button.bind(on_release=self.go_to_stage_selection)  # Use on_release
        
        layout.add_widget(label)
        layout.add_widget(next_button)
        layout.add_widget(back_button)
        
        self.popup = Popup(title="Congratulations!", content=layout, size_hint=(0.5, 0.5), auto_dismiss=False)
        self.popup.open()
        
    def retry_level(self, instance=None):
        if hasattr(self, 'popup') and self.popup:
            self.popup.dismiss()
            self.popup = None
        
        # Increment attempt counter when retrying
        self.attempt_count += 1
        
        # Update UI to show new attempt count
        if hasattr(self.ids, 'attempt_counter'):
            self.ids.attempt_counter.text = f"Attempt: {self.attempt_count}"
        
        # Hide pause menu if active
        if self.paused:
            pause_menu = self.ids.pause_menu
            pause_menu.opacity = 0
            pause_menu.disabled = True
            self.paused = False
        
        if self.game_loop:
            self.game_loop.cancel()
            self.game_loop = None
        Clock.unschedule(self.update)
        
        # Reset player state
        if self.platforms:
            first_platform = self.platforms[0]
            self.player.pos = (100, first_platform.top + 10)
        else:
            self.player.pos = (100, 100)
        
        self.player.moving_speed = 500
        self.player.velocity = 0
        self.player.on_ground = True
        self.player.is_jumping = False
        self.player.rotation = 0
        self.player.opacity = 1
        self.player.source = self.player_skin
        self.player.original_source = self.player_skin
        
        # Reload level
        self.load_level(self.level_file)
        
        # Start new game loop
        self.game_loop = Clock.schedule_interval(self.update, 1.0/60.0)
        if self.background_music:
            self.background_music.volume = 1.0
            self.background_music.play()
        
    def go_to_next_level(self, instance):
        if hasattr(self, 'popup') and self.popup:
            self.popup.dismiss()
            self.popup = None  # Set to None to ensure it's fully cleared
        
        try:
            level_file_name = os.path.basename(self.level_file)
            current_level = int(''.join(filter(str.isdigit, level_file_name)))
            next_level = current_level + 1
            next_level_file = f"assets/levels/level{next_level}.json"
            
            try:
                with open(next_level_file, 'r') as f:
                    # Cancel existing game loop
                    if self.game_loop:
                        self.game_loop.cancel()
                        self.game_loop = None
                    Clock.unschedule(self.update)
                    
                    # Load next level
                    self.level_file = next_level_file
                    self.setup_level()
                    self.manager.current = 'game'
                    
            except FileNotFoundError:
                print(f"Level {next_level} not found.")
                self.manager.current = 'stage_selection'
                
        except (ValueError, AttributeError) as e:
            print(f"Error parsing level number: {e}")
            self.manager.current = 'stage_selection'
        
    def go_to_stage_selection(self, instance=None):
        if hasattr(self, 'popup') and self.popup:
            self.popup.dismiss()
            self.popup = None  # Set to None to ensure it's fully cleared
        
        if self.game_loop:
            self.game_loop.cancel()
            self.game_loop = None
        Clock.unschedule(self.update)
        self.manager.current = 'stage_selection'
        
    def go_to_home(self, instance):
        self.manager.current = 'home'
        if hasattr(self, 'popup'):
            self.popup.dismiss()
        
    def on_enter(self):
        self.setup_level()
        
    def setup_level(self):
        # Reset attempt counter when starting a new level
        self.attempt_count = 1
        
        if self.game_loop:
            self.game_loop.cancel()
            self.game_loop = None
        Clock.unschedule(self.update)
        
        if hasattr(self, 'level_file'):
            self.load_level(self.level_file)
            
            # Update level name in UI
            if hasattr(self.ids, 'level_info') and hasattr(self, 'level_data'):
                level_name = self.level_data.get('name', 'Level')
                self.ids.level_info.text = level_name
                
            # Update attempt counter in UI
            if hasattr(self.ids, 'attempt_counter'):
                self.ids.attempt_counter.text = f"Attempt: {self.attempt_count}"
                
            if self.player:
                # Position player at proper height
                if self.platforms:
                    first_platform = self.platforms[0]
                    # Ensure player is positioned well above the platform to prevent immediate collision
                    self.player.pos = (100, first_platform.top + 20)  # Increased padding
                    # Explicitly set the player to be on ground
                    self.player.on_ground = True
                    self.player.velocity = 0
                else:
                    self.player.pos = (100, 150)  # Higher default position
                
                # Reset player state
                self.player.world_x = 0
                self.player.velocity = 0
                self.player.moving_speed = 500
                self.player.on_ground = True  # Ensure this is set
                self.player.is_jumping = False
                self.player.rotation = 0
                self.player.opacity = 1
                self.player.source = self.player_skin
                self.player.original_source = self.player_skin
                
                # Ensure pause menu is hidden
                if hasattr(self.ids, 'pause_menu'):
                    self.ids.pause_menu.opacity = 0
                    self.ids.pause_menu.disabled = True
                    self.paused = False
        
        # Start game loop
        self.game_loop = Clock.schedule_interval(self.update, 1.0/60.0)
        if self.background_music:
            self.background_music.volume = 1.0
            self.background_music.play()
    
    def load_level(self, level_file):
        try:
            with open(level_file, 'r') as f:
                try:
                    self.level_data = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON format in {level_file}: {str(e)}")
                    return
                
            # Set background image
            if 'background' in self.level_data:
                self.ids.background.source = self.level_data['background']
                
            # Clear existing objects
            self.clear_level_objects()
            
            # Create new objects
            self.create_platforms()
            self.create_obstacles()
            self.create_finish_line()
            self.create_speed_portals()  # Add this line
            
        except FileNotFoundError:
            print(f"Level file not found: {level_file}")
        except Exception as e:
            print(f"Error loading level: {str(e)}")

    def clear_level_objects(self):
        # Remove old platforms
        for platform in self.platforms:
            self.game_world.remove_widget(platform)
        self.platforms.clear()
        
        # Remove old obstacles
        for obstacle in self.obstacles:
            self.game_world.remove_widget(obstacle)
        self.obstacles.clear()
        
        # Remove old finish lines
        for finish_line in self.finish_lines:
            self.game_world.remove_widget(finish_line)
        self.finish_lines.clear()
        
        # Remove old speed portals
        for portal in self.speed_portals:
            self.game_world.remove_widget(portal)
        self.speed_portals.clear()
        
    def check_platform_collisions(self):
        on_platform = False
        for platform in self.platforms:
            # Simplified collision detection for jumping fix
            x_overlap = (self.player.x + self.player.width * 0.8 > platform.x and 
                        self.player.x + self.player.width * 0.2 < platform.x + platform.width)
            
            # Slightly more generous threshold
            below_threshold = 10
            
            if (x_overlap and
                abs(self.player.y - platform.top) < below_threshold and
                self.player.velocity <= 0):  # Only when falling or standing
                
                self.player.y = platform.top
                self.player.velocity = 0
                if not self.player.on_ground:  # Only update if changing state
                    print("Player landed on platform")
                    self.player.on_ground = True
                    self.player.is_jumping = False
                    
                    # Snap rotation to nearest 90 degrees
                    self.player.rotation = round(self.player.rotation / 90) * 90
                on_platform = True
                break
        
        if not on_platform and self.player.on_ground:
            print("Player left platform")
        
        return on_platform
                    
    def check_collision(self, rect1, rect2):
        return (rect1[0] < rect2[0] + rect2[2] and
                rect1[0] + rect1[2] > rect2[0] and
                rect1[1] < rect2[1] + rect2[3] and
                rect1[1] + rect2[3] > rect2[1])

    def create_platforms(self):
        if 'platforms' in self.level_data:
            for platform_data in self.level_data['platforms']:
                pos = platform_data['pos']
                size = platform_data['size']
                platform = Platform(pos=pos, size=size)
                self.platforms.append(platform)
                self.game_world.add_widget(platform)

    def create_obstacles(self):
        if 'obstacles' in self.level_data:
            for obstacle_data in self.level_data['obstacles']:
                if obstacle_data['type'] == 'spike':
                    # Create the spike
                    obstacle = Spike(pos=(obstacle_data['x'], obstacle_data['y']))
                    self.obstacles.append(obstacle)
                    self.game_world.add_widget(obstacle)
                    obstacle.initial_x = obstacle_data['x']
                    
                elif obstacle_data['type'] == 'rotating_spike':
                    # Create the rotating spike
                    angle = obstacle_data.get('angle', 180)  # Default to 180 if not specified
                    obstacle = RotatingSpike(pos=(obstacle_data['x'], obstacle_data['y']), angle=angle)
                    self.obstacles.append(obstacle)
                    self.game_world.add_widget(obstacle)
                    obstacle.initial_x = obstacle_data['x']
                    
                elif obstacle_data['type'] == 'boost_pad':
                    # Create the boost pad
                    obstacle = BoostPad(pos=(obstacle_data['x'], obstacle_data['y']))
                    self.obstacles.append(obstacle)
                    self.game_world.add_widget(obstacle)
                    obstacle.initial_x = obstacle_data['x']

    def create_finish_line(self):
        if 'finish_x' in self.level_data:
            finish_x = self.level_data['finish_x']
            print(f"Creating finish line at x={finish_x} for level {os.path.basename(self.level_file)}")
            
            # Make sure the finish line is visible - improve its appearance
            finish_line = FinishLine(pos=(finish_x, 0))
            self.finish_lines.append(finish_line)
            self.game_world.add_widget(finish_line)
            print(f"Finish line added: {finish_line}, position: {finish_line.pos}")
        else:
            print(f"No finish_x in level data for {os.path.basename(self.level_file)}!")

    def create_speed_portals(self):
        if 'speed_portals' in self.level_data:
            for portal_data in self.level_data['speed_portals']:
                portal = SpeedPortal(pos=(portal_data['x'], 100), 
                                    speed_multiplier=portal_data['speed'])
                self.speed_portals.append(portal)
                self.game_world.add_widget(portal)

    def on_size(self, *args):
        """Ensure game_world covers the entire screen when resized"""
        if hasattr(self, 'game_world') and self.game_world:
            self.game_world.size = self.size

    def toggle_pause(self):
        if self.game_loop:
            if not self.paused:
                # Pause the game
                self.paused = True
                self.old_game_loop = self.game_loop
                self.game_loop.cancel()
                self.game_loop = None
                
                # Show pause menu
                pause_menu = self.ids.pause_menu
                pause_menu.disabled = False
                anim = Animation(opacity=1, duration=0.3)
                anim.start(pause_menu)
                
                # Pause music
                if self.background_music:
                    self.background_music.volume = 0.3
            else:
                self.resume_game()

    def resume_game(self):
        # Hide pause menu first
        pause_menu = self.ids.pause_menu
        anim = Animation(opacity=0, duration=0.3)
        
        def on_complete(*args):
            pause_menu.disabled = True
            
            # Unpause the game
            self.paused = False
            if not self.game_loop:
                self.game_loop = Clock.schedule_interval(self.update, 1.0/60.0)
            
            # Resume music
            if self.background_music:
                self.background_music.volume = 1.0
        
        anim.bind(on_complete=on_complete)
        anim.start(pause_menu)