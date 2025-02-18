from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, BooleanProperty


class Player(Image):
    velocity = NumericProperty(0)
    gravity = -0.5
    jump_strength = 10
    on_ground = BooleanProperty(True)  # เพิ่มตัวแปรเพื่อตรวจสอบว่าตัวละครอยู่บนพื้นหรือไม่
    
    def jump(self):
        if self.on_ground:  # กระโดดได้เฉพาะเมื่ออยู่บนพื้น
            self.velocity = self.jump_strength
            self.on_ground = False  # เมื่อลอยขึ้น ให้ถือว่าไม่อยู่บนพื้น

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        
        if self.y <= 0:
            self.y = 0
            self.velocity = 0
            self.on_ground = True  # ตั้งค่าเป็น True เมื่อแตะพื้น

class GameScreen(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player(source='cube_85.png', size_hint=(None, None), size=(50, 50), pos=(100, 100))
        self.add_widget(self.player)
        Clock.schedule_interval(self.update, 1/60)
        Window.bind(on_key_down=self.on_key_down)
    
    def on_key_down(self, instance, key, *args):
        if key == 32:  # Spacebar
            self.player.jump()
    
    def update(self, dt):
        self.player.update()

class GeometryDashApp(App):
    def build(self):
        return GameScreen()

if __name__ == '__main__':
    GeometryDashApp().run()
