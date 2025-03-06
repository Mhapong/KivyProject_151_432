from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class HomePage(Screen):
    def __init__(self, **kwargs):
        super(HomePage, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=20, padding=50)
        
        title = Label(
            text='GeoDash',
            font_size='48sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.2),
            halign='center'
        )
        
        button = Button(
            text='Go to Play ➡️',
            size_hint=(0.3, 0.1),
            pos_hint={'center_x': 0.5},
            font_size='24sp'
        )
        button.bind(on_press=self.go_to_level_selection)
        
        layout.add_widget(title)
        layout.add_widget(button)
        self.add_widget(layout)

    def go_to_level_selection(self, instance):
        self.manager.current = 'stage_selection'
