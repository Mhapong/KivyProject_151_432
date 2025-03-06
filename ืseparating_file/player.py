from kivy.uix.image import Image
from kivy.properties import NumericProperty, BooleanProperty
from kivy.animation import Animation

class Player(Image):
    velocity = NumericProperty(0)
    jump_strength = 12
    on_ground = BooleanProperty(True)

    def jump(self):
        if self.on_ground:
            self.velocity = self.jump_strength
            self.on_ground = False

    def update(self, platforms, finish_line):
        self.y += self.velocity
        self.velocity -= 0.5

        for platform in platforms:
            if self.collide_widget(platform) and self.velocity <= 0:
                self.y = platform.y + platform.height
                self.velocity = 0
                self.on_ground = True
                break
        else:
            self.on_ground = False

        if self.collide_widget(finish_line):
            self.parent.level_complete()

    def reset_position(self):
        self.pos = (100, 300)
