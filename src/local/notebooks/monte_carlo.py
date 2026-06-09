from scipy import stats
import numpy as np
from typing import Literal
from matplotlib import pyplot as plt
import seaborn as sns

class MeanOneGenerator:
    """
    Generate random distributions of mean 1
    """
    def __init__(self, size=100000):
        self.size = size
        # Bank of base distributions with random shape parameters
        self.distribution_bank = [
            (stats.lognorm, {'s': lambda: np.random.uniform(0.5, 2.0)}),  # Heavy right tail
            (stats.gamma, {'a': lambda: np.random.uniform(0.5, 5.0)}),    # Flexible skew
            (stats.weibull_min, {'c': lambda: np.random.uniform(0.5, 2.0)}), # Extreme value
            # (stats.halfcauchy, {'loc': lambda: 0, 'scale': lambda: 1})    # Extreme heavy tail (dont't use because it doesn't have a finite mean)
        ]

    def generate_uniform_shape(self, width=None):
      """Generates a uniform distribution with random variance, projected to mean 1."""
      
      if width is None:
          width = np.random.uniform(low=0.1, high=0.99)
      
      Z = np.random.uniform(low=1.0 - width, high=1.0 + width, size=self.size)
      X = Z / np.mean(Z) 
    
      return X, "uniform", {"low": 1.0 - width, "high": 1.0 + width}
    
    def generate_custom_shape(self, shape: Literal["uniform", "lognorm", "gamma", "dirac", "weibull_min"]):
        if shape == "uniform":
            return self.generate_uniform_shape()
        elif shape == "dirac":
            # Generate a Dirac delta distribution (all values are 1)
            X = np.ones(self.size)
            return X, "dirac", {}
        else:
            dist_class, param_generators = self.distribution_bank[{"lognorm": 0, "gamma": 1, "weibull_min": 2}[shape]]
            
            # Evaluate the random parameters
            params = {k: v() for k, v in param_generators.items()}
            
            # Generate the unconstrained array (Z)
            Z = dist_class.rvs(**params, size=self.size)
            
            # Project to Mean = 1 (X)
            empirical_mean = np.mean(Z)
            X = Z / empirical_mean
            
            return X, dist_class.name, params
        
    def generate_random_shape(self):
        """Selects a random distribution and randomizes its shape parameters."""
        
        dist_class, param_generators = self.distribution_bank[np.random.randint(0, len(self.distribution_bank))]
        
        # Evaluate the random parameters
        params = {k: v() for k, v in param_generators.items()}
        
        # Generate the unconstrained array (Z)
        Z = dist_class.rvs(**params, size=self.size)
        
        # Project to Mean = 1 (X)
        empirical_mean = np.mean(Z)
        X = Z / empirical_mean
        
        return X, dist_class.name, params

def sample_from_empirical(X, size=None):
    """
    Sample with replacement from an empirical distribution defined by the array X. 
    
    Args:
      X (array-like): The empirical distribution to sample from.
      size (int, optional): The number of samples to draw. Defaults to the length of X.

    Returns:
      array-like: Samples from the empirical distribution.
    """
    if size is None:
        size = len(X)
    return np.random.choice(X, size=size, replace=True)

def pmf_to_particles(pmf_array, size):
    """
    Converts a PMF array into a corresponding array of particles.
    """
    possible_values = np.arange(len(pmf_array))
    normalized_pmf = pmf_array / np.sum(pmf_array)
    
    particles = np.random.choice(possible_values, size=size, p=normalized_pmf)
    
    return particles


def plot_distribution(
        particle_array, 
        title="Empirical Distribution", 
        bins=100, clip_percentile=100, 
        log_y=False, show_bins=False, show_kde=True):
    """
    Plots the distribution of a 1D array of particles with optional bins and KDE.
    """
    clean_array = particle_array[np.isfinite(particle_array)]
    
    if clip_percentile < 100:
        max_val = np.percentile(clean_array, clip_percentile)
        view_array = clean_array[clean_array <= max_val]
        clip_note = f" (X-axis clipped at {clip_percentile}th percentile)"
    else:
        view_array = clean_array
        clip_note = ""

    plt.figure(figsize=(10, 6))
    
    if show_bins and show_kde:
        ax = sns.histplot(view_array, bins=bins, kde=True, 
                          stat="density", alpha=0.4)
                        
    elif show_bins and not show_kde:
        ax = sns.histplot(view_array, bins=bins, kde=False, 
                          stat="density", alpha=0.6)
                          
    elif not show_bins and show_kde:
        ax = sns.kdeplot(view_array, fill=True, alpha=0.3, linewidth=2, warn_singular=False)
        
    else:
        print("Error: Must choose to show either bins, KDE, or both.")
        return

    if log_y:
        ax.set_yscale('log')
        plt.ylabel("Density (Log Scale)")
    else:
        plt.ylabel("Density")
        
    plt.xlabel("Particle Value")
    plt.title(title + clip_note, fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    emp_mean = np.mean(clean_array)
    plt.axvline(emp_mean, color='red', linestyle='dashed', linewidth=1, 
                label=f'Mean = {emp_mean:.4f}')
    
    plt.legend()
    plt.tight_layout()
    plt.show()

def wasserstein(X, Y, p=1):

    X = np.asarray(X)
    Y = np.asarray(Y)
    
    if len(X) != len(Y):
        raise ValueError(f"Distributions must have the same length. "
                         f"Got len(X)={len(X)} and len(Y)={len(Y)}.")
  
    X_sorted = np.sort(X)
    Y_sorted = np.sort(Y)
    distance = np.power(np.mean(np.abs(X_sorted - Y_sorted)**p), 1/p)
    
    return distance