import re

class IntentParser:
    """
    Interpreta mensagens do usuário e identifica intenções (Intents).
    Mapeia linguagem natural para ações do bot.
    """
    def __init__(self):
        self.intent_map = {
            "value_bet": [r"aposta boa", r"vale a pena", r"onde apostar", r"sugestão", r"dicas", r"value", r"tips"],
            "best_odds": [r"melhor odd", r"onde tá pagando mais", r"comparar odds", r"betano"],
            "bankroll": [r"minha banca", r"saldo", r"quanto eu tenho", r"gestão"],
            "profit": [r"lucro", r"roi", r"estatísticas", r"ganhei"],
            "trade": [r"trade", r"scalping", r"hedge", r"sair do jogo"],
            "previsao": [r"previsão", r"quem ganha", r"análise", r"acha desse jogo", r"liga", r"nba", r"ucl", r"epl", r"brasileirão", r"jogos"],
            "live": [r"ao vivo", r"live", r"tá rolando", r"pressão"],
            "agenda": [r"agenda", r"calendário", r"quando joga"],
            "jogadores": [r"jogadores", r"quem marca", r"artilheiro"],
            "learning": [r"aprendizado", r"evolução", r"melhorando", r"auto-ajuste"],
            "leverage": [r"alavancagem", r"ciclo", r"meta", r"hedge hoje"],
            "insider": [r"insider", r"sinal antecipado", r"notícia", r"vazou", r"lesão"],
            "time_clarification": [r"quando", r"data", r"que dia"],
            "history": [r"histórico", r"últimos jogos", r"confrontos", r"estatísticas", r"desempenho", r"médias"]
        }

    def parse(self, text):
        text = text.lower()
        for intent, patterns in self.intent_map.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return intent
        return "chat" # Padrão: Conversa normal com LLM
