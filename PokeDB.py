import requests
import json
import os
import shutil
import re
from collections import deque
import glob


class PokeDB:
    POKE_API_URL = "https://pokeapi.co/api/v2/"
    LOCAL_DB_BASE = "poke_api/"

    def __init__(self, size: int = 5):
        self.base_url: str = self.POKE_API_URL
        self.local_path: str = self.LOCAL_DB_BASE
        self.file_q = deque(maxlen=size)
        for file in glob.iglob(self.local_path+"**/*.json", recursive=True):
            self.add_file(file)

    def add_file(self, file: str):
        if len(self.file_q) == self.file_q.maxlen:
            os.remove(self.file_q.pop())
        self.file_q.append(file)

    def clear(self):
        while self.file_q:
            os.remove(self.file_q.pop())

    def dist_clear(self):
        if os.path.exists(self.local_path):
            shutil.rmtree(self.local_path, ignore_errors=False)
        self.file_q.clear()

    def get_poke_api(self, path: str = ""):
        url = ""
        if re.search(self.base_url, path):
            url = path
            path = path.replace(self.base_url, "")
        else:
            url = self.base_url + path

        data_file = self.local_path + path + ".json"
        if os.path.exists(data_file):
            with open(data_file, "r") as file:
                return json.load(file)

        try:
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            os.makedirs(os.path.dirname(data_file), exist_ok=True)
            with open(data_file, "w") as file:
                json.dump(data, file, indent=4)
            self.add_file(data_file)

            return data

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def get_pokemon(self, pokemon: str):
        pokemon_path = "pokemon/" + pokemon
        return self.get_poke_api(pokemon_path)

    def get_species(self, species: str):
        species_path = "pokemon-species/" + species
        return self.get_poke_api(species_path)

    def get_learnset(self, pokemon: str, version_group: str):
        learnset = []
        moves = self.get_pokemon(pokemon)["moves"]
        for move in moves:
            for detail in move["version_group_details"]:
                if detail["move_learn_method"]["name"] == "level-up":
                    if detail["version_group"]["name"] == version_group:
                        learnset.append(
                            {"move": move["move"], "details": detail})
        return learnset
