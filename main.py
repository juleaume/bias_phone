import random

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from architecture import settings_buttons, menu_buttons, buttons_names
from constants import *
from game import Game

SMALL_HEIGHT = 40
MEDIUM_HEIGHT = 60
LARGE_HEIGHT = 80


def name_factory(order):
    def name():
        return order

    return name()


class BiasScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(BiasScreenManager, self).__init__(**kwargs)
        self.game = Game(
            judgements=["Ecoute", "Bienveillance"]
        )
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
            buttons=menu_buttons,
            name="menu"
        )
        self.setting_screen = _ButtonScreen(
            buttons=settings_buttons,
            name='settings')
        self.judgement_settings = JudgementScreen(self.game, name="Judgements")
        self.judgement_settings.back_button.on_press = \
            lambda: self.switch_to_settings("right")
        self.game_screen = GameInitScreen(self.game, name="game_init")
        self.game_screen.back_button.on_press = self.switch_to_menu

        self.menu_screen.buttons[EXIT].on_press = exit
        self.menu_screen.buttons[EXIT].height = LARGE_HEIGHT
        self.menu_screen.buttons[EXIT].size_hint_y = None
        self.menu_screen.buttons[SETTINGS].on_press = self.switch_to_settings
        self.menu_screen.buttons[GAME].on_press = self.switch_to_game
        self.setting_screen.buttons[BACK].on_press = self.switch_to_menu
        self.setting_screen.buttons[BACK].height = LARGE_HEIGHT
        self.setting_screen.buttons[BACK].size_hint_y = None
        self.setting_screen.buttons[
            JUDGEMENTS].on_press = self.switch_to_judgements_settings

        self.add_widget(self.menu_screen)
        self.add_widget(self.setting_screen)
        self.add_widget(self.game_screen)
        self.add_widget(self.judgement_settings)

    def switch_to_settings(self, direction="left"):
        self.transition.direction = direction
        self.switch_to(self.setting_screen)

    def switch_to_menu(self):
        self.transition.direction = "right"
        self.switch_to(self.menu_screen)

    def switch_to_game(self):
        self.transition.direction = "left"
        self.switch_to(self.game_screen)

    def switch_to_judgements_settings(self):
        self.transition.direction = "left"
        self.switch_to(self.judgement_settings)

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
            _button = Button(text=buttons_names.get(b, ""))
            self.layout.add_widget(_button)
            self.buttons[b] = _button


class GameInitScreen(Screen):
    def __init__(self, game: Game, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(Label(
            text="Joueurs et joueuses", height=LARGE_HEIGHT, size_hint_y=None
        ))
        add_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=MEDIUM_HEIGHT
        )
        self.new_player = TextInput(
            text='', multiline=False, size_hint_y=None, height=MEDIUM_HEIGHT
        )
        add_button = Button(
            text="Ajouter", size_hint_y=None, height=MEDIUM_HEIGHT
        )
        add_button.on_press = self.add_player_to_game
        add_layout.add_widget(self.new_player)
        add_layout.add_widget(add_button)
        layout.add_widget(add_layout)
        self.scroll_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        self.scroll_layout.bind(
            minimum_height=self.scroll_layout.setter('height')
        )
        scroll_view = ScrollView()
        scroll_view.add_widget(self.scroll_layout)
        layout.add_widget(scroll_view)
        self.start_button = Button(
            text="Démarrer !", height=LARGE_HEIGHT, size_hint_y=None
        )
        self.start_button.disabled = True
        layout.add_widget(self.start_button)
        self.back_button = Button(
            text="Retour", height=MEDIUM_HEIGHT, size_hint_y=None
        )
        layout.add_widget(self.back_button)
        self.add_widget(layout)

        self.display_players()

    def display_players(self):
        self.scroll_layout.clear_widgets()
        for player in self.game.players:
            _l = BoxLayout(
                orientation="horizontal", size_hint_y=None, height=SMALL_HEIGHT
            )
            _l.add_widget(Label(
                text=player, size_hint_y=None, height=SMALL_HEIGHT
            ))
            _b = Button(
                text="Supprimer", size_hint_y=None, height=SMALL_HEIGHT,
                width=100, size_hint_x=None, on_press=lambda x:
                self.remove_player(player)
            )
            _l.add_widget(_b)
            self.scroll_layout.add_widget(_l)
        self.start_button.disabled = self.game.player_number <= 1

    def add_player_to_game(self):
        self.game.add_player(self.new_player.text)
        self.new_player.text = ""
        self.display_players()

    def remove_player(self, player):
        self.game.remove_player(player)
        self.display_players()


class JudgementScreen(Screen):
    def __init__(self, game: Game, **kwargs):
        super(JudgementScreen, self).__init__(**kwargs)
        self.game = game
        layout = BoxLayout(orientation="vertical")
        add_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=MEDIUM_HEIGHT
        )
        self.new_judgement = TextInput(
            text='', multiline=False, size_hint_y=None, height=MEDIUM_HEIGHT
        )
        add_button = Button(
            text="Ajouter", size_hint_y=None, height=MEDIUM_HEIGHT
        )
        add_button.on_press = self.add_judgement_to_game
        add_layout.add_widget(self.new_judgement)
        add_layout.add_widget(add_button)
        layout.add_widget(add_layout)
        self.scroll_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        self.scroll_layout.bind(
            minimum_height=self.scroll_layout.setter('height')
        )
        self.display_judgements()
        scroll_view = ScrollView()
        scroll_view.add_widget(self.scroll_layout)
        layout.add_widget(scroll_view)
        self.back_button = Button(
            text="Retour", height=MEDIUM_HEIGHT, size_hint_y=None
        )
        layout.add_widget(self.back_button)
        self.add_widget(layout)

    def display_judgements(self):
        self.scroll_layout.clear_widgets()
        for judgement in self.game.judgements:
            _l = BoxLayout(
                orientation="horizontal", size_hint_y=None, height=SMALL_HEIGHT
            )
            _l.add_widget(Label(
                text=judgement, size_hint_y=None, height=SMALL_HEIGHT
            ))
            _b = Button(
                text="Supprimer", size_hint_y=None, height=SMALL_HEIGHT,
                width=100, size_hint_x=None, on_press=lambda x:
                self.remove_judgement(judgement)
            )
            _l.add_widget(_b)
            self.scroll_layout.add_widget(_l)

    def add_judgement_to_game(self):
        self.game.add_judgement(self.new_judgement.text)
        self.new_judgement.text = ""
        self.display_judgements()

    def remove_judgement(self, judgement):
        self.game.remove_judgement(judgement)
        self.display_judgements()


class BiasApp(App):
    def build(self):
        return BiasScreenManager()


if __name__ == '__main__':
    BiasApp().run()
