import numpy as np
import pandas as pd

class MonteCarloSimulator:
    """
    Simulador de Monte Carlo para Proyecciones Patrimoniales (Wealth 3.0).
    Utiliza Movimiento Browniano Geométrico para modelar la incertidumbre.
    """
    
    @staticmethod
    def simulate_gbm(initial_capital, annual_return, annual_volatility, years, n_simulations=1000):
        """
        Simula trayectorias usando Geometric Brownian Motion.
        annual_return y annual_volatility deben estar en decimales (ej: 0.07 para 7%).
        """
        t_steps = years # Pasos anuales para simplicidad, o mensual (years * 12)
        dt = 1 # Paso anual
        
        # Matriz de retornos logarítmicos normales con drift
        # Formula: drift = (mu - 0.5 * sigma^2) * dt
        #          shock = sigma * sqrt(dt) * epsilon
        drift = (annual_return - 0.5 * annual_volatility**2) * dt
        shock = annual_volatility * np.sqrt(dt) 
        
        # Generar retornos aleatorios para cada año y simulación
        # shape: (years, n_simulations)
        random_shocks = np.random.normal(0, 1, (years, n_simulations))
        log_returns = drift + shock * random_shocks
        
        # Acumular retornos (Producto de factores)
        # S_t = S_0 * exp(cumsum(log_returns))
        price_paths = np.exp(np.cumsum(log_returns, axis=0))
        
        # Insertar capital inicial al tiempo 0
        initial_row = np.ones((1, n_simulations))
        price_paths = np.vstack([initial_row, price_paths]) * initial_capital
        
        return price_paths

    @staticmethod
    def get_statistics(paths):
        """
        Calcula percentiles para las bandas de confianza.
        """
        years_len = paths.shape[0]
        stats = {
            'p5': np.percentile(paths, 5, axis=1),
            'p50': np.percentile(paths, 50, axis=1),
            'p95': np.percentile(paths, 95, axis=1),
            'mean': np.mean(paths, axis=1)
        }
        return stats

    @staticmethod
    def calculate_var(initial_capital, paths, confidence_level=0.95):
        """
        Calcula el Valor en Riesgo (VaR) absoluto al final del periodo.
        """
        final_values = paths[-1, :]
        loss = initial_capital - final_values
        var = np.percentile(loss, confidence_level * 100)
        return var

def test_simulation():
    # Prueba rápida
    sim = MonteCarloSimulator()
    paths = sim.simulate_gbm(100000000, 0.07, 0.15, 10, n_simulations=5000)
    stats = sim.get_statistics(paths)
    var = sim.calculate_var(100000000, paths)
    
    print(f"Capital Inicial: 100M")
    print(f"Final P5 (Escenario Pesimista): {stats['p5'][-1]:,.0f}")
    print(f"Final P50 (Mediana): {stats['p50'][-1]:,.0f}")
    print(f"Final P95 (Escenario Optimista): {stats['p95'][-1]:,.0f}")
    print(f"VaR (95% confianza): {var:,.0f}")

if __name__ == "__main__":
    test_simulation()
