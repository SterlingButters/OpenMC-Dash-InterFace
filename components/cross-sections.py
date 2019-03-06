import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns  # This optional package makes plots prettier

import openmc

library = openmc.data.DataLibrary.from_xml(os.environ['OPENMC_CROSS_SECTIONS'])
filename = library.get_by_material('U238')['path']
u238_pointwise = openmc.data.IncidentNeutron.from_hdf5(filename)

for r in u238_pointwise.reactions.values(): print(r)

n_gamma = u238_pointwise[102]

xs = n_gamma.xs['294K']
plt.loglog(xs.x, xs.y)

E = np.linspace(5, 25, 1000)
plt.semilogy(E, xs(E))
plt.show()

# filename = os.environ['OPENMC_MULTIPOLE_LIBRARY'] + '/092238.h5'
# u238_multipole = openmc.data.WindowedMultipole.from_hdf5(filename)
#
# u238_multipole(1.0, 294)
#
# E = np.linspace(5, 25, 1000)
# plt.semilogy(E, u238_multipole(E, 293.606)[1])
#
# E = np.linspace(6.1, 7.1, 1000)
# plt.semilogy(E, u238_multipole(E, 0)[1])
# plt.semilogy(E, u238_multipole(E, 900)[1])