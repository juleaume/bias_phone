from kivy.app import App
from kivy.uix.widget import Widget


class BiasGame(Widget):
    pass


class BiasApp(App):
    def build(self):
        return BiasGame()


if __name__ == '__main__':
    BiasApp().run()
