from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.utils import platform

from architecture import settings_buttons, menu_buttons, buttons_names
from constants import *
from game import Game

SMALL_HEIGHT = 75 if platform == 'android' else 40
MEDIUM_HEIGHT = 150 if platform == 'android' else 60
LARGE_HEIGHT = 250 if platform == 'android' else 80

SMALL_WIDTH = 250 if platform == 'android' else 100
MEDIUM_WIDTH = 500 if platform == 'android' else 200
LARGE_WIDTH = 750 if platform == 'android' else 300


def name_factory(order):
    def name():
        return order

    return name()


class BiasScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(BiasScreenManager, self).__init__(**kwargs)
        self.game = Game(
            players=["Louis", "Théo", "Jules"],
            jury=["Louis", "Jules"],
            judgements=["Ecoute", "Bienveillance"]
        )
        self.order_screens = list()
        self._setup_screens()

    def _setup_screens(self):
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
        self.game_screen.start_button.on_press = self.init_game

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

    def init_game(self):
        self.game.set()
        for judgement in self.game.judgements:
            for player in self.game.players:
                for jury in self.game.jury:
                    prep_screen = PlayerPrepScreen(
                        self, jury, name=jury
                    )
                    self.order_screens.append(prep_screen)
                    self.add_widget(prep_screen)
                    judgement_screen = VotingScreen(
                        self, self.game, player, judgement,
                        name=f"{jury}_vote_{judgement}_for_{player}")
                    self.order_screens.append(judgement_screen)
                    self.add_widget(judgement_screen)
                transition_screen = SummaryScreen(
                    self, self.game, player, judgement,
                    name=f"score_{player}_{judgement}"
                )
                self.order_screens.append(transition_screen)
                self.add_widget(transition_screen)
        end_screen = EndScreen(self, self.game, name="endscreen")
        end_screen.ok_button.on_press = self.switch_to_menu
        self.add_widget(end_screen)
        self.order_screens.append(end_screen)
        for screen, next_screen in zip(self.order_screens[:-1],
                                       self.order_screens[1:]):
            screen.set_next_screen(next_screen)

        self.switch_to(self.order_screens[0])


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


