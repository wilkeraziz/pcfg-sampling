"""
@author wilkeraziz
"""

import collections
import itertools
import logging

EMPTY_SET = frozenset()


class Agenda(object):

    def __init__(self, item_factory, active=[], passive=[]):
        self._item_factory = item_factory
        # a queue of active states
        self._active = collections.OrderedDict()
        # these are the passive states
        # they are organized in sets
        # and distinguished between 'complete' and 'waiting for completion'
        self._waiting_completion = collections.defaultdict(set)
        self._complete = collections.defaultdict(set)

        for item in active:
            self._active[item.uid] = True

        for item in passive:
            if item.is_complete():
                self._complete[(item.start, item.rule.lhs)].add(item.uid)
            else:
                self._waiting_completion[(item.dot, item.next)].add(item.uid)

    def __str__(self):
        lines = ['passive (incomplete)']
        for key, items in self._waiting_completion.iteritems():
            lines.extend(str(item) for item in items)
        lines.append('passive (complete)')
        for key, items in self._complete.iteritems():
            lines.extend(str(item) for item in items)
        lines.append('active')
        for item in self._active.iterkeys():
            lines.append(str(item))
        return '\n'.join(lines)

    def clear(self):
        self._active.clear()
        self._waiting_completion.clear()
        self._complete.clear()

    def __len__(self):
        return len(self._active)

    def pop(self):
        uid, _ = self._active.popitem(last=False)
        return self._item_factory[uid]

    def is_passive(self, item):
        """Whether or not this state is passive (that is, is complete or waiting for completion)."""
        return item.uid in self._waiting_completion.get((item.dot, item.next), EMPTY_SET) or item.uid in self._complete.get((item.start, item.rule.lhs), EMPTY_SET)

    def make_passive(self, item):
        """Make a state passive storing it in the appropriate container."""
        try:
            del self._active[item.uid]
        except:
            pass
        if item.is_complete():
            self._complete[(item.start, item.rule.lhs)].add(item.uid)
        else:
            self._waiting_completion[(item.dot, item.next)].add(item.uid)

    def complete(self, item):
        """Stores a complete state, this is syntactic sugar for makePassive in case the input state is complete."""
        assert item.is_complete(), 'This state is not complete: %s' % item
        self._complete[(item.start, item.rule.lhs)].add(item.uid)

    def itercomplete(self):
        """Iterates over the complete states in no particular order."""
        return (self._item_factory[uid] for uid in itertools.chain(*self._complete.itervalues()))

    def get_passive(self):
        passive = collections.defaultdict(set)
        [passive[key[1]].update(items) for key, items in self._complete.iteritems()]
        [[passive[self._item_factory[uid].rule.lhs].add(uid) for uid in items] for items in self._waiting_completion.itervalues()]
        return passive

    def extend(self, items):
        """Adds states to the active queue if necessary and returns how many states were added."""
        before = len(self._active)
        # it is important not to add passive items to the active agenda
        # it would not break the intersection, but it would make it a lot less efficient
        for item in itertools.ifilter(lambda item: not self.is_passive(item), items):
            self._active[item.uid] = True
        return len(self._active) - before

    def match_items_waiting_completion(self, complete):
        """Returns all the passive items that are waiting for the complete input item."""
        assert complete.is_complete(), 'This is not a complete state: %s' % complete
        return (self._item_factory[uid] for uid in self._waiting_completion.get((complete.start, complete.rule.lhs), EMPTY_SET))

    def match_complete_items(self, incomplete):
        """Returns all the complete items that can make an incomplete item progress."""
        assert not incomplete.is_complete(), 'This is not an incomplete item: %s' % incomplete
        return (self._item_factory[uid] for uid in self._complete.get((incomplete.dot, incomplete.next), EMPTY_SET))
