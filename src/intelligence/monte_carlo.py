import numpy as np

class MonteCarloEngine:
    """
    Motor estocástico para simulaciones de Monte Carlo aplicado a Wealth Management.
    Permite proyectar el patrimonio bajo miles de escenarios de mercado considerando volatilidad.
    """
    
    # Parámetros base del mercado (Retornos Reales y Volatilidad estimados a largo plazo)
    # Valores asumen inflación ya descontada (Retorno Real)
    PROFILES = {
        "Conservador": {"return_mean": 0.04, "volatility": 0.04},
        "Moderado": {"return_mean": 0.06, "volatility": 0.09},
        "Agresivo": {"return_mean": 0.08, "volatility": 0.15},
        "Experto": {"return_mean": 0.09, "volatility": 0.18}
    }

    @staticmethod
    def run_wealth_projection(
        patrimonio_inicial: float,
        ahorro_mensual: float,
        perfil_riesgo: str,
        horizonte_anos: int,
        num_simulaciones: int = 10000
    ) -> dict:
        """
        Ejecuta la simulación de Monte Carlo y devuelve estadísticas clave.
        """
        if perfil_riesgo not in MonteCarloEngine.PROFILES:
            perfil_riesgo = "Moderado" # Default fallback
            
        params = MonteCarloEngine.PROFILES[perfil_riesgo]
        mu = params["return_mean"]
        sigma = params["volatility"]
        
        ahorro_anual = ahorro_mensual * 12
        
        # Matriz para almacenar todas las simulaciones (escenarios x años)
        simulations = np.zeros((num_simulaciones, horizonte_anos + 1))
        simulations[:, 0] = patrimonio_inicial
        
        # Generar retornos aleatorios asumiendo distribución normal log-normal
        # (1 + r) ~ LogNormal
        for year in range(1, horizonte_anos + 1):
            # Muestra aleatoria de retornos para este año en todas las simulaciones
            random_returns = np.random.normal(loc=mu, scale=sigma, size=num_simulaciones)
            
            # Capitalizar el año anterior y sumar el ahorro del año
            # Asumimos que el ahorro anual crece con la inflación, al ser retornos reales, el ahorro se mantiene constante en valor real
            simulations[:, year] = simulations[:, year - 1] * (1 + random_returns) + ahorro_anual
            
            # El patrimonio no puede ser negativo
            simulations[:, year] = np.maximum(simulations[:, year], 0)
            
        final_wealth = simulations[:, -1]
        
        # Extraer percentiles clave
        pesimista_10 = np.percentile(final_wealth, 10)
        esperado_50 = np.percentile(final_wealth, 50)
        optimista_90 = np.percentile(final_wealth, 90)
        
        return {
            "horizonte_anos": horizonte_anos,
            "perfil_riesgo": perfil_riesgo,
            "simulaciones_ejecutadas": num_simulaciones,
            "escenario_pesimista_10": float(pesimista_10),
            "escenario_esperado_50": float(esperado_50),
            "escenario_optimista_90": float(optimista_90),
            # Guardamos trayectorias de muestra (ej. 3) para posible graficación en UI
            "sample_paths": simulations[:3, :].tolist()
        }
