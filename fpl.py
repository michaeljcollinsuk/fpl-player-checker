import requests
import flet

from flet import UserControl, Column, Row, Page, Text
from flet.dropdown import Dropdown, Option as DropdownOption


class FPLApp(UserControl):
    MANAGERS = {
        "joel": 5809911,
        "alex": 5796718,
        "rob": 5796815,
        "danny": 5797202,
        "michael": 5797354,
        "andy": 5797489,
        "james": 5798350,
        "jake": 5009655,
    }
    API_BASE = f"https://fantasy.premierleague.com/api/"
    POSITIONS = {
        1: "goalkeepers",
        2: "defenders",
        3: "midfielders",
        4: "forwards",
    }

    def __init__(self):
        super().__init__()
        self.bootstrap_data = requests.get(f"{self.API_BASE}bootstrap-static/").json()
        self.team_dropdown = Dropdown(
            on_change=self.change_team,
            width=300,
            options=self.team_options(),
            hint_text="Select a team",
        )
        self.player_dropdown = Dropdown(
            on_change=self.change_player,
            width=300,
            visible=False,
            hint_text="Select a player",
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
        return self.gameweek_numbers["previous"]

    def teams(self):
        return [(team["code"], team["name"]) for team in self.bootstrap_data["teams"]]

    def all_players(self):
        return self.bootstrap_data["elements"]

    def players_for_team(self, team_code):
        team_code = int(team_code)
        players = [player for player in self.all_players() if player["team_code"] == team_code]
        players.sort(key=lambda obj: (obj["element_type"], obj["web_name"]))
        return players

    def team_options(self):
        return [DropdownOption(key=team[0], text=team[1]) for team in self.teams()]

    def player_options(self, team_code):
        players = self.players_for_team(team_code=team_code)
        position_code = 0
        options = []
        for player in players:

            if player["element_type"] != position_code:
                position_code = player["element_type"]
                position_name = self.POSITIONS[position_code].upper()
                heading = DropdownOption(text=f" {position_name} ".center(25, '-'), disabled=True)
                options.append(heading)

            full_name = f"{player['first_name']} {player['second_name']}"
            option = DropdownOption(key=f"{player['id']}__{full_name}", text=player["web_name"])
            options.append(option)

        return options

    def change_team(self, e):
        self.selected.value = ""
        team_code = self.team_dropdown.value
        self.player_dropdown.options = self.player_options(team_code=team_code)
        self.player_dropdown.visible = True
        self.update()

    def change_player(self, e):
        player_code, player_name = self.player_dropdown.value.split("__")
        self.selected.value = f"{player_name} is available, fill yer boots"
        for manager, picks in self.current_picks.items():
            if int(player_code) in picks:
                self.selected.value = f"UNLUCKEEE! {manager.title()} owns {player_name}"
                break

        self.update()

    def build(self):
        self.selected = Text(style="bodyLarge")
        return Column(
            width=600,
            spacing=25,
            horizontal_alignment="center",
            controls=[
                Row(
                    alignment="center",
                    controls=[
                        Text(value="Does anyone have him?", style="titleLarge", color="black")]
                    ,
                ),
                Row(
                    alignment="center",
                    controls=[
                        self.team_dropdown,
                    ]
                ),
                Row(
                    alignment="center",
                    controls=[
                        self.player_dropdown,
                    ]
                ),
                Row(
                    alignment="center",
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
