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

    def __repr__(self):
        ''' Gives a nice view '''

        # TODO
        res = ''
        return res

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

    def winning_strategy(self):
        ''' Compute a winning strategy '''

        # Get sure the graph is bipartite
        if not(self.is_bipartite):
            self.to_bipartite()

        # TODO
        pass


A = Automaton('input_file')
A.to_bipartite()

print(A.V)
print(A.E)
print(A.marks)

# TODO
# Calcul de W, choix de représentation primordial
# Calcul des rangs, identification de la stratégie gagnante

# Indexer par des entiers ?
