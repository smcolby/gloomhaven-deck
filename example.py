import numpy as np
import gloomhaven as gh


def attack(mn=2, mx=6):
    '''Function to define expected base attack value.'''

    return np.random.randint(mn, mx)


if __name__ == '__main__':
    # setup deck
    base = gh.Deck()
    base.apply_upgrades(['remove two -1 cards',
                         'remove two -1 cards'])

    # simulate base deck
    base_diff = base.simulate(attack, n=int(1e5))

    # options
    options = list(set(base.options))
    options.sort()
    for opt in options:
        # initialize
        d = base.copy()

        # upgrade deck
        d.upgrade(option=opt)

        # simulate
        diff = d.simulate(attack, n=int(1e5))

        # display result
        print('%s:' % opt)
        print('%.2f%%\n' % (100 * (diff - base_diff)))
