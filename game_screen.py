from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.audio import SoundLoader
from game_logic import Player, Floor, Platform, Spike, BoostPad, FinishLine
import json

Builder.load_file('kv/game.kv')

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Create game world
        self.game_world = self.ids.game_world
        
        # Create floor
        self.floor = Floor()
        self.game_world.add_widget(self.floor)
        
        # Get player from kv file
        self.player = self.ids.player
        
        # Initialize lists
        self.obstacles = []
        self.platforms = []
        self.finish_lines = []  # สร้าง list สำหรับเก็บเส้นชัย
        
        # Setup keyboard and mouse
        Window.bind(on_key_down=self._on_key_down)
        Window.bind(on_mouse_down=self._on_mouse_down)
        
        # Load sounds
        self.death_sound = SoundLoader.load('assets/sounds/death.wav')
        self.game_over_music = SoundLoader.load('assets/sounds/game_over.mp3')
        
        # Start game loop
        self.game_loop = Clock.schedule_interval(self.update, 1.0/60.0)
    
    def update(self, dt):
        # Move platforms, obstacles, and finish line to the left
        for platform in self.platforms:
            platform.x -= self.player.moving_speed * dt
            if platform.right < 0:
                self.platforms.remove(platform)
                self.game_world.remove_widget(platform)
        
        for obstacle in self.obstacles:
            obstacle.x -= self.player.moving_speed * dt
            if obstacle.right < 0:
                self.obstacles.remove(obstacle)
                self.game_world.remove_widget(obstacle)

        # เคลื่อนที่เส้นชัยไปทางซ้าย
        for finish_line in self.finish_lines:
            finish_line.x -= self.player.moving_speed * dt

        # Update player and check collisions
        player_died = self.player.update(dt, self.obstacles, self.platforms)
        if player_died:
            self.game_over()
            return

        # ตรวจสอบการชนกับเส้นชัย
        for finish_line in self.finish_lines:
            if finish_line.check_collision(self.player):
                self.level_complete()
                return
    
    def _on_key_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 32:  # Spacebar
            self.player.jump()
    
    def _on_mouse_down(self, instance, x, y, button, modifiers):
        if button == 'left':
            self.player.jump()
    
    def game_over(self):
        print("Game Over!")
        self.player.on_death()  # เรียกฟังก์ชัน on_death ของตัวละคร
        self.stop_game()  # หยุดการเคลื่อนไหวทั้งหมด
        self.show_game_over_popup()
        
    def stop_game(self):
        self.game_loop.cancel()  # หยุดการอัปเดตฟังก์ชัน Clock.schedule_interval
        self.player.stop()  # หยุดการเคลื่อนที่ของตัวละคร
        if self.death_sound:
            self.death_sound.play()  # เล่นเสียงการตาย
        if self.game_over_music:
            self.game_over_music.play()  # เล่นเพลง Game Over
        
    def level_complete(self):
        print("Level Complete!")
        self.stop_game()
        self.show_level_complete_popup()
        
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
        self.player.reset_position()  # รีเซ็ตตำแหน่งของตัวละคร
        self.setup_level()  # เรียกใช้ฟังก์ชัน setup_level เพื่อเริ่มเกมใหม่
        self.popup.dismiss()
        self.game_loop = Clock.schedule_interval(self.update, 1.0/60.0)  # รีสตาร์ทการเลื่อนฉาก
        
    def go_to_next_level(self, instance):
        try:
            # Extract level number more robustly using os.path
            import os
            level_file_name = os.path.basename(self.level_file)  # Get just the filename
            current_level = int(''.join(filter(str.isdigit, level_file_name)))  # Extract digits
            next_level = current_level + 1
            next_level_file = f"assets/levels/level{next_level}.json"
            
            try:
                with open(next_level_file, 'r') as f:
                    self.level_file = next_level_file
                    self.setup_level()
                    self.manager.current = 'game'
                    self.popup.dismiss()
                    self.game_loop = Clock.schedule_interval(self.update, 1.0/60.0)
            except FileNotFoundError:
                print(f"Level {next_level} not found.")
                self.manager.current = 'stage_selection'
                self.popup.dismiss()
                
        except (ValueError, AttributeError) as e:
            print(f"Error parsing level number: {e}")
            self.manager.current = 'stage_selection'
            self.popup.dismiss()
        
    def go_to_stage_selection(self, instance=None):
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
        # Load the level file specified in the start_game method
        if hasattr(self, 'level_file'):
            self.load_level(self.level_file)
        self.player.pos = (100, 100)  # เริ่มต้นที่พื้น
        self.player.world_x = 0  # Reset world_x
    
    def load_level(self, level_file):
        try:
            with open(level_file, 'r') as f:
                self.level_data = json.load(f)
                
            # Set background image
            if 'background' in self.level_data:
                self.ids.background.source = self.level_data['background']
                
            # ลบ platforms เก่า
            for platform in self.platforms:
                self.game_world.remove_widget(platform)
            self.platforms.clear()
            
            # สร้าง platforms ใหม่
            if 'platforms' in self.level_data:
                for platform_data in self.level_data['platforms']:
                    pos = platform_data['pos']
                    size = platform_data['size']
                    platform = Platform(pos=pos, size=size)
                    self.platforms.append(platform)
                    self.game_world.add_widget(platform)
            
            # ลบ obstacles เก่า
            for obstacle in self.obstacles:
                self.game_world.remove_widget(obstacle)
            self.obstacles.clear()
            
            # สร้าง obstacles ใหม่
            if 'obstacles' in self.level_data:
                for obstacle_data in self.level_data['obstacles']:
                    if obstacle_data['type'] == 'spike':
                        obstacle = Spike(pos=(obstacle_data['x'], obstacle_data['y']))
                    elif obstacle_data['type'] == 'boost_pad':
                        obstacle = BoostPad(pos=(obstacle_data['x'], obstacle_data['y']))
                    else:
                        continue
                    self.obstacles.append(obstacle)
                    self.game_world.add_widget(obstacle)
            
            # ลบเส้นชัยเก่า
            for finish_line in self.finish_lines:
                self.game_world.remove_widget(finish_line)
            self.finish_lines.clear()
            
            # สร้างเส้นชัยใหม่
            finish_x = self.level_data['finish_x']
            finish_line = FinishLine(pos=(finish_x, 0))
            self.finish_lines.append(finish_line)
            self.game_world.add_widget(finish_line)
        except FileNotFoundError:
            print(f"Level file not found: {level_file}")
        except json.JSONDecodeError:
            print(f"Invalid JSON format in: {level_file}")
        except KeyError as e:
            print(f"Missing required data: {e}")
        
    def check_platform_collisions(self):
        player_rect = [self.player.pos[0], self.player.pos[1], 
                      self.player.size[0], self.player.size[1]]
                      
        for platform in self.platforms:
            if self.check_collision(player_rect, [platform.pos[0], platform.pos[1],
                                                platform.size[0], platform.size[1]]):
                if self.player.velocity < 0:  # ถ้ากำลังตกลงมา
                    self.player.pos = (self.player.pos[0], platform.pos[1] + platform.size[1])
                    self.player.velocity = 0
                    self.player.is_jumping = False
                    self.player.rotation = 0
                    
    def check_collision(self, rect1, rect2):
        return (rect1[0] < rect2[0] + rect2[2] and
                rect1[0] + rect1[2] > rect2[0] and
                rect1[1] < rect2[1] + rect2[3] and
                rect1[1] + rect2[3] > rect2[1])