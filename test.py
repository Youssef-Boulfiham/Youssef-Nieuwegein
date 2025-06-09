def get_pings(self, age_counts, binge_percentages, fixed_drinker_counts):
    results = {}
    for age, count in age_counts.items():
        num_drinkers = fixed_drinker_counts.get(age, 0)
        binge_percentage = binge_percentages.get(age, 0)

        # Maak een array met booleans: wie vaste drinker is
        is_drinker = np.zeros(count, dtype=bool)
        is_drinker[:num_drinkers] = True
        np.random.shuffle(is_drinker)

        # Vul resistances voor drinkers willekeurig (los van agents)
        resistance = np.zeros(count)
        resistances = np.random.uniform(0.05, 0.95, size=num_drinkers)
        np.random.shuffle(resistances)

        idx = 0
        for i in range(count):
            if is_drinker[i]:
                resistance[i] = resistances[idx]
                idx += 1

        # Voeg ruis toe voor realisme
        noise = np.random.normal(0, 2)
        expected = int(round((binge_percentage / 100) * num_drinkers + noise))
        expected = max(0, min(expected, num_drinkers))
        results[age] = expected
    return results

def middelen_gebruiken(self, substance, pings):
    for age, num_pings in pings.items():
        if num_pings == 0:
            continue

        # Filter agents op leeftijd en fixed gebruiker per stof
        if substance == "alcohol":
            fixed_users = [a for a in self.agents if a.age == age and a.fixed_drinker]
            # Sorteer op alcohol_resistance
            sorted_agents = sorted(fixed_users, key=lambda a: a.alcohol_resistance)
        elif substance == "smoking":
            fixed_users = [a for a in self.agents if a.age == age and a.fixed_smoker]
            # Sorteer op smoking_resistance
            sorted_agents = sorted(fixed_users, key=lambda a: a.smoking_resistance)
        else:
            continue

        candidates = []
        for agent in sorted_agents:
            if substance not in agent.substance_count:
                agent.substance_count[substance] = 0

            if substance == "alcohol":
                base_chance = 1 - agent.alcohol_resistance
            else:
                base_chance = 1 - agent.smoking_resistance

            usage_factor = 1 + (agent.substance_count[substance] * 0.1)
            chance = base_chance * usage_factor
            candidates.append((agent, chance))

        total_chance = sum(chance for _, chance in candidates)
        if total_chance == 0:
            continue

        normalized = [(agent, chance / total_chance) for agent, chance in candidates]
        selected_agents = np.random.choice(
            [agent for agent, _ in normalized],
            size=min(num_pings, len(normalized)),
            replace=False,
            p=[chance for _, chance in normalized]
        )

        for agent in selected_agents:
            agent.substance_count[substance] += 1
            agent.action = f"used {substance}"
            print(f"Agent {agent.name} (age {agent.age}) used {substance}.")
