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


class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(MyScreenManager, self).__init__(**kwargs)
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
        self.menu_screen = MenuScreen(name="menu")
        self.setting_screen = SettingsScreen(name='settings')
        self.menu_screen.exit_button.on_press = exit
        self.menu_screen.setting_button.on_press = self.switch_to_settings
        self.setting_screen.menu_button.on_press = self.switch_to_menu
        self.setting_screen.setting_button.on_press = self.switch_to_rnd
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


# Declare both screens
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout()
        self.add_widget(self.layout)
        self.setting_button = Button(text="Settings")
        self.layout.add_widget(self.setting_button)

        self.exit_button = Button(text="Quit")
        self.layout.add_widget(self.exit_button)


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout()
        self.add_widget(self.layout)
        self.setting_button = Button(text="Go to...")
        self.layout.add_widget(self.setting_button)

        self.menu_button = Button(text="Back to menu")
        self.layout.add_widget(self.menu_button)


class TestApp(App):

    def build(self):
        # Create the screen manager
        return MyScreenManager()


if __name__ == '__main__':
    TestApp().run()
