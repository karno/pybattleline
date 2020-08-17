from src import game


def test_troops_deck_len():
    assert len(game.TroopsDeck()) == 60


def test_tactics_deck_len():
    assert len(game.TacticsDeck()) == 10
