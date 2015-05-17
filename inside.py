__author__ = 'Iason'

from topSort import get_bs


class Inside(object):

    def __init__(self, forest, sorted_forest):
        self.forest = forest
        self.sorted_forest = sorted_forest

    """
    The actual algorithm
    """
    def inside(self):
        forest = self.forest
        sorted_forest = self.sorted_forest
        inside_prob = dict()

        # visit nodes bottom up
        for q in sorted_forest:
            incoming = get_bs(q, forest)
            print "\n=== Q =================", q, "========================"
            print "BS: "
            for i in incoming:
                print i
            print

            # leaves have inside weight 1
            if len(incoming) < 1:
                inside_prob[q] = 1
            else:
                inside_prob[q] = 0

                # total inside weight of an incoming edge
                for bs in incoming:
                    k = bs.log_prob
                    print "K = ", k, "\n"

                    for e in bs.rhs:
                        print "edge", e

                        # including the edge own weight
                        k = k * inside_prob[e]
                        print "updated K = ", k, "\n"

                    inside_prob[q] = inside_prob[q] + k

            print "INSIDE prob of ", q, " = ", inside_prob[q]

        return inside_prob

