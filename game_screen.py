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
from kivy.properties import StringProperty  # Add this import
from game_logic import Player, Floor, Platform, Spike, BoostPad, FinishLine
import json
import os  # Add this import

class GameScreen(Screen):
    # Add this property
    player_skin = StringProperty('assets/image/cube_5.png')  # Default skin
    
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
        
        for obstacle in self.obstacles[:]:
            obstacle.x -= self.player.moving_speed * dt
            if obstacle.right < 0:
                self.obstacles.remove(obstacle)
                self.game_world.remove_widget(obstacle)
        
        # Move finish lines
        for finish_line in self.finish_lines[:]:
            finish_line.x -= self.player.moving_speed * dt
            
            # Debug print to verify finish line position
            print(f"Finish line at: {finish_line.pos}, Player at: {self.player.pos}")
            
            # Check if player reached finish line
            if finish_line.check_collision(self.player):
                self.level_complete()
                return

        # Rest of your update logic remains the same
        on_platform = self.check_platform_collisions()
        if not on_platform:
            self.player.on_ground = False

        if self.player.update(dt, self.obstacles, self.platforms):
            self.game_over()
            return
    
    def _on_key_down(self, instance, keyboard, keycode, text, modifiers):
        if isinstance(keycode, tuple):
            code, key = keycode
        else:
            code = keycode
            key = None

        # Check both the keycode number and name for space
        if code == 32 or key == 'spacebar' or key == 'space':
            if self.player and self.player.on_ground:
                self.player.jump()

    def _on_mouse_down(self, instance, x, y, button, modifiers):
        if button == 'left':
            if self.player and self.player.on_ground:
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
        retry_button.bind(on_press=self.retry_level)
        back_button = Button(text="Back to Stage Selection", size_hint=(1, 0.2))
        back_button.bind(on_press=self.go_to_stage_selection)
        layout.add_widget(label)
        layout.add_widget(retry_button)
        layout.add_widget(back_button)
        self.popup = Popup(title="Game Over", content=layout, size_hint=(0.5, 0.5))
        self.popup.open()
        
    def show_level_complete_popup(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text="Level Complete!")
        next_button = Button(text="Next Level", size_hint=(1, 0.2))
        next_button.bind(on_press=self.go_to_next_level)
        back_button = Button(text="Back to Stage Selection", size_hint=(1, 0.2))
        back_button.bind(on_press=self.go_to_stage_selection)
        layout.add_widget(label)
        layout.add_widget(next_button)
        layout.add_widget(back_button)
        self.popup = Popup(title="Congratulations!", content=layout, size_hint=(0.5, 0.5))
        self.popup.open()
        
    def retry_level(self, instance):
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
        self.popup.dismiss()
        
    def go_to_next_level(self, instance):
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
                    if hasattr(self, 'popup'):
                        self.popup.dismiss()
                    
            except FileNotFoundError:
                print(f"Level {next_level} not found.")
                self.manager.current = 'stage_selection'
                if hasattr(self, 'popup'):
                    self.popup.dismiss()
                
        except (ValueError, AttributeError) as e:
            print(f"Error parsing level number: {e}")
            self.manager.current = 'stage_selection'
            if hasattr(self, 'popup'):
                self.popup.dismiss()
        
    def go_to_stage_selection(self, instance=None):
        if self.game_loop:
            self.game_loop.cancel()
            self.game_loop = None
        self.manager.current = 'stage_selection'
        if hasattr(self, 'popup'):
            self.popup.dismiss()
        
    def go_to_home(self, instance):
        self.manager.current = 'home'
        if hasattr(self, 'popup'):
            self.popup.dismiss()
        
    def on_enter(self):
        self.setup_level()
        
    def setup_level(self):
        if self.game_loop:
            self.game_loop.cancel()
            self.game_loop = None
        Clock.unschedule(self.update)
        
        if hasattr(self, 'level_file'):
            self.load_level(self.level_file)
            
            if self.player:
                # Position player
                if self.platforms:
                    first_platform = self.platforms[0]
                    self.player.pos = (100, first_platform.top + 10)
                else:
                    self.player.pos = (100, 100)
                
                # Reset player state
                self.player.world_x = 0
                self.player.velocity = 0
                self.player.moving_speed = 500
                self.player.on_ground = True
                self.player.is_jumping = False
                self.player.rotation = 0
                self.player.opacity = 1
                self.player.source = self.player_skin
                self.player.original_source = self.player_skin  # Set original source
            
            # Start game loop
            self.game_loop = Clock.schedule_interval(self.update, 1.0/60.0)
            if self.background_music:
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
        
    def check_platform_collisions(self):
        for platform in self.platforms:
            # More precise collision detection
            if (self.player.velocity < 0 and  # Only check when falling
                self.player.x + self.player.width * 0.2 < platform.x + platform.width and
                self.player.x + self.player.width * 0.8 > platform.x and
                self.player.y > platform.y - 5 and
                self.player.y < platform.y + platform.height):
                
                # Snap to platform more precisely
                self.player.y = platform.top
                self.player.velocity = 0
                self.player.on_ground = True
                self.player.is_jumping = False
                
                # Snap rotation to nearest 90 degrees
                self.player.rotation = round(self.player.rotation / 90) * 90
                return True
        return False
                    
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
                    obstacle = Spike(pos=(obstacle_data['x'], obstacle_data['y']))
                elif obstacle_data['type'] == 'boost_pad':
                    obstacle = BoostPad(pos=(obstacle_data['x'], obstacle_data['y']))
                self.obstacles.append(obstacle)
                self.game_world.add_widget(obstacle)

    def create_finish_line(self):
        if 'finish_x' in self.level_data:
            finish_x = self.level_data['finish_x']
            print(f"Creating finish line at x={finish_x}")
            finish_line = FinishLine(pos=(finish_x, 0))
            self.finish_lines.append(finish_line)
            self.game_world.add_widget(finish_line)
            print(f"Finish line added: {finish_line}, position: {finish_line.pos}")
        else:
            print("No finish_x in level data!")