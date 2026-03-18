class TiltControl:
    """
    Gerencia o estado emocional do apostador (controle de tilt).
    """
    def __init__(self, max_losses=3):
        self.max_losses = max_losses
        self.current_loss_streak = 0

    def record_result(self, is_win):
        if is_win:
            self.current_loss_streak = 0
        else:
            self.current_loss_streak += 1
            
    def should_stop(self):
        return self.current_loss_streak >= self.max_losses

    def get_advice(self):
        if self.should_stop():
            return "🚨 ALERTA DE TILT: Você está em uma sequência de perdas. Sugerimos uma PAUSA de 24 horas."
        return "✅ Controle emocional estável. Siga a gestão de banca."
