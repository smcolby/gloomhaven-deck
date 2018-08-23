import numpy as np
from copy import deepcopy


class Deck(list):
    def __init__(self):
        '''Constructor and deck meta information.'''

        self.idx = 0
        self.options = ['remove two -1 cards',
                        'remove two -1 cards',
                        'remove four +0 cards',
                        'replace one -2 card with one +0 card',
                        'replace one -1 card with one +1 card',
                        'replace one +0 card with one +2 card',
                        'replace one +0 card with one +2 card',
                        'ignore negative scenario effects',
                        'add two rolling +1 cards']
        self.special = {'bless': 99,
                        '2x': 98,
                        'curse': -99,
                        'null': -98,
                        'rolling +1': 97}
        self.immune = False
        self.generate_std()

    def generate_std(self):
        '''Generate standard attack deck.'''

        self.extend([0 for x in range(6)])
        self.extend([1 for x in range(5)])
        self.extend([-1 for x in range(5)])
        self.append(2)
        self.append(-2)
        self.append(self.special['2x'])
        self.append(self.special['null'])

    def shuffle(self):
        '''Shuffles the deck in place.'''

        np.random.shuffle(self)
        self.idx = 0

    def draw(self):
        '''Draw a card from the deck, shuffling if necessary.'''

        if self.idx + 1 > len(self):
            self.shuffle()

        card = self[self.idx]
        self.idx += 1

        return card

    def evaluate(self, base):
        '''Evaluate an attack event.'''

        # draw card
        card = self.draw()

        # rolling bonus
        if card == self.special['rolling +1']:
            return self.evaluate(base + 1)

        # check for shuffle events
        elif (card == self.special['null']) or (card == self.special['2x']):
            self.shuffle()

        # check for removable cards
        elif (card == self.special['bless']) or (card == self.special['curse']):
            self.remove_card(card)
            self.idx -= 1

        # evaluate
        if (card == self.special['bless']) or (card == self.special['2x']):
            return base * 2
        elif (card == self.special['curse']) or (card == self.special['null']):
            return 0
        else:
            return max([base + card, 0])

    def remove_card(self, card):
        '''Remove card from deck.'''

        self.remove(card)

    def add_card(self, card):
        '''Add card to deck.'''

        self.append(card)

    def upgrade(self, option):
        '''Apply a single upgrade.'''

        if option == 'base deck':
            pass
        elif option == 'remove two -1 cards':
            for i in range(2):
                self.remove_card(-1)
        elif option == 'remove four +0 cards':
            for i in range(4):
                self.remove_card(0)
        elif option == 'replace one -2 card with one +0 card':
            self.remove_card(-2)
            self.add_card(0)
        elif option == 'replace one -1 card with one +1 card':
            self.remove_card(-1)
            self.add_card(1)
        elif option == 'replace one +0 card with one +2 card':
            self.remove_card(0)
            self.add_card(2)
        elif option == 'ignore negative scenario effects':
            self.immune = True
        elif option == 'add two rolling +1 cards':
            for i in range(2):
                self.add_card(self.special['rolling +1'])

    def apply_upgrades(self, upgrades):
        '''Applies list of upgrades in batch.'''

        for u in upgrades:
            if u in self.options:
                self.options.remove(u)
                self.upgrade(u)
            else:
                print('"%s" not available. Ignoring.' % u)

    def copy(self):
        '''Returns a copy of the deck in its current state.'''

        return deepcopy(self)

    def bless(self, n=1):
        '''Adds bless card(s) to the deck.'''

        for i in range(n):
            self.add_card(self.special['bless'])
        self.shuffle()

    def curse(self, card='curse', n=1):
        '''Adds curse cards to the deck, if not immune to effects.'''

        if not self.immune:
            for i in range(n):
                if card == 'curse':
                    self.add_card(self.special['curse'])
                else:
                    self.add_card(card)
            self.shuffle()

    def simulate(self, base_func, n=1000, seed=747, hand_size=9,
                 bless=0, curse=0, curse_type='curse'):
        '''Evaluate deck utility through repeated card draws.'''

        np.random.seed(seed)
        nturns = duration(hand_size)

        deck = self.copy()
        deck.shuffle()

        if bless > 0:
            deck.bless(n=bless)
        if curse > 0:
            deck.curse(card=curse_type, n=curse)

        res = []
        bases = []
        for i in range(n):
            if (i % nturns) == 0:
                d = deck.copy()
                d.shuffle()

            base = base_func()
            bases.append(base)
            res.append(d.evaluate(base))

        final = np.array(res)
        initial = np.array(bases)

        return (final.mean() - initial.mean()) / initial.mean()


def duration(hand_size):
    '''Calculates expected number of turns based on hand size.'''

    i = 0
    while hand_size > 1:
        i += hand_size // 2
        hand_size -= 1

    return i
