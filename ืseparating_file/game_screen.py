import random
import os
import json
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from finish_line import FinishLine
from obstacles import Spike, BoostPad
from player import Player

class GameScreen(Screen):
    def set_background(self, background_image):
        self.ids.background.source = background_image

    def load_level(self, level_name):
        level_path = os.path.join("levels", f"{level_name}.json")
        with open(level_path, "r") as f:
            level_data = json.load(f)

        self.set_background(level_data["background"])

        # สร้าง Obstacle
        for obj in level_data["obstacles"]:
            if obj["type"] == "spike":
                obstacle = Spike()
            elif obj["type"] == "boost_pad":
                obstacle = BoostPad()

            obstacle.x = obj["x"]
            obstacle.y = self.ids.ground1.top
            self.add_widget(obstacle)

        # ตั้งค่าเส้นชัย
        self.finish_line = FinishLine()
        self.finish_line.x = level_data["finish_line"]
        self.finish_line.y = self.ids.ground1.top
        self.add_widget(self.finish_line)

    def on_enter(self):
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        Window.bind(on_key_down=self.on_key_down)

    def on_leave(self):
        Clock.unschedule(self.update)
        Window.unbind(on_key_down=self.on_key_down)

    def update(self, dt):
        self.ids.player.update(
            [self.ids.ground1, self.ids.ground2],
            self.finish_line
        )

    def on_key_down(self, window, key, *args):
        if key == 32:  # Spacebar
            self.ids.player.jump()

    def game_over(self):
        self.show_game_over_popup()

    def show_game_over_popup(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='Game Over!', font_size='24sp'))
        
        button_layout = BoxLayout(orientation='horizontal', spacing=10)
        reset_button = Button(text='Play Again', font_size='20sp')
        home_button = Button(text='Back to Home', font_size='20sp')
        
        button_layout.add_widget(reset_button)
        button_layout.add_widget(home_button)
        layout.add_widget(button_layout)
        
        popup = Popup(title='Game Over', content=layout, size_hint=(0.5, 0.5), auto_dismiss=False)
        
        reset_button.bind(on_release=lambda instance: self.reset_game(instance, popup))
        home_button.bind(on_release=lambda instance: self.go_to_menu(instance, popup))
        
        popup.open()

    def reset_game(self, instance, popup):
        popup.dismiss()
        self.ids.player.reset_position()

    def level_complete(self):
        self.manager.current = 'stage_selection'
