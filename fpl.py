from time import sleep
import requests
import flet

from flet import UserControl, Column, Row, Page, Text
from flet.dropdown import Dropdown, Option as DropdownOption


class FPLApp(UserControl):
    MANAGERS = {
        "jd": 5809911,
        "ab": 5796718,
        "rp": 5796815,
        "db": 5797202,
        "mc": 5797354,
        "ap": 5797489,
        "jw": 5798350,
        "jm": 5009655,
    }
    API_BASE = f"https://fantasy.premierleague.com/api/"

    def __init__(self):
        super().__init__()
        self.bootstrap_data = requests.get(f"{self.API_BASE}bootstrap-static/").json()
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
        self.gameweek_numbers = {}
        self.current_picks = {}
        self.setup_data()

    def setup_data(self):
        self._build_gameweek_numbers()
        self._build_current_picks()

    def _build_gameweek_numbers(self):
        if self.gameweek_numbers:
            return

        gws = {
            "previous": None,
            "current": None,
            "next": None
        }
        for gw in self.bootstrap_data["events"]:         
            if gw["is_previous"]:
                gws["previous"] = gw["id"]

            if gw["is_current"]:
                gws["current"] = gw["id"]

            if gw["is_next"]:
                gws["next"] = gw["id"]

        self.gameweek_numbers = gws

    def _build_current_picks(self):
        if self.current_picks:
            return

        picks = {}
        use_previous_gw = None
        for manager, id in self.MANAGERS.items():
            # try current GW picks first
            data = None
            if not use_previous_gw == True:
                url = f"{self.API_BASE}/entry/{id}/event/{self.current_gameweek_number}/picks/"
                response = requests.get(url=url)
                if response.ok:
                    data = response.json()
                else:
                    use_previous_gw = True

            # if we dont have current gw data use previous
            if not data:
                url = f"{self.API_BASE}/entry/{id}/event/{self.previous_gameweek_number}/picks/"
                response = requests.get(url=url)
                data = response.json()

            picks[manager] = [player["element"] for player in data["picks"]]

        self.current_picks = picks

    @property
    def current_gameweek_number(self):
        return self.gameweek_numbers["current"]

    @property
    def previous_gameweek_number(self):
        self.gameweek_numbers["previous"]

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
        self.selected.value = ""
        team_code = self.team_dropdown.value
        self.player_dropdown.options = self.player_options(team_code=team_code)
        self.player_dropdown.visible = True
        self.update()

    def change_player(self, e):
        player_code = self.player_dropdown.value
        self.selected.value = f"Selected player with code {player_code} is available"
        for manager, picks in self.current_picks.items():
            if int(player_code) in picks:
                self.selected.value = f"Not available, {manager} owns this player"
                break

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
