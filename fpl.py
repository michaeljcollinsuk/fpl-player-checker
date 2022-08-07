import requests
import flet

from flet import UserControl, Column, Row, Page, Text
from flet.dropdown import Dropdown, Option as DropdownOption

FPL_API_BASE = f"https://fantasy.premierleague.com/api/"


class FPLApp(UserControl):

    def __init__(self):
        super().__init__()
        self.bootstrap_data = requests.get(f"{FPL_API_BASE}bootstrap-static/").json()
        self.team_dropdown = Dropdown(
            on_change=self.change_team,
            width=200,
            options=self.team_options()
        )
        self.player_dropdown = Dropdown(
            on_change=self.change_player,
            width=200,
            visible=False
        )

    def teams(self):
        return [(team["code"], team["name"]) for team in self.bootstrap_data["teams"]]

    def all_players(self):
        return self.bootstrap_data["elements"]

    def players_for_team(self, team_code):
        team_code = int(team_code)
        return [
            {
                # "first_name": player["first_name"],
                # "second_name": player.second_name,
                "web_name": player["web_name"],
                "team_code": player["team_code"],
                "id": player["id"],
                # "code": player["code"],
            } for player in self.all_players() if player["team_code"] == team_code
        ]

    def team_options(self):
        return [DropdownOption(key=team[0], text=team[1]) for team in self.teams()]

    def player_options(self, team_code):
        players = self.players_for_team(team_code=team_code)
        return [DropdownOption(key=player["id"], text=player["web_name"]) for player in players]

    def change_team(self, e):
        team_code = self.team_dropdown.value
        self.player_dropdown.options = self.player_options(team_code=team_code)
        self.player_dropdown.visible = True
        self.update()

    def change_player(self, e):
        player_code = self.player_dropdown.value
        self.selected.value = f"Selected player with code {player_code}"
        self.update()

    def build(self):
        self.selected = Text()
        return Column(
            width=600,
            controls=[
                Row(
                    controls=[
                        self.team_dropdown,
                    ]
                ),
                Row(
                    controls=[
                        self.player_dropdown,
                    ]
                ),
                Row(
                    controls=[
                        self.selected,
                    ]
                )

            ]
        )


def main(page: Page):
    page.title = "FPL player checker app"
    page.horizontal_alignment = "center"
    page.update()

    fpl_app = FPLApp()
    page.add(fpl_app)

flet.app(target=main, view=flet.WEB_BROWSER, port=8000)
