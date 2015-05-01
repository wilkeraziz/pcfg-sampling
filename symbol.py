"""
@author wilkeraziz
"""


def is_terminal(symbol):
    """nonterminals are formatted as this: [X]"""
    return not (symbol[0] == '[' and symbol[-1] == ']')
            
def make_symbol(base_symbol, sfrom, sto):
    return base_symbol if is_terminal(base_symbol) else '[%s,%d-%d]' % (base_symbol[1:-1], sfrom, sto)

