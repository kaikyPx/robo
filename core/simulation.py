from core.strategy import check_trigger_1, check_trigger_2

def run_simulation(numbers, target_numbers, max_attempts=4):
    """
    Realiza a simulação iterando sobre os números.
    Retorna uma lista de resultados contendo informações de cada gatilho disparado.
    """
    results = []
    i = 0
    total_numbers = len(numbers)
    
    while i < total_numbers - 1:
        trigger_found = False
        trigger_type = 0
        trigger_end_index = i
        
        # Verifica Gatilho 1
        if check_trigger_1(numbers[i], numbers[i+1]):
            trigger_found = True
            trigger_type = 1
            trigger_end_index = i + 1
        # Verifica Gatilho 2
        elif i < total_numbers - 2 and check_trigger_2(numbers[i], numbers[i+1], numbers[i+2]):
            trigger_found = True
            trigger_type = 2
            trigger_end_index = i + 2
            
        if trigger_found:
            # Simulação das tentativas
            attempts = 0
            hit = False
            hit_attempt = 0
            
            # Posição onde começamos a verificar as tentativas
            sim_index = trigger_end_index + 1
            
            while attempts < max_attempts and sim_index < total_numbers:
                attempts += 1
                drawn_number = numbers[sim_index]
                
                if drawn_number in target_numbers:
                    hit = True
                    hit_attempt = attempts
                    break
                
                sim_index += 1
                
            results.append({
                'trigger_type': trigger_type,
                'trigger_index': trigger_end_index,
                'trigger_value': numbers[trigger_end_index],
                'result_value': drawn_number if attempts > 0 else "-",
                'hit': hit,
                'hit_attempt': hit_attempt if hit else 0,
                'attempts_used': attempts
            })
            
            # Após finalizar um gatilho, continua procurando o próximo normalmente
            i = sim_index if hit or attempts == max_attempts else sim_index
            continue
            
        i += 1
        
    return results
