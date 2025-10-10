# Define the payoff matrix.
# Key: (Player 1 Strategy, Player 2 Strategy)
# Value: (Player 1 Payoff, Player 2 Payoff) - Years in prison
# Strategies: 'C' (Cooperate/Silent), 'D' (Defect/Betray)
PAYOFF_MATRIX = {
    ('C', 'C'): (2, 2),   # Reward: Both get 2 years
    ('C', 'D'): (10, 0),  # Sucker/Temptation: P1 gets 10, P2 goes free (0)
    ('D', 'C'): (0, 10),  # Temptation/Sucker: P1 goes free (0), P2 gets 10
    ('D', 'D'): (5, 5)    # Punishment: Both get 5 years
}

STRATEGIES = ['C', 'D']

def find_nash_equilibrium(payoffs):
    """
    Finds the Nash Equilibrium by checking if any player can improve their
    payoff by unilaterally switching strategies.
    
    A strategy pair (S1, S2) is a NE if:
    1. P1's payoff for (S1, S2) is >= P1's payoff for (S1_alt, S2).
    2. P2's payoff for (S1, S2) is >= P2's payoff for (S1, S2_alt).
    (Note: Since payoffs are prison years, lower number is better, so we use <=)
    """
    nash_equilibria = []
    
    # Iterate through all possible strategy combinations
    for s1 in STRATEGIES:
        for s2 in STRATEGIES:
            p1_payoff, p2_payoff = payoffs[(s1, s2)]
            is_nash = True
            
            # 1. Check if Player 1 has an incentive to deviate (unilaterally switch strategy)
            p1_alternative_strategy = 'D' if s1 == 'C' else 'C'
            p1_alt_payoff, _ = payoffs[(p1_alternative_strategy, s2)]
            
            # P1 has an incentive to deviate if the alternative payoff is strictly better (less prison time)
            if p1_alt_payoff < p1_payoff:
                is_nash = False
            
            # 2. Check if Player 2 has an incentive to deviate
            p2_alternative_strategy = 'D' if s2 == 'C' else 'C'
            _, p2_alt_payoff = payoffs[(s1, p2_alternative_strategy)]
            
            # P2 has an incentive to deviate if the alternative payoff is strictly better
            if p2_alt_payoff < p2_payoff:
                is_nash = False
                
            if is_nash:
                nash_equilibria.append(((s1, s2), (p1_payoff, p2_payoff)))
                
    return nash_equilibria

def find_socially_optimal(payoffs):
    """
    Finds the outcome that minimizes the total combined years in prison (P1 + P2).
    """
    best_outcome = None
    min_total_years = float('inf')
    
    for strategies, (p1_payoff, p2_payoff) in payoffs.items():
        total_years = p1_payoff + p2_payoff
        
        if total_years < min_total_years:
            min_total_years = total_years
            best_outcome = (strategies, (p1_payoff, p2_payoff))
            
    return best_outcome

# --- Execution ---

print("--- Prisoner's Dilemma Analysis ---")
print("Payoff Format: (Years for P1, Years for P2). Lower is better.")
print(f"Full Payoff Matrix: {PAYOFF_MATRIX}\n")

# 1. Calculate Nash Equilibrium
ne_results = find_nash_equilibrium(PAYOFF_MATRIX)

print("1. Nash Equilibrium (The Self-Interested Choice):")
if ne_results:
    for strategies, payoffs in ne_results:
        print(f"  -> Strategies: P1 chooses '{strategies[0]}', P2 chooses '{strategies[1]}'")
        print(f"  -> Payoffs (Years): P1: {payoffs[0]}, P2: {payoffs[1]}")
        print("  *Rationale: Each player chooses Defect (D) because it is their dominant strategy, guaranteeing them a better outcome regardless of the other player's choice.")
else:
    print("  -> No pure-strategy Nash Equilibrium found.")

print("\n" + "="*50 + "\n")

# 2. Calculate Socially Optimal Outcome
so_result = find_socially_optimal(PAYOFF_MATRIX)

print("2. Socially Optimal Outcome (The Cooperative Choice):")
strategies, payoffs = so_result
total_years = payoffs[0] + payoffs[1]

print(f"  -> Strategies: P1 chooses '{strategies[0]}', P2 chooses '{strategies[1]}'")
print(f"  -> Payoffs (Years): P1: {payoffs[0]}, P2: {payoffs[1]}")
print(f"  -> Total Combined Years: {total_years}")
print("  *Rationale: This outcome minimizes the total combined years in prison, but it is unstable because each player has an individual incentive to defect.")

"""
Expected Output Summary:
Nash Equilibrium: (Defect, Defect) with (5, 5) years.
Socially Optimal: (Cooperate, Cooperate) with (2, 2) years.
"""
