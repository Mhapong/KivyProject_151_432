from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class HomePage(Screen):
    def __init__(self, **kwargs):
        super(HomePage, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=20, padding=50)
        self.add_widget(layout)

        label = Label(text='GeoDash Tee Barn', font_size='48sp', bold=True, color=(1, 1, 1, 1), size_hint_y=0.2)
        layout.add_widget(label)

        play_button = Button(text='Go to Play ➡️', size_hint=(0.3, 0.1), pos_hint={'center_x': 0.5}, font_size='24sp')
        play_button.bind(on_press=self.go_to_level_selection)
        layout.add_widget(play_button)

        settings_button = Button(text='Settings', size_hint=(0.3, 0.1), pos_hint={'center_x': 0.5}, font_size='24sp')
        settings_button.bind(on_press=self.go_to_settings)
        layout.add_widget(settings_button)

    def go_to_level_selection(self, instance):
        self.manager.current = 'stage_selection'

    def go_to_settings(self, instance):
        print("Settings button pressed")
