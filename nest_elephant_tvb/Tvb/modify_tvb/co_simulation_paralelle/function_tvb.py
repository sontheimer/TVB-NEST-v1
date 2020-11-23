# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2020, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#
import nest_elephant_tvb.Tvb.tvb_git.scientific_library.tvb.simulator.lab as lab
import numpy as np
import numpy.random as rgn
from nest_elephant_tvb.Tvb.modify_tvb.Interface_co_simulation_parallel import Interface_co_simulation

rgn.seed(42)


def tvb_model(dt, weight, delay, id_proxy):
    """
        Initialise TVB with Wong-Wang models and default connectivity

        WARNING : in this first example most of the parameter for the simulation is define. In the future, this function
        will be disappear and replace only by the tvb_init. This function is only here in order to constraint the usage
         of proxy
    :param dt: the resolution of the raw monitor (ms)
    :param weight: weight on the connexion
    :param delay: delay on the connexion
    :param id_proxy: id of the proxy
    :return:
        populations: model in TVB
        white_matter: Connectivity in TVB
        white_matter_coupling: Coupling in TVB
        heunint: Integrator in TVB
        what_to_watch: Monitor in TVB
    """
    region_label = np.repeat(['real'], len(weight))  # name of region fixed can be modify for parameter of function
    region_label[id_proxy] = 'proxy'
    populations = lab.models.ReducedWongWang()
    white_matter = lab.connectivity.Connectivity(region_labels=region_label,
                                                 weights=weight,
                                                 speed=np.array(1.0),
                                                 tract_lengths=delay,
                                                 # TVB don't take care about the delay only the track length and speed
                                                 #  delai = tract_lengths/speed
                                                 centres=np.ones((weight.shape[0], 3))
                                                 )
    white_matter_coupling = lab.coupling.Linear(a=np.array(0.0154))
    heunint = lab.integrators.HeunDeterministic(dt=dt, bounded_state_variable_indices=np.array([0]),
                                                state_variable_boundaries=np.array([[0.0, 1.0]]))
    return populations, white_matter, white_matter_coupling, heunint, id_proxy


def tvb_init(parameters, time_synchronize, initial_condition):
    """
        To initialise Nest and to create the connectome model
    :param parameters : (model,connectivity,coupling,integrator) : parameter for the simulation without monitor
    :param time_synchronize : the time of synchronization for the proxy
    :param initial_condition: the initial condition of the model
    :return:
        sim : the TVB simulator,
        (weights_in,delay_in): the connectivity of disconnect region input
        (weights_out,delay_out): the connectivity of disconnect region ouput
    """
    model, connectivity, coupling, integrator, id_proxy = parameters
    # Initialise some Monitors with period in physical time
    monitors = (lab.monitors.Raw(variables_of_interest=np.array(0)),
                Interface_co_simulation(id_proxy=np.asarray(id_proxy, dtype=np.int), time_synchronize=time_synchronize))

    # Initialise a Simulator -- Model, Connectivity, Integrator, and Monitors.
    sim = lab.simulator.Simulator(model=model,
                                  connectivity=connectivity,
                                  coupling=coupling,
                                  integrator=integrator,
                                  monitors=monitors,
                                  initial_conditions=initial_condition
                                  )
    sim.configure()
    return sim


def tvb_simulation(time, sim, data_proxy):
    """
    Simulate t->t+dt:
    :param time: the time of simulation
    :param sim: the simulator
    :param data_proxy : the firing rate of the next steps
    :return:
        the time, the firing rate and the state of the network
    """
    if data_proxy is not None:
        data_proxy[1] = np.reshape(data_proxy[1], (data_proxy[1].shape[0], data_proxy[1].shape[1], 1, 1))
    result = sim.run(proxy_data=data_proxy, simulation_length=time)
    time = result[0][0]
    s = result[0][1][:, 0]
    return time, s


class TvbSim:

    def __init__(self, weight, delay, id_proxy, resolution_simulation, time_synchronize, initial_condition=None):
        """
        initialise the simulator
        :param weight: weight on the connexion
        :param delay: delay of the connexions
        :param id_proxy: the id of the proxy
        :param resolution_simulation: the resolution of the simulation
        :param initial_condition: initial condition for S and H
        """
        self.nb_node = weight.shape[0] - len(id_proxy)
        model = tvb_model(resolution_simulation, weight, delay, id_proxy)
        self.sim = tvb_init(model, time_synchronize, initial_condition)

    def __call__(self, time, proxy_data=None):
        """
        run simulation for t biological
        :param time: the time of the simulation
        :param proxy_data: the firing rate fo the next steps for the proxy
        :return:
            the result of time, the firing rate and the state of the network
        """
        time, s_out = tvb_simulation(time, self.sim, proxy_data)
        return time, s_out
