import time
import numpy as np
import matplotlib.pyplot as plt

# Age-based parameters
age_counts = {12: 4, 13: 4, 14: 4, 15: 3, 16: 3, 17: 3, 18: 3}
binge_percentages = {12: 1, 13: 3, 14: 6, 15: 14, 16: 36, 17: 48, 18: 86}

# Simulation parameters
num_steps = 24
num_epochs = 1000

# Track results
step_pings = {age: np.zeros((num_steps,)) for age in age_counts}
ping_details = {age: [] for age in age_counts}
players_pinged = {age: np.zeros((num_epochs, age_counts[age]), dtype=bool) for age in age_counts}

# Simulation loop
for epoch in range(num_epochs):
    print(f"\n--- Epoch {epoch + 1} ---")

    for age, player_count in age_counts.items():
        print(f"\n  Age {age} with {player_count} players")

        # Select resistance factors based on player count
        if player_count == 3:
            resistance_factors = np.array([0.5, 1.0, 1.5])
        elif player_count == 4:
            resistance_factors = np.array([0.5, 0.75, 1.25, 1.5])
        else:
            continue  # Skip invalid player counts

        # Binge percentage as ping probability
        binge_prob = binge_percentages[age] / 100.0

        # Initialize pings for this epoch
        epoch_pings = np.zeros((player_count, num_steps), dtype=bool)

        # Step-first loop
        for step in range(num_steps):
            for player in range(player_count):
                # Adjust ping probability based on resistance
                step_ping_prob = binge_prob / resistance_factors[player]

                # Determine if the player pings at this step
                if np.random.rand() < step_ping_prob:
                    epoch_pings[player, step] = True
                    players_pinged[age][epoch, player] = True

                    # Store ping details
                    ping_details[age].append((epoch + 1, player + 1, step + 1))

                # Print the ping status
                status = 'True' if epoch_pings[player, step] else 'False'
                print(f"      Player {player + 1} (Res: {resistance_factors[player]}): {status}")

                time.sleep(0.01)  # Reduced sleep time for faster execution

            # Accumulate pings per step
            step_pings[age][step] += np.sum(epoch_pings[:, step])
        print()

# Compute statistics
average_ping_per_step = {
    age: step_pings[age] / (age_counts[age] * num_epochs) for age in age_counts
}

pinged_players_per_epoch = {
    age: np.mean(players_pinged[age], axis=1) * 100 for age in age_counts
}

# Print results
print("\n--- Step-wise Average Ping Probabilities ---")
for age, probs in average_ping_per_step.items():
    print(f"\nAge {age}:")
    for step, prob in enumerate(probs):
        print(f"  Step {step + 1}: {prob:.2%}")

print("\n--- Overall Ping Statistics ---")
for age in age_counts:
    avg_pinged = np.mean(pinged_players_per_epoch[age])
    print(f"Age {age}: {avg_pinged:.2f}% of players pinged at least once per epoch")

# Plot step-wise ping probabilities
plt.figure(figsize=(12, 6))
for age, probs in average_ping_per_step.items():
    plt.plot(range(1, num_steps + 1), probs, label=f'Age {age}')
plt.axhline(y=0.66, color='red', linestyle='dashed', linewidth=2, label='Expected 66%')
plt.xlabel('Step Index')
plt.ylabel('Proportion of True Pings')
plt.title(f'Ping Probability per Step Over {num_epochs} Epochs by Age')
plt.legend()
plt.show()

# Plot distribution of players who pinged per epoch
plt.figure(figsize=(12, 6))
for age, data in pinged_players_per_epoch.items():
    plt.hist(data, bins=20, alpha=0.6, label=f'Age {age}')
plt.axvline(x=66, color='red', linestyle='dashed', linewidth=2, label='Expected 66%')
plt.xlabel('Percentage of Players Who Pinged per Epoch')
plt.ylabel('Frequency')
plt.title(f'Distribution of Players Who Pinged Across {num_epochs} Epochs by Age')
plt.legend()
plt.show()
