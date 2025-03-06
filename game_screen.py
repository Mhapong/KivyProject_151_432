from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from game_logic import Player, FinishLine, Floor, Platform, Spike, BoostPad
import random
import json

Builder.load_file('kv/game.kv')

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Create game world
        self.game_world = Widget()
        self.add_widget(self.game_world)
        
        # Create background
        with self.game_world.canvas.before:
            Color(0.2, 0.2, 0.2)
            self.bg = Rectangle(pos=(0, 0), size=(Window.width * 3, Window.height))
        
        # Create floor
        self.floor = Floor()
        self.game_world.add_widget(self.floor)
        
        # Create player
        self.player = Player(size=(30, 30))  # ทำให้ตัวละครเล็กลง
        self.game_world.add_widget(self.player)
        
        # Initialize lists
        self.obstacles = []
        self.platforms = []
        
        # Setup keyboard and mouse
        Window.bind(on_key_down=self._on_key_down)
        Window.bind(on_mouse_down=self._on_mouse_down)
        
        # Start game loop
        Clock.schedule_interval(self.update, 1.0/60.0)
    
    def update(self, dt):
        # Move platforms and obstacles to the left
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

        if self.player.update(dt, self.obstacles):
            self.game_over()
            return

        self.check_platform_collisions()
        
        if hasattr(self, 'finish_line_x') and self.player.world_x >= self.finish_line_x:
            self.level_complete()
    
    def _on_key_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 32:  # Spacebar
            self.player.jump()
    
    def _on_mouse_down(self, instance, x, y, button, modifiers):
        if button == 'left':
            self.player.jump()
    
    def game_over(self):
        print("Game Over!")
        self.player.die()  # เพิ่มการเรียกใช้ฟังก์ชัน die() ของ player
        Clock.schedule_once(self.go_to_stage_selection, 1)  # รอ 1 วินาทีก่อนเปลี่ยนหน้าจอ
        
    def level_complete(self):
        print("Level Complete!")
        self.manager.current = 'stage_selection'
        
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
                        obstacle = Spike()
                    elif obstacle_data['type'] == 'boost_pad':
                        obstacle = BoostPad()
                    else:
                        continue
                    obstacle.pos = (obstacle_data['x'], obstacle_data['y'])
                    self.obstacles.append(obstacle)
                    self.game_world.add_widget(obstacle)
            
            # สร้างเส้นชัย
            self.finish_line_x = self.level_data['finish_x']
            self.finish_line = FinishLine(pos=(self.finish_line_x, 0))
            self.game_world.add_widget(self.finish_line)
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
                if self.player.velocity_y < 0:  # ถ้ากำลังตกลงมา
                    self.player.pos = (self.player.pos[0], platform.pos[1] + platform.size[1])
                    self.player.velocity_y = 0
                    self.player.is_jumping = False
                    self.player.rotation = 0
                    
    def check_collision(self, rect1, rect2):
        return (rect1[0] < rect2[0] + rect2[2] and
                rect1[0] + rect1[2] > rect2[0] and
                rect1[1] < rect2[1] + rect2[3] and
                rect1[1] + rect2[3] > rect2[1])
    
    def go_to_stage_selection(self, dt):
        self.manager.current = 'stage_selection'