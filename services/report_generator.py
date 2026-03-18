from tabulate import tabulate

class ReportGenerator:
    def __init__(self):
        pass

    def generate_daily_report(self, value_bets):
        if not value_bets:
            return "Nenhuma Value Bet encontrada para hoje."

        headers = ["Time/Jogo", "Seleção", "Odds", "Prob Real", "EV"]
        table_data = []
        
        for bet in value_bets:
            table_data.append([
                f"{bet['home_team']} vs {bet['away_team']}",
                bet['selection'],
                bet['odds'],
                f"{bet['real_prob']*100:.1f}%",
                f"{bet['ev']*100:.1f}%"
            ])
            
        report = "📊 *RELATÓRIO DIÁRIO DE APOSTAS DE VALOR*\n\n"
        report += f"```{tabulate(table_data, headers=headers, tablefmt='simple')}```\n\n"
        report += "💡 _Sugestão: Use gestão de banca rigorosa._"
        
        return report

    def generate_history_report(self, history):
        if not history:
            return "Sem histórico de apostas registrado."
            
        # Simplificado para o Bot
        total_bets = len(history)
        wins = len([b for b in history if b['result'] == 'WIN'])
        profit = sum([b['profit'] for b in history if b['profit'] is not None])
        
        report = "📈 *RESUMO DE PERFORMANCE*\n\n"
        report += f"Total de Apostas: {total_bets}\n"
        report += f"Taxa de Acerto: {(wins/total_bets*100 if total_bets > 0 else 0):.1f}%\n"
        report += f"Lucro/Prejuízo Total: R$ {profit:.2f}\n"
        report += f"ROI: {(profit/(total_bets*10) if total_bets > 0 else 0):.1f}%" # Assumindo stake média 10
        
        return report
