def check_trigger_1(n1, n2):
    """Gatilho 1: Dois números consecutivos terminam com o mesmo algarismo."""
    return (n1 % 10) == (n2 % 10)

def check_trigger_2(n1, n2, n3):
    """Gatilho 2: Um número de intervalo entre dois números terminados com mesmo algarismo."""
    return (n1 % 10) == (n3 % 10)
