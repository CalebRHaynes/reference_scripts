import random
import numpy as np
import matplotlib.pyplot as plt

class Player:
    def __init__(self, name):
        self.name = name
        self.drops = {
            "Noxious_blade": 0,
            "Noxious_point": 0,
            "Noxious_pommel": 0,
            "Araxyte_fang": 0
        }
        self.u_drop_table = {
            "Noxious_blade": 3/4,
            "Noxious_point": 3/4,
            "Noxious_pommel": 3/4,
            "Araxyte_fang": 1/4
        }
        self.roll_table_chance = 1/150

    def roll_for_drop(self):
        if random.random() > self.roll_table_chance:
            return None
        possible = self.get_possible_drops()
        total_weight = sum(self.u_drop_table[item] for item in possible)
        roll = random.uniform(0, total_weight)
        cumulative = 0
        for drop in possible:
            cumulative += self.u_drop_table[drop]
            if roll <= cumulative:
                return drop

    def get_possible_drops(self):
        noxious = ["Noxious_blade", "Noxious_point", "Noxious_pommel"]
        have_noxious = [item for item in noxious if self.drops[item] > 0]
        if len(have_noxious) == 3:
            return list(self.u_drop_table.keys())
        return [item for item in noxious if self.drops[item] == 0] + ["Araxyte_fang"]

    def kill_boss(self):
        drop = self.roll_for_drop()
        if drop:
            self.drops[drop] += 1

    def has_all_unique_drops(self):
        return all(count > 0 for count in self.drops.values())

    def simulate_until_all_drops(self):
        kills = 0
        while not self.has_all_unique_drops():
            self.kill_boss()
            kills += 1
        return kills

def simulate_multiple_players(num_players):
    kills_list = []
    for i in range(num_players):
        player = Player(f"Player_{i+1}")
        kills_list.append(player.simulate_until_all_drops())
    return np.mean(kills_list), kills_list

# Run simulation
mean_kills, kills_data = simulate_multiple_players(100)
print(f"Mean kills to get all unique drops (100 players): {mean_kills:.2f}")

# Plot results
plt.figure(figsize=(10,6))
plt.hist(kills_data, bins=50, edgecolor='black')
plt.title('Kills Needed to Get All Unique Drops')
plt.xlabel('Number of Kills')
plt.ylabel('Number of Players')
plt.grid(True)
plt.show()

