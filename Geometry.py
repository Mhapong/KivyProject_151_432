from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, BooleanProperty

# ตัวละครผู้เล่น
class Player(Image):
    velocity = NumericProperty(0)
    gravity = -0.5
    jump_strength = 10
    on_ground = BooleanProperty(True)
    
    def jump(self):
        if self.on_ground:
            self.velocity = self.jump_strength
            self.on_ground = False

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        
        if self.y <= 0:
            self.y = 0
            self.velocity = 0
            self.on_ground = True

# หน้าจอเกม (ใช้สำหรับทุกด่าน)
class GameScreen(Screen):
    def __init__(self, level, **kwargs):
        super().__init__(**kwargs)
        self.level = level  # เก็บหมายเลขด่าน
        self.player = Player(source='cube_85.png', size_hint=(None, None), size=(50, 50), pos=(100, 100))
        self.add_widget(self.player)
        Clock.schedule_interval(self.update, 1/60)
        Window.bind(on_key_down=self.on_key_down)

        # แสดงชื่อด่านที่มุมบนซ้าย
        level_label = Label(text=f"Level {self.level}", font_size="24sp", size_hint=(None, None), pos=(20, Window.height - 50))
        self.add_widget(level_label)

        # ปุ่มกลับไปที่หน้าจอเลือกด่าน
        back_button = Button(text="Back", size_hint=(None, None), size=(100, 50), pos=(20, 20))
        back_button.bind(on_press=self.back_to_levels)
        self.add_widget(back_button)
    
    def on_key_down(self, instance, key, *args):
        if key == 32:  # Spacebar
            self.player.jump()
    
    def update(self, dt):
        self.player.update()

    def back_to_levels(self, instance):
        self.manager.current = "level_select"

# หน้าจอเลือกด่าน
class LevelSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        title = Label(
            text="Select Level",
            font_size="40sp",
            size_hint=(None, None),
            size=(400, 100),
            pos_hint={"center_x": 0.5, "top": 1}
        )
        self.add_widget(title)
        
        # ปุ่มเลือกด่าน
        levels = 3  # กำหนดจำนวนด่าน
        for i in range(1, levels + 1):
            btn = Button(
                text=f"Level {i}",
                font_size="24sp",
                size_hint=(None, None),
                size=(200, 60),
                pos_hint={"center_x": 0.5, "center_y": 0.6 - (i * 0.15)}
            )
            btn.bind(on_press=self.start_level)
            btn.level = i  # กำหนดหมายเลขด่านให้ปุ่ม
            self.add_widget(btn)
        
        # ปุ่มกลับไปเมนู
        back_button = Button(text="Back to Menu", size_hint=(None, None), size=(200, 50), pos_hint={"center_x": 0.5, "center_y": 0.1})
        back_button.bind(on_press=self.back_to_menu)
        self.add_widget(back_button)

    def start_level(self, instance):
        level = instance.level  # ดึงหมายเลขด่าน
        self.manager.get_screen(f"game{level}").player.pos = (100, 100)  # รีเซ็ตตำแหน่งตัวละคร
        self.manager.current = f"game{level}"  # เปลี่ยนไปหน้าด่านที่เลือก

    def back_to_menu(self, instance):
        self.manager.current = "menu"

# หน้าเมนูหลัก
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        title = Label(
            text="Geometry at Home",
            font_size="40sp",
            bold=True,
            size_hint=(None, None),
            size=(400, 100),
            pos_hint={"center_x": 0.5, "top": 1}
        )
        self.add_widget(title)
        
        play_button = Button(
            text="Play",
            font_size="24sp",
            size_hint=(None, None),
            size=(200, 60),
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.4}
        )
        play_button.bind(on_press=self.start_game)
        self.add_widget(play_button)
    
    

# แอปหลัก
class GeometryDashApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(LevelSelectScreen(name="level_select"))

        # เพิ่มด่านหลายด่าน
        for i in range(1, 4):  # ด่าน 1-3
            sm.add_widget(GameScreen(name=f"game{i}", level=i))

        return sm

if __name__ == '__main__':
    GeometryDashApp().run()
