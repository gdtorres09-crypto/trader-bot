class EVCalculator:
    """
    Calculadora pura de Valor Esperado (Expected Value).
    """
    @staticmethod
    def calculate(prob, odds):
        # EV = (Probabilidade de Ganhar * Lucro por Aposta) - (Probabilidade de Perder * Valor da Aposta)
        # Simplificado: (Prob * Odds) - 1
        return (prob * odds) - 1

    @staticmethod
    def is_profitable(prob, odds, threshold=0.05):
        return EVCalculator.calculate(prob, odds) > threshold
