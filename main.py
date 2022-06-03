import random

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen


def name_factory(order):
    def name():
        return order

    return name()


class BiasScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(BiasScreenManager, self).__init__(**kwargs)
        self._setup_screens()

    def _setup_screens(self):
        def make_screen(_screen: Screen):
            layout = BoxLayout(orientation="vertical")
            layout.add_widget(Label(text=screen.name))
            layout.add_widget(
                Button(
                    text="Back to settings",
                    on_press=self.switch_to_settings
                )
            )
            _screen.add_widget(layout)

        self._screens = [
            Screen(name=name_factory(f"Screen {i}")) for i in range(4)
        ]
        for screen in self._screens:
            make_screen(screen)
        self.menu_screen = _ButtonScreen(
            buttons=["Partie locale", "Paramètres", "Quitter"],
            name="menu"
        )
        self.setting_screen = _ButtonScreen(
            buttons=["Jugements", "Retour"],
            name='settings')
        self.menu_screen.buttons["Quitter"].on_press = exit
        self.menu_screen.buttons["Paramètres"].on_press = \
            self.switch_to_settings
        self.setting_screen.buttons["Retour"].on_press = self.switch_to_menu
        self.setting_screen.buttons["Jugements"].on_press = self.switch_to_rnd
        self.add_widget(self.menu_screen)
        self.add_widget(self.setting_screen)

    def switch_to_settings(self, *args):
        self.transition.direction = "left" if len(args) == 0 \
            else "down"
        self.switch_to(self.setting_screen)

    def switch_to_menu(self):
        self.transition.direction = "right"
        self.switch_to(self.menu_screen)

    def switch_to_rnd(self):
        self.transition.direction = "up"
        screen = random.choice(self._screens)
        self.switch_to(screen)


class _ButtonScreen(Screen):
    def __init__(self, buttons, **kwargs):
        super(_ButtonScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical")
        self.add_widget(self.layout)
        self.buttons = dict()
        self.make_buttons(buttons)

    def make_buttons(self, buttons):
        for b in buttons:
            _button = Button(text=b)
            self.layout.add_widget(_button)
            self.buttons[b] = _button


class BiasApp(App):
    def build(self):
        return BiasScreenManager()


if __name__ == '__main__':
    BiasApp().run()
