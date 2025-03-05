import random
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, BooleanProperty
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

# Load the KV files
Builder.load_file('stage_selection.kv')
Builder.load_file('game.kv')

class StageSelectionScreen(Screen):
    pass

class GameScreen(Screen):
    def set_background(self, background_image):
        self.ids.background.source = background_image

    def on_enter(self):
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        Window.bind(on_key_down=self.on_key_down)
        self.spawn_spike()
        self.create_hole()

        # Create Finish Line
        self.finish_line = FinishLine()
        self.finish_line.x = Window.width + 800  # Adjust the distance further out
        self.finish_line.y = self.ids.ground1.top
        self.add_widget(self.finish_line)

    def on_leave(self):
        Clock.unschedule(self.update)
        Window.unbind(on_key_down=self.on_key_down)

    def update(self, dt):
        self.ids.player.update([self.ids.ground1, self.ids.ground2], [self.ids.spike], self.finish_line)

    def on_key_down(self, window, key, *args):
        if key == 32:  # 32 is the keycode for the spacebar
            self.ids.player.jump()

    def spawn_spike(self, dt=None):
        # Randomly decide whether to spawn a spike based on the level
        if random.random() < 0.1:  # Adjust the probability based on the level
            self.ids.spike.x = Window.width
        Clock.schedule_once(self.spawn_spike, random.uniform(1, 3))  # Adjust the spawn rate based on the level

    def create_hole(self, dt=None):
        # Randomly decide whether to create a hole in the ground
        if random.random() < 0.1:  # Adjust the probability based on the level
            hole_width = random.randint(50, 150)
            self.ids.ground1.size = (self.ids.ground1.width - hole_width, self.ids.ground1.height)
            self.ids.ground2.pos = (self.ids.ground1.right + hole_width, self.ids.ground2.y)
        Clock.schedule_once(self.create_hole, random.uniform(5, 10))  # Adjust the spawn rate based on the level

    def game_over(self):
        print("Game Over!")
        self.show_game_over_popup()

    def show_game_over_popup(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='Game Over!'))

        button_layout = BoxLayout(orientation='horizontal', spacing=10)
        reset_button = Button(text='Play Again')
        quit_button = Button(text='Quit')

        button_layout.add_widget(reset_button)
        button_layout.add_widget(quit_button)

        layout.add_widget(button_layout)

        popup = Popup(title='Game Over', content=layout, size_hint=(0.5, 0.5), auto_dismiss=False)

        reset_button.bind(on_release=lambda *args: self.reset_game(popup))
        quit_button.bind(on_release=lambda *args: self.quit_game())

        popup.open()
        
    def reset_game(self, popup):
        popup.dismiss()
        self.manager.current = 'stage_selection'
        
    def level_complete(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='You Win! 🎉'))

        button_layout = BoxLayout(orientation='horizontal', spacing=10)
        next_button = Button(text='Next Level')
        menu_button = Button(text='Main Menu')

        button_layout.add_widget(next_button)
        button_layout.add_widget(menu_button)
        layout.add_widget(button_layout)

        popup = Popup(title='Level Complete!', content=layout, size_hint=(0.5, 0.5), auto_dismiss=False)

        next_button.bind(on_release=lambda *args: self.next_level(popup))
        menu_button.bind(on_release=lambda *args: self.go_to_menu())

        popup.open()

    def next_level(self, popup):
        popup.dismiss()
        self.reset_game()

    def go_to_menu(self):
        self.manager.current = 'stage_selection'

    def quit_game(self):
        App.get_running_app().stop()

class Player(Image):
    velocity = NumericProperty(0)
    x_velocity = NumericProperty(4)  # Increase horizontal speed
    gravity = -0.5
    jump_strength = 12  # Reduce jump height
    on_ground = BooleanProperty(True)
    rotation = NumericProperty(0)  # Add rotation property

    def jump(self):
        if self.on_ground:
            self.velocity = self.jump_strength
            self.on_ground = False

    def update(self, platforms, obstacles,finish_line):
        self.velocity += self.gravity
        self.y += self.velocity

        # Continuously rotate while in the air
        if not self.on_ground:
            self.rotation += 5  # Adjust the rotation speed to be quicker

        # Move platforms to create the illusion of movement
        for platform in platforms:
            platform.x -= self.x_velocity

            # Reset platform position to create infinite map illusion
            if platform.right <= 0:
                platform.x = platform.width

        # Move obstacles to create the illusion of movement
        for obstacle in obstacles:
            obstacle.x -= self.x_velocity

            # Reset obstacle position if it moves off-screen
            if obstacle.right <= 0:
                obstacle.x = Window.width

        # Check for collision with platforms
        for platform in platforms:
            if self.collide_widget(platform) and self.velocity <= 0:
                self.y = platform.y + platform.height
                self.velocity = 0
                self.on_ground = True
                self.rotation = 0  # Reset rotation when on ground
                break
        else:
            self.on_ground = False

        # Check for collision with obstacles
        for obstacle in obstacles:
            if self.collide_widget(obstacle):
                # Handle collision with spike (e.g., end game, reduce health, etc.)
                App.get_running_app().root.get_screen('game').game_over()

        # Check if player falls into a hole
        if self.y < 0:
            App.get_running_app().root.get_screen('game').game_over()
            
        if self.collide_widget(finish_line):
            App.get_running_app().root.get_screen('game').level_complete()

class FinishLine(Image):
    pass

class Platform(Image):
    pass

class Spike(Widget):
    pass

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StageSelectionScreen(name='stage_selection'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    MyApp().run()