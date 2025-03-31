from PokeDB import PokeDB
import PokeSpecies

import random
import time

database = PokeDB(1200)

mon_list = []

print("pulling new mon data...")
for i in range(5):
    num = random.randint(1, 386)
    print(num, end=" ")
    mon_list.append(PokeSpecies.generate_mon(num, "emerald", database))
    print(mon_list[i].name)
mon_list.append(PokeSpecies.generate_mon(263, "emerald", database))

print("")
time.sleep(2)

print("Generating movesets")
team = []
for mon in mon_list[:-1]:
    team.append((mon.name, mon.get_moveset(55, True)))
team.append((mon_list[-1].name, mon_list[-1].get_moveset(1, True)))

for i in team:
    print(i[0], end=" ")
    for move in i[1][:-1]:
        print(move.name, end=" ")
    print(i[1][-1].name)
