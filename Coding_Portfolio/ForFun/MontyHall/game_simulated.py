import random
import matplotlib.pyplot as plt

def simulate_monty_hall(switch=False):
    prizes = [False, False, True]  # False = goat, True = car
    random.shuffle(prizes)
    player_choice = random.randint(0, 2)
    remaining_goats = [i for i, prize in enumerate(prizes) if prize is False and i != player_choice]
    door_to_reveal = random.choice(remaining_goats)
    if switch:
        player_choice = 3 - player_choice - door_to_reveal
    outcome = prizes[player_choice]
    return outcome  # True for win, False for lose

if __name__ == '__main__':
    num_simulations = 1234

    # Switching strategy
    switch_wins = 0
    for _ in range(num_simulations):
        result = simulate_monty_hall(switch=True)
        switch_wins += result

    print(f"Out of {num_simulations} simulations, the player won {switch_wins} times switching.")

    # Staying strategy
    stay_wins = 0
    for _ in range(num_simulations):
        result = simulate_monty_hall(switch=False)
        stay_wins += result

    print(f"Out of {num_simulations} simulations, the player won {stay_wins} times staying.")

    fig, ax = plt.subplots()

    strategies = ['switch', 'stay']
    counts = [switch_wins, stay_wins]
    colors = ['tab:blue', 'tab:red']

    ax.bar(strategies, counts, color=colors)
    ax.set_ylabel('Number of Wins')
    ax.set_title(f'Monty Hall Simulation ({num_simulations} iterations)')

    plt.savefig("simulated.png")
