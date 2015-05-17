__author__ = 'Iason'


class TopSort(object):

    def __init__(self, forest):
        self.forest = forest

    """
    The actual top sort algorithm
    """
    def top_sort(self):
        forest = self.forest
        v = get_v(forest)
        s, d = get_sd(v, forest)

        # L, top sorted nodes
        l = []

        # TEMP PRINT V
        print "\n--- V -------------------"
        for item in v:
            print item

        # TEMP PRINT S
        print "\n--- S-------------------"
        for i in s:
            print i

        # TEMP PRINT D
        print "\n--- D-------------------"
        for i, dd in d.iteritems():
            print i, dd

        while len(s) is not 0:
            # remove and return a node from S
            q = s.pop()

            # append q to L
            l.append(q)

            # outgoing edges from q
            temp_fs = get_fs(q, forest)
            for e in temp_fs:
                # parent of q in e
                p = e.lhs

                # remove q from D(p)
                d[p].remove(q)

                # if p's dependencies have been sorted
                if len(d[p]) < 1:
                    del d[p]
                    s.append(p)

        print "\n=== TOP SORTED ========================="
        rev_l = reversed(l)
        for meh in rev_l:
            for r in forest:
                if r.lhs == meh:
                    print r
        return l

"""
create V = terminals + non-terminals
"""
def get_v(forest):
    v = []

    for rule in forest:
        if not v.__contains__(rule.lhs):
            v.append(rule.lhs)

        for item in rule.rhs:
            if not v.__contains__(item):
                v.append(item)
    return v

"""
The backward star of q, is the set of incoming edges to q.
It is the set of all rules whose LHS is the non-terminal q,
BS(q) = {e elem E: h[e] = q}
"""
def get_bs(q, forest):
    bs = []

    for rule in forest:
        if rule.lhs == q:
            bs.append(rule)

    return bs

"""
The forward star of q, is the set of outgoing edges from q.
It is the set of all rules that use q in their RHS
FS(q) = {e elem E: q elem t[e]}
"""
def get_fs(q, forest):
    fs = []

    for rule in forest:
        if rule.rhs.__contains__(q):
            fs.append(rule)

    return fs

"""
Get S and D, states without and with dependencies respectively
"""
def get_sd(v, forest):
    s = []
    d = dict()

    for item in v:
        temp_bs = get_bs(item, forest)
        # create S, states without dependencies
        if len(temp_bs) < 1:
            s.append(item)

        # create D, states with their direct dependencies
        else:
            d.update({item: []})

            for bs in temp_bs:
                for i in bs.rhs:
                    d[item].append(i)

    return s, d


