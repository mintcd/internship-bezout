import random
import matplotlib.pyplot as plt

def simulate_tree(N, a, b):
    """
    Recursively generates a single realization of the structural metric Y_N.
    """
    if N <= 2:
        return 0
        
    # Uniformly split the remaining N-1 nodes
    U = random.randint(0, N - 1)
    
    # Generate independent subtrees
    left_subtree = simulate_tree(U, a, b)
    right_subtree = simulate_tree(N - 1 - U, a, b)
    
    # Select and apply the operator
    r = random.random()
    if r < a:
        return left_subtree + right_subtree + 1
    elif r < a + b:
        return max(left_subtree, right_subtree)
    else:
        return 0

def run_experiment(max_N, trials, a, b):
    """
    Calculates the empirical expected value for each tree size up to max_N.
    """
    expected_values = []
    
    # Compute the average over multiple trials for each N
    for n in range(1, max_N + 1):
        total = sum(simulate_tree(n, a, b) for _ in range(trials))
        expected_values.append(total / trials)
        
    return list(range(1, max_N + 1)), expected_values

if __name__ == "__main__":
    # Simulation parameters
    max_n = 1000
    trials_per_n = 200

    # Run the three distinct regimes
    # 1. Subcritical: 2a + b < 1 (Expected O(1))
    n_sub, y_sub = run_experiment(max_N=max_n, trials=trials_per_n, a=0.2, b=0.3)

    # 2. Critical: 2a + b = 1 (Expected O(log n))
    n_crit, y_crit = run_experiment(max_N=max_n, trials=trials_per_n, a=0.25, b=0.5)

    # 3. Supercritical: 2a + b > 1 (Expected O(n^p))
    n_sup, y_sup = run_experiment(max_N=max_n, trials=trials_per_n, a=0.4, b=0.4)

    # Plotting the results
    plt.figure(figsize=(10, 6))
    plt.plot(n_sub, y_sub, label="Subcritical (2a+b=0.7)", color='blue')
    plt.plot(n_crit, y_crit, label="Critical (2a+b=1.0)", color='green')
    plt.plot(n_sup, y_sup, label="Supercritical (2a+b=1.2)", color='red')

    plt.title("Monte Carlo Simulation of Expected Structural Metric")
    plt.xlabel("Tree Size (n)")
    plt.ylabel("Empirical Expected Value")
    plt.legend()
    plt.grid(True)
    plt.show()