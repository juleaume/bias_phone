import random
from typing import Dict


class Game:
    def __init__(self, players=None, jury=None, judgements=None):
        self.is_set = False
        self._players = players if players is not None else list()
        self._jury = jury if jury is not None else list()
        self._judgements = judgements if judgements is not None else list()
        self._scores = dict()
        self._descriptions = dict()  # type: Dict[str: str]

    def set(self):
        random.shuffle(self._players)
        random.shuffle(self._judgements)
        self._scores = {
            p: {j: 0 for j in self.judgements} for p in self.players
        }  # type: Dict[Dict[str: int]]
        self.is_set = True

    @property
    def players(self):
        for player in self._players:
            yield player

    @property
    def player_number(self):
        return len(self._players)

    @property
    def jury(self):
        for jury in self._jury:
            yield jury

    @property
    def jury_number(self):
        return len(self._jury)

    @property
    def judgements(self):
        for judgement in self._judgements:
            yield judgement

    @property
    def judgment_number(self):
        return len(self._judgements)

    @property
    def scores(self):
        return self._scores

    def add_player(self, player):
        if not self.is_set:
            self._players.append(player)
        else:
            raise RuntimeError

    def add_players(self, *players):
        for player in players:
            self.add_player(player)

    def add_jury(self, jury):
        if not self.is_set:
            self._jury.append(jury)
        else:
            raise RuntimeError

    def add_juries(self, *juries):
        for jury in juries:
            self.add_jury(jury)

    def add_judgement(self, judgement):
        if not self.is_set:
            self._judgements.append(judgement)
        else:
            raise RuntimeError

    def remove_judgement(self, judgement):
        if not self.is_set:
            if judgement in self._judgements:
                self._judgements.remove(judgement)
            else:
                raise ValueError
        else:
            raise RuntimeError

    def add_judgements(self, *judgements):
        for judgement in judgements:
            self.add_judgement(judgement)

    def judge(self, player: str, judgement: str, vote: int):
        if not 0 <= vote <= 10:
            raise ValueError
        self._scores[player][judgement] += vote

    def summarize_turn(self, player, judgement):
        self._scores[player][judgement] /= len(self._jury)
        return self.scores.get(player).get(judgement)

    def finish_turn(self):
        random.shuffle(self._players)

    def finish_game(self):
        final_scores = {p: 0 for p in self.players}
        for player in self.players:
            for judgment in self.judgements:
                final_scores[player] += self.scores.get(player).get(judgment)
            final_scores[player] /= len(self._judgements)
        return final_scores


if __name__ == '__main__':
    game = Game(
        players=["Louis", "Theo", "Jules"],
        jury=["Louis", "Theo", "Jules"],
        judgements=["Bienveillance", "Ecoute", "Organisation"]
    )
    game.set()
    for _ju in game.judgements:
        for _pl in game.players:
            for _jr in game.jury:
                score = input(f"Vote {_ju} for {_pl} from {_jr}: ")
                game.judge(_pl, _ju, int(score))
            print(
                f"Score for {_pl} for {_ju}: "
                f"{game.summarize_turn(_pl, _ju):.2f}"
            )
        game.finish_turn()

    print(game.finish_game())

