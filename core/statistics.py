def generate_statistics(simulation_results, financial_results, total_numbers_analyzed):
    """Gera o consolidado estatístico dos resultados."""
    total_triggers = len(simulation_results)
    hits = [r for r in simulation_results if r['hit']]
    losses = [r for r in simulation_results if not r['hit']]
    
    hits_by_attempt = {}
    for h in hits:
        att = h['hit_attempt']
        hits_by_attempt[att] = hits_by_attempt.get(att, 0) + 1
        
    win_rate = (len(hits) / total_triggers * 100) if total_triggers > 0 else 0
    
    # Financial metrics
    fixed_profits = [f['fixed_profit'] for f in financial_results]
    martingale_profits = [f['martingale_profit'] for f in financial_results]
    
    net_fixed = sum(fixed_profits)
    net_martingale = sum(martingale_profits)
    
    # Drawdown calc helper
    def calc_drawdown(profits):
        peak = 0
        max_dd = 0
        current_balance = 0
        for p in profits:
            current_balance += p
            if current_balance > peak:
                peak = current_balance
            dd = peak - current_balance
            if dd > max_dd:
                max_dd = dd
        return max_dd

    stats = {
        'total_analyzed': total_numbers_analyzed,
        'total_triggers': total_triggers,
        'hits': len(hits),
        'losses': len(losses),
        'hits_by_attempt': hits_by_attempt,
        'win_rate': win_rate,
        'net_fixed_profit': net_fixed,
        'net_martingale_profit': net_martingale,
        'max_dd_fixed': calc_drawdown(fixed_profits),
        'max_dd_martingale': calc_drawdown(martingale_profits)
    }
    
    return stats
