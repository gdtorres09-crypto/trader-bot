class SharpMoneyDetector:
    """
    Detecta movimentação de dinheiro profissional (Sharp Money).
    """
    def __init__(self):
        pass

    def detect(self, match_id, volume_data, odds_change):
        # Lógica: Se o volume é alto e as odds caem contra a tendência pública
        # Mock de detecção
        if odds_change < -0.10: # Queda brusca
            return True
        return False
