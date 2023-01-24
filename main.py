from math import inf

class Automaton:

    def check(self, node):
        if node not in self.S:
            raise f'Error: "{node}" is not in the nodes.'

    def __init__(self, input_file):
        ''' Create an automaton from the data contained in input_file '''
        with open(input_file, 'r') as file:
            self.S = file.readline().strip().split(' ')
            self.s0, self.t = file.readline().strip().split(' ')
            self.check(self.s0)
            self.check(self.t)
            self.T = {}
            self.L = []
            for tr in file:
                src, label, dest = tr.strip().split(' ')
                self.check(src)
                self.check(dest)
                self.T[(src, label)] = dest
                self.L.append(label[1:])
        self.state = self.s0
        self.is_bipartite = False
        self.ranks_computed = False

    def to_bipartite(self):
        ''' Transform the automaton into a bipartite one '''

        # Init V, E and marks (1 for V_R, -1 for V_B)
        self.V = []
        self.E = {}
        self.marks = {}
        for node in self.S:
            self.V.append(node)
            self.E[node] = []
            self.marks[node] = -1

        # Add of "error" states
        self.V.append("errorR")
        self.marks["errorR"] = 1
        self.V.append("errorB")
        self.marks["errorB"] = -1
        self.E["errorB"] = ["errorR"]
        self.E["errorR"] = ["errorB"]

        # Detection of V_R
        for (src, label) in self.T:
            if label[0] == '!':
                self.marks[src] = 1

        # Generate E (check for transitions within V_R/V_B)
        nb_added = 0
        for (src, label), dest in self.T.items():
            if self.marks[src] * self.marks[dest] == 1:
                node = f'new{nb_added}'
                self.V.append(node)
                self.marks[node] = -self.marks[src]
                self.E[src].append(node)
                self.E[node] = [dest]
                if self.marks[node] == 1:
                    self.E[node].append("errorB")
                nb_added += 1
            else:
                self.E[src].append(dest)

        # Add transitions from V_R to errorB
        for node in self.S:
            if self.marks[node] == 1:
                self.E[node].append("errorB")

        # Remember the process has been done
        self.is_bipartite = True

    def move(self, label):
        ''' Move to the next state '''

        if (self.state, label) not in self.T:
            raise f'Unable to process "{label}" from node {self.state}.'
        self.state = self.T[(self.state, label)]

    def compute_ranks(self):
        ''' Compute the ranks '''

        # Get sure the graph is bipartite
        if not(self.is_bipartite):
            self.to_bipartite()

        # Init ranks
        self.ranks = {}
        self.ranks[self.t] = 0
        k = 1

        added = True
        while added:
            added = False
            for p in self.V:
                if p in self.ranks:
                    continue
                if self.marks[p] == -1:
                    for q in self.E[p]:
                        if q in self.ranks:
                            self.ranks[p] = k
                            added = True
                            break
                else:
                    for q in self.E[p]:
                        if q not in self.ranks:
                            break
                    else:
                        self.ranks[p] = k
                        added = True
            if added == False:
                # W(i+1, j) = W(i, j): we need to increment j
                for p in self.V:
                    if p not in self.ranks and self.marks[p] == 1:
                        is_found_in = False
                        is_found_not_in = False
                        for q in self.E[p]:
                            if q in self.ranks:
                                is_found_in = True
                            else:
                                is_found_not_in = True
                        if is_found_in == True and is_found_not_in == True:
                            self.ranks[p] = k
                            added = True
            k += 1

        # Remember ranks has been computed
        self.ranks_computed = False

    def winning_strategy(self):
        ''' Compute the winning strategy '''

        # Get sure ranks has been computed
        if (self.ranks_computed == False):
            self.compute_ranks()

        res = {}

        for node in self.V:
            if self.marks[node] == -1:
                if node == "errorB":
                    res[node] = "tau"
                else:
                    tr = None
                    lowest_rank = None
                    # Check each possible transition
                    for (src, label), dest in self.T.items():
                        if src != node:
                            continue
                        if lowest_rank == None or (self.ranks[dest] < lowest_rank):
                            tr = label
                            lowest_rank = self.ranks[dest]
                    res[node] = tr

        return res

    def compute_couples_ranks(self):
        ''' Compute couples ranks '''

        # Get sure the graph is bipartite
        if not(self.is_bipartite):
            self.to_bipartite()

        #Initialize W and the rank dictionary
        self.W = [[],[self.t]]
        Wmemory = [] #List keeping in memory the previous iteration of W[-1]
        self.rankdic = {self.t: (0,0)}
        i,j = 0,0

        while self.W[-1] != Wmemory:
            j+=1
            Wmemory = self.W[-1][:]
            for p in filter(lambda x: x not in Wmemory, self.V):
                if self.marks[p]==-1:
                    for q in self.E[p]:
                        if q in Wmemory:
                            self.W[-1].append(p)
                            self.rankdic[p] = (i,j)
                            break
                else:
                    b = True
                    for q in self.E[p]:
                        if self.marks[q]==-1 and q not in Wmemory:
                            b = False
                            break
                    if b:
                        self.W[-1].append(p)
                        self.rankdic[p] = (i,j)

        while self.W[-1] != self.W[-2]:
            i+=1
            j=0
            self.W.append(self.W[-1][:])
            for p in filter(lambda x: x not in self.W[-2], self.V):
                if self.marks[p]==1:
                    b1,b2 = False,False
                    for q in self.E[p]:
                        if q in self.W[-2]:
                            b1 = True
                        else:
                            b2 = True
                    if b1 and b2:
                        self.W[-1].append(p)
                        self.rankdic[p] = (i,j)

            while self.W[-1] != Wmemory:
                j+=1
                Wmemory = self.W[-1][:]
                for p in filter(lambda x: x not in Wmemory, self.V):
                    if self.marks[p]==-1:
                        for q in self.E[p]:
                            if q in Wmemory:
                                self.W[-1].append(p)
                                self.rankdic[p] = (i,j)
                                break
                    else:
                        b = True
                        for q in self.E[p]:
                            if self.marks[q]==-1 and q not in Wmemory:
                                b = False
                                break
                        if b:
                            self.W[-1].append(p)
                            self.rankdic[p] = (i,j)
        self.W.pop(0)
        self.W.pop()
        for p in filter(lambda x: x not in self.W[-1], self.V):
            self.rankdic[p]= (inf,inf)


A = Automaton('input_file')

print(A.winning_strategy())

# A.compute_couples_ranks()
# print(A.rankdic)
# print(A.W)

# TODO: check if problem with error nodes
