import flet

from flet import UserControl, Column, Row, Page, Text, Image
from flet.dropdown import Dropdown, Option as DropdownOption

from client.client import FPLApiClient


class FPLApp(UserControl):
    MANAGERS = {
        5809911: "joel",
        5796718: "alex",
        5796815: "rob",
        5797202: "danny",
        5797354: "michael",
        5797489: "andy",
        5798350: "james",
        5009655: "jake",
    }
    POSITIONS = {
        1: "goalkeepers",
        2: "defenders",
        3: "midfielders",
        4: "forwards",
    }

    def __init__(self):
        super().__init__()
        self.client = FPLApiClient()
        self.bootstrap_data = self.client.get_bootstrap_data()
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
        """
        Build an index of every selected player element ID to manager e.g.
        {
            10: "michael",
            22: "michael",
            33: "joel",
            48: "alex",
            51: "joel",
            ....
        }
        """
        if self.current_picks:
            return

        for manager_id, name in self.MANAGERS.items():
            picks = self.client.get_manager_picks(manager_id=manager_id, gameweek=self.current_gameweek_number)

            if not picks or picks["active_chip"] == "freehit":
                # use previous gameweek if no picks for current gameweek
                picks = self.client.get_manager_picks(manager_id=manager_id, gameweek=self.previous_gameweek_number)

            picks = picks["picks"]
            self.current_picks.update({pick["element"]: name for pick in picks})

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
        self.unavailable.visible = False
        self.available.visible = False
        team_code = self.team_dropdown.value
        self.player_dropdown.options = self.player_options(team_code=team_code)
        self.player_dropdown.visible = True
        self.update()

    def change_player(self, e):
        self.unavailable.visible = False
        player_code, player_name = self.player_dropdown.value.split("__")
        self.selected.value = f"{player_name} is available for transfer, fill yer boots"
        self.available.visible = True

        owner = self.current_picks.get(int(player_code))
        if owner:
            self.unavailable.visible = True
            self.available.visible = False
            self.selected.value = f"UNLUCKEEEEE!\n{owner.title()} owns {player_name}"

        self.update()

    def build(self):
        self.selected = Text(style="bodyLarge", text_align="center")
        self.unavailable = Image(
            src="/images/unavailable.jpg",
            width=300,
            fit="contain",
            visible=False
        )
        self.available = Image(
            src="/images/available.jpeg",
            width=300,
            fit="contain",
            visible=False
        )

        return Column(
            width=300,
            spacing=25,
            horizontal_alignment="center",
            controls=[
                Row(
                    wrap=True,
                    alignment="center",
                    controls=[
                        Text(value="Does anyone have him?", style="titleLarge", color="black"),
                        Text(
                            value="A player availability checker for the Nicola Pépé FPL 22/23",
                            style="titleSmall",
                            color="black",
                            text_align="center",
                        ),
                    ],
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
                    wrap=True,
                    alignment="center",
                    controls=[
                        self.unavailable,
                        self.available,
                        self.selected,
                    ]
                ),
            ]
        )


def main(page: Page):
    page.title = "The Nicolas Pépé FPL 22/23 player checker"
    page.horizontal_alignment = "center"
    page.update()

    fpl_app = FPLApp()
    page.add(fpl_app)


flet.app(target=main, assets_dir="assets", view=flet.WEB_BROWSER, port=8000)
