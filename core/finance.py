def calculate_financials(simulation_results, bet_amount=1.0, payout_multiplier=36, target_count=15, martingale_multipliers=None):
    """
    Calcula os resultados financeiros da simulação.
    """
    if martingale_multipliers is None:
        martingale_multipliers = [1, 2, 4, 8] # Exemplo default
        
    fin_results = []
    
    for res in simulation_results:
        # Aposta Fixa
        fixed_cost = res['attempts_used'] * (bet_amount * target_count)
        fixed_revenue = (bet_amount * payout_multiplier) if res['hit'] else 0
        fixed_profit = fixed_revenue - fixed_cost
        
        # Martingale
        martingale_cost = 0
        martingale_revenue = 0
        
        for attempt in range(1, res['attempts_used'] + 1):
            mult = martingale_multipliers[attempt - 1] if attempt <= len(martingale_multipliers) else martingale_multipliers[-1]
            current_bet = bet_amount * mult
            martingale_cost += (current_bet * target_count)
            
            if res['hit'] and attempt == res['hit_attempt']:
                martingale_revenue = current_bet * payout_multiplier
                break
                
        martingale_profit = martingale_revenue - martingale_cost
        
        fin_results.append({
            'fixed_profit': fixed_profit,
            'martingale_profit': martingale_profit,
            'hit': res['hit']
        })
        
    return fin_results
