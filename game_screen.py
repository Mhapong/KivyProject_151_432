import json
import random
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.clock import Clock
from game_logic import Player, FinishLine, Spike, BoostPad

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level_data = None

    def load_level(self, level_file):
        with open(level_file, 'r') as f:
            self.level_data = json.load(f)

    def on_enter(self):
        self.load_level("assets/levels/level1.json")
        self.setup_level()

    def setup_level(self):
        self.ids.player.pos = (100, 300)

        for obj in self.level_data["obstacles"]:
            if obj["type"] == "spike":
                spike = Spike(pos=(obj["x"], obj["y"]))
                self.add_widget(spike)

            elif obj["type"] == "boost_pad":
                boost = BoostPad(pos=(obj["x"], obj["y"]))
                self.add_widget(boost)

        self.finish_line = FinishLine(pos=(self.level_data["finish_x"], 100))
        self.add_widget(self.finish_line)

    def update(self, dt):
        self.ids.player.update([], [], self.finish_line, [])

    def on_leave(self):
        Clock.unschedule(self.update)
