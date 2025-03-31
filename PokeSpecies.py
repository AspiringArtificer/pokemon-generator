from PokeDB import PokeDB

import random
import json


class PokeMove:
    def __init__(self, name: str, level: int = 0, order: int = 0):
        self.name = name
        self.level = level
        self.order = order

    def __str__(self):
        return f"PokeMove object: name={self.name}, level={self.level}, order={self.order}"

    def __repr__(self):
        return f"PokeMove({self.name}, {self.level}, {self.order})"

    def __lt__(self, other):
        if self.level == other.level:
            return self.order < other.order
        return self.level < other.level


class PokeSpecies:
    def __init__(self, name: str = "", id: int = 0, version: str = ""):
        self.name = name
        self.id = id
        self.version = version
        self.maxlevel = 100
        self.learnset = []
        self.prevolutions = []

    def __str__(self):
        return f"PokeSpecies object: name={self.name}, id={self.id}, game={self.version}"

    def __repr__(self):
        return f"PokeSpecies({self.name}, {self.id}, {self.version}, {self.maxlevel})"

    def build_learnset(self, db: PokeDB):
        for prevo in self.prevolutions:
            prevo.build_learnset(db)

        version_group = db.get_poke_api(
            "version/" + self.version)["version_group"]["name"]
        l_set = db.get_learnset(str(self.id), version_group)
        for set in l_set:
            set_order = set["details"]["order"] if set["details"]["order"] is not None else 0
            self.learnset.append(
                PokeMove(set["move"]["name"], set["details"]["level_learned_at"], set_order))
        self.learnset.sort()
        return

    def get_evos(self, db: PokeDB):
        evos = list(reversed(self.prevolutions))
        evos.append(self)
        e_iter = iter(evos)
        species = db.get_species(str(self.id))
        evo_chain = db.get_poke_api(
            species["evolution_chain"]["url"][:-1])["chain"]
        for _ in range(len(evos)):
            evo = next(e_iter)
            try:
                next_evo = next(e_iter)
                # make sure root is valid
                if evo_chain["species"]["name"] != evo.name:
                    print("Unexpected evo species",
                          evo_chain["species"]["name"])
                    return

                for mon in evo_chain["evolves_to"]:
                    if mon["species"]["name"] == next_evo.name:
                        for detail in mon["evolution_details"]:
                            if detail["trigger"]["name"] == "level-up":
                                min_level = detail["min_level"]
                                if min_level:
                                    evo.maxlevel = min_level
                                break
                        evo_chain = mon
                        break

                e_iter = iter(evos[evos.index(next_evo):])
            except StopIteration:
                return
        return

    def get_moveset(self, level: int, allow_skips: bool = True, moveset=None):
        for prevo in reversed(self.prevolutions):
            moveset = prevo.get_moveset(level, allow_skips, moveset)
        for move in self.learnset:
            if move.level <= level:
                if not moveset:
                    moveset = [move]
                elif len(moveset) < 4:
                    moveset.append(move)
                else:
                    new_move = True
                    for m in moveset:
                        if m.name == move.name:
                            new_move = False
                    if new_move:
                        index = random.randint(
                            0, 4) if allow_skips else random.randint(0, 3)
                        if index < 4:
                            moveset[index] = move
        return moveset


def check_mon_exists(pokemon, version: str):
    p_versions = pokemon["game_indices"]
    for pv in p_versions:
        if pv["version"]["name"] == version:
            return True
    return False


def generate_mon(id: int, version: str, db: PokeDB):
    species = db.get_species(str(id))
    if not species:
        print(f"Pokemon id={id} doesn't exist")
        return
    p_mon = db.get_pokemon(str(id))

    if not check_mon_exists(p_mon, version):
        print(f"Pokemon id={id} doesn't exist in {version}")
        return None

    mon = PokeSpecies(species["name"], id, version)

    while species["evolves_from_species"]:
        species = db.get_poke_api(species["evolves_from_species"]["url"][:-1])
        p_mon = db.get_pokemon(str(species["id"]))
        if not check_mon_exists(p_mon, version):
            break
        mon.prevolutions.append(PokeSpecies(
            species["name"], species["id"], version))

    mon.build_learnset(db)
    mon.get_evos(db)

    return mon
