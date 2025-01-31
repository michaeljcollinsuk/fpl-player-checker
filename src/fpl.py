import flet

from flet import Column, Row, Page, Text, Image, Dropdown
from client.client import FPLApiClient


class FPLApp(Column):
    MANAGERS = {
        4679310: "joel",
        4680239: "alex",
        4680068: "rob",
        4679848: "danny",
        4679423: "michael",
        610713: "andy",
        4680327: "james",
        4609896: "jake",
    }
    POSITIONS = {
        1: "goalkeepers",
        2: "defenders",
        3: "midfielders",
        4: "forwards",
        5: "manager",
    }
    RUBBISH_ASSISTANTS = ["Mikel Arteta", "Ruben Filipe Marques Diogo Amorim", "Enzo Maresca", "Arne Slot"]

    def __init__(self):
        super().__init__(width=300, spacing=25, horizontal_alignment="center")
        self.client = FPLApiClient()
        self.bootstrap_data = self.client.get_bootstrap_data()
        self.gameweek_numbers = {}
        self.current_picks = {}
        self.setup_data()

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
        self.selected = Text(style="bodyLarge", text_align="center")
        self.unavailable = Image(
            src="/images/unavailable.jpg",
            width=300,
            fit="contain",
            visible=False,
        )
        self.available = Image(
            src="/images/available.jpeg",
            width=300,
            fit="contain",
            visible=False,
        )

        self.controls.extend([
            Row(
                wrap=True,
                alignment="center",
                controls=[
                    Text(value="Guinness Deep Fantasy Premier League 24/25", style="titleLarge", text_align="center"),
                    Text(value="Does anyone have him?", style="titleSmall", text_align="center"),
                ],
            ),
            Row(alignment="center", controls=[self.team_dropdown]),
            Row(alignment="center", controls=[self.player_dropdown]),
            Row(
                wrap=True,
                alignment="center",
                controls=[self.unavailable, self.available, self.selected],
            ),
        ])

    def setup_data(self):
        self._build_gameweek_numbers()
        self._build_current_picks()

    def _build_gameweek_numbers(self):
        if self.gameweek_numbers:
            return

        gws = {"previous": None, "current": None, "next": None}
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
            picks = self.get_latest_picks(manager_id=manager_id, gameweek=self.current_gameweek_number)["picks"]
            self.current_picks.update({pick["element"]: name for pick in picks})

    @property
    def current_gameweek_number(self):
        return self.gameweek_numbers["current"]

    def get_latest_picks(self, manager_id, gameweek):
        """
        Get latest valid picks. If picks are from using a freehit, they are invalid, so look at the previous week.
        """
        if not gameweek:
            return {"picks": {}}
        if gameweek <= 0 or gameweek >= 39:
            raise Exception("Invalid gameweek")

        picks = self.client.get_manager_picks(manager_id=manager_id, gameweek=gameweek)
        if not picks or picks["active_chip"] == "freehit":
            picks = self.get_latest_picks(manager_id, gameweek - 1)

        return picks

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
        return [flet.dropdown.Option(key=team[0], text=team[1]) for team in self.teams()]

    def player_options(self, team_code):
        players = self.players_for_team(team_code=team_code)
        position_code = 0
        options = []
        for player in players:
            if player["status"] == "u":
                continue
            if player["element_type"] != position_code:
                position_code = player["element_type"]
                try:
                    position_name = self.POSITIONS[position_code].upper()
                except KeyError:
                    continue
                heading = flet.dropdown.Option(text=f" {position_name} ".center(25, '-'), disabled=True)
                options.append(heading)

            full_name = f"{player['first_name']} {player['second_name']}"
            option = flet.dropdown.Option(key=f"{player['id']}__{full_name}__{position_code}", text=player["web_name"])
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
        player_code, player_name, position_code = self.player_dropdown.value.split("__")
        msg = f"{player_name} is available for transfer, fill yer boots"
        is_manager = position_code == "5"
        if is_manager:
            msg = f"{player_name} is available and willing to assist you."
            if player_name in self.RUBBISH_ASSISTANTS:
                msg = f"{msg} But come on, you can do better than this fraud..."
            else:
                msg = f"{msg} Sign him up quick!"
        self.selected.value = msg
        self.available.visible = True

        owner = self.current_picks.get(int(player_code))
        if owner:
            self.unavailable.visible = True
            self.available.visible = False
            selected_msg = f"UNLUCKEEEEE!\n{owner.title()} owns {player_name}"
            if is_manager:
                selected_msg = f"UNLUCKEEEEE!\n{player_name} is {owner.title()}'s assistant manager"
            self.selected.value = selected_msg

        self.update()


def main(page: Page):
    page.title = "The Guinness Deep FPL 24/25 player checker"
    page.horizontal_alignment = "center"

    page.fonts = {"guinness": "fonts/guinness.ttf"}
    theme = flet.Theme(font_family="guinness")
    page.theme = theme
    page.dark_theme = theme
    page.theme_mode = "dark"
    page.update()

    fpl_app = FPLApp()
    page.add(fpl_app)


flet.app(target=main, assets_dir="assets", view=flet.WEB_BROWSER, port=8000)
