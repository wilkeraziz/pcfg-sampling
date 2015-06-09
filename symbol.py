"""
@author wilkeraziz
"""

from weakref import WeakValueDictionary
import re

NT_RE = re.compile('\[(.+),([0-9]+)-([0-9]+)\]')

def is_terminal(symbol):
    """nonterminals are formatted as this: [X]"""
    return not (symbol[0] == '[' and symbol[-1] == ']')


def is_nonterminal(symbol):
    """nonterminals are formatted as this: [X]"""
    return symbol[0] == '[' and symbol[-1] == ']'

def make_nonterminal(symbol):
    return '[{0}]'.format(symbol)

def make_terminal(symbol):
    return symbol

def make_symbol(base_symbol, sfrom, sto):
    if sfrom is None and sto is None:
        return base_symbol
    return base_symbol if is_terminal(base_symbol) else '[%s,%s-%s]' % (base_symbol[1:-1], sfrom, sto)

def parse_annotated_nonterminal(nt):
    m = NT_RE.match(nt)
    if m is None:
        return nt, None, None
    else:
        return '[{0}]'.format(m.group(1)), int(m.group(2)), int(m.group(3))
    
def _make_symbol(base_symbol, sfrom, sto, structured=True):
    if not structured:
        return base_symbol if is_terminal(base_symbol) else '[%s,%s-%s]' % (base_symbol[1:-1], sfrom, sto)
    else:
        return base_symbol if is_terminal(base_symbol) else (base_symbol[1:-1], sfrom, sto)


class Terminal(object):
    """
    Implements a terminal symbol. References to terminal symbols are managed by the Terminal class.
    We use WeakValueDictionary for builtin reference counting.

    >>> t1 = Terminal(1)
    >>> t2 = Terminal(1)
    >>> t1 == t2
    True
    >>> t1 is t2
    True
    >>> t3 = Terminal(2)
    >>> t1 != t3
    True
    >>> id(t1) == id(t2) != id(t3)
    True
    >>> hash(t1) == hash(t2) != hash(t3)
    True
    >>> Terminal(10)
    Terminal(10)
    >>> Terminal('x')
    Terminal('x')
    """

    _vocabulary = WeakValueDictionary()

    def __new__(cls, surface):
        """The surface has to be hashable"""
        obj = Terminal._vocabulary.get(surface, None)
        if not obj:
            obj = object.__new__(cls)
            Terminal._vocabulary[surface] = obj
            obj._surface = surface
        return obj

    def __repr__(self):
        return '%s(%s)' % (Terminal.__name__, repr(self._surface))

    def __str__(self):
        return str(self._surface)


class Nonterminal(object):
    """
    Implements a nonterminal symbol. References to nonterminal symbols are managed by the Nonterminal class.
    We use WeakValueDictionary for builtin reference counting.

    >>> n1 = Nonterminal('S')
    >>> n2 = Nonterminal('S')
    >>> n3 = Nonterminal('X')
    >>> n1 == n2 != n3
    True
    >>> n1 is n2 is not n3
    True
    >>> Nonterminal(('NP', 1, 2))  # a noun phrase spanning from 1 to 2
    Nonterminal(('NP', 1, 2))
    """

    _categories = WeakValueDictionary()

    def __new__(cls, label):
        """The label has to be hashable"""
        obj = Nonterminal._categories.get(label, None)
        if not obj:
            obj = object.__new__(cls)
            Nonterminal._categories[label] = obj
            obj._label = label
        return obj

    def __repr__(self):
        return '%s(%s)' % (Nonterminal.__name__, repr(self._label))

    def __str__(self):
        return str(self._label)