class GameScreen(Screen):
    def __init__(self, screen_manager: ScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.next_screen = None

    def set_next_screen(self, next_screen: Screen):
        self.next_screen = next_screen

    def switch_to_next(self):
        if isinstance(self.next_screen, Screen):
            self.screen_manager.switch_to(self.next_screen)
            if hasattr(self.next_screen, "set_text"):
                self.next_screen.set_text()


class PlayerPrepScreen(GameScreen):
    def __init__(self, screen_manager, jury, **kwargs):
        super().__init__(screen_manager, **kwargs)
        layout = BoxLayout(orientation="vertical")
        label = Label(text=f"C'est le tour de {jury} !")
        layout.add_widget(label)
        ok_button = Button(text="ok", height=LARGE_HEIGHT, size_hint_y=None)
        ok_button.on_press = self.switch_to_next
        layout.add_widget(ok_button)
        self.add_widget(layout)


class VotingScreen(GameScreen):
    def __init__(self, screen_manager, game: Game, player: str, judgement:
    str, **kwargs):
        super().__init__(screen_manager, **kwargs)
        self.game = game
        self.player = player
        self.judgement = judgement
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(Label(
            text=f"{judgement.upper()} pour {player.upper()}",
            height=LARGE_HEIGHT, size_hint_y=None,
        ))
        ten_button = Button(text="10", height=LARGE_HEIGHT, size_hint_y=None)
        ten_button.on_press = lambda: self.vote(ten_button)
        layout.add_widget(ten_button)
        grid_layout = GridLayout(cols=3, size_hint_y=None)
        grid_layout.bind(minimum_height=grid_layout.setter('height'))

        for i in range(9, 0, -1):
            btn = Button(
                text=str(i), size_hint_y=None, height=LARGE_HEIGHT,
                on_press=lambda x: self.vote(int(x.text))
            )
            grid_layout.add_widget(btn)
        layout.add_widget(grid_layout)
        zero_button = Button(text="0", height=LARGE_HEIGHT, size_hint_y=None)
        zero_button.on_press = lambda: self.vote(zero_button)
        layout.add_widget(zero_button)
        self.add_widget(layout)

    def vote(self, button: int):
        self.game.judge(self.player, self.judgement, button)
        self.switch_to_next()


class SummaryScreen(GameScreen):
    def __init__(self, screen_manager, game: Game, player: str, judgement:
    str, **kwargs):
        super(SummaryScreen, self).__init__(screen_manager, **kwargs)
        self.game = game
        self.player = player
        self.judgement = judgement
        layout = BoxLayout(orientation="vertical")
        self.score_label = Label()
        layout.add_widget(self.score_label)
        self.add_widget(layout)

        ok_button = Button(text="ok", height=LARGE_HEIGHT, size_hint_y=None)
        ok_button.on_press = self.switch_to_next
        layout.add_widget(ok_button)

    def set_text(self):
        score = self.game.summarize_turn(self.player, self.judgement)
        self.score_label.text = \
            f"{self.player.upper()} a pour le trait\n" \
            f"{self.judgement} un score moyen de\n" \
            f"{score:.2f}"


class EndScreen(GameScreen):
    def __init__(self, screen_manager, game: Game, **kwargs):
        super(EndScreen, self).__init__(screen_manager, **kwargs)
        self.game = game
        layout = BoxLayout(orientation="vertical")
        self.label = Label()
        layout.add_widget(self.label)

        self.ok_button = Button(
            text="Retour", height=MEDIUM_HEIGHT, size_hint_y=None
        )
        layout.add_widget(self.ok_button)
        self.add_widget(layout)

    def set_text(self):
        final_score = self.game.finish_game()
        best_player = ""
        best_score = 0
        worst_player = ""
        worst_score = float('inf')
        for quick_pass in range(2):
            for player, score in final_score.items():
                if score > best_score:
                    best_player = player
                    best_score = score
                elif score < worst_score:
                    worst_player = player
                    worst_score = score
        others = ""
        for player, score in final_score.items():
            others += f"{player}: {score}\n"
        self.label.text = \
            f"Le meilleur être humain est {best_player.upper()}\n" \
            f"avec un score de {best_score}\n" \
            f"le pire est {worst_player.upper()}\n" \
            f"avec un score de {worst_score}.\n\n" \
            f"les scores finaux sont :\n" \
            f"{others}"


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
            text="Ajouter", size_hint=(None, None), height=MEDIUM_HEIGHT,
            width=MEDIUM_WIDTH
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
                width=SMALL_WIDTH, size_hint_x=None, on_press=lambda x:
                self.remove_player(player)
            )
            _l.add_widget(_b)
            self.scroll_layout.add_widget(_l)
        self.start_button.disabled = not self.game.can_start

    def add_player_to_game(self):
        self.game.add_player(self.new_player.text)
        self.game.add_jury(self.new_player.text)
        self.new_player.text = ""
        self.display_players()

    def remove_player(self, player):
        self.game.remove_player(player)
        self.game.remove_jury(player)
        self.display_players()


class JudgementScreen(Screen):
    def __init__(self, game: Game, **kwargs):
        super(JudgementScreen, self).__init__(**kwargs)
        self.game = game
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(Label(
            text="Jugements", height=LARGE_HEIGHT, size_hint_y=None
        ))
        add_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=MEDIUM_HEIGHT
        )
        self.new_judgement = TextInput(
            text='', multiline=False, size_hint_y=None, height=MEDIUM_HEIGHT
        )
        add_button = Button(
            text="Ajouter", size_hint=(None, None), height=MEDIUM_HEIGHT,
            width=MEDIUM_WIDTH
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
                width=SMALL_WIDTH, size_hint_x=None, on_press=lambda x:
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
