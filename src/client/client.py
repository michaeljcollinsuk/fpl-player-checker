import requests


class FPLApiClient:
    API_BASE = f"https://fantasy.premierleague.com/api/"

    def get_bootstrap_data(self):
        return requests.get(f"{self.API_BASE}bootstrap-static/").json()

    def get_manager_picks(self, manager_id, gameweek):
        url = f"{self.API_BASE}/entry/{manager_id}/event/{gameweek}/picks/"
        response = requests.get(url=url)
        if not response.ok:
            return []
        return response.json()

    def get_manager_transfers(self, manager_id):
        url = f"{self.API_BASE}/entry/{manager_id}/transfers/"
        response = requests.get(url=url)
        if not response.ok:
            return []
        return response.json()

    def get_manager_history(self, manager_id):
        url = f"{self.API_BASE}/entry/{manager_id}/history/"
        response = requests.get(url=url)
        if not response.ok:
            return []
        return response.json()
