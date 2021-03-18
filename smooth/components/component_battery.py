"""
This module represents a stationary battery.

*****
Scope
*****
Batteries are crucial in effectively integrating high shares of renewable
energy electricity sources in diverse energy systems. They can be particularly
useful for off-grid energy systems, or for the management of grid stability
and flexibility. This flexibility is provided to the energy system by the
battery in times where the electric consumers cannot.

*******
Concept
*******
The battery component has an electricity bus input and output, where factors
such as the charging and discharging efficiency, the loss rate, the C-rates
and the depth of discharge define the electricity flows.

.. figure:: /images/battery.png
    :width: 60 %
    :alt: battery.png
    :align: center

    Fig.1: Simple diagram of a battery storage.

Wanted storage level
--------------------
Within this component, there is the possibility to choose a wanted
storage level that the energy system should try to maintain when it
feasibly can. If the state of charge level wanted is defined, the variable
artificial costs change depending on whether the storage level is above or
below the desired value. If the battery level is too low, the artificial
costs of storing electricity into the battery can be reduced and the costs
of extracting electricity from the battery can be increased to incentivise
the system to maintain the wanted storage level.

Maximum chargeable/dischargeable energy
---------------------------------------
The maximum power [W] going in to or out of the battery are dependent on
the C-rate and the capacity:

.. math::
    P_{in,max} = E_{cap} \\cdot C_{r,charge}

    P_{out,max} = E_{cap} \\cdot C_{r,discharge}

* :math:`P_{in,max}` = maximum power flowing from bus to battery [W]
* :math:`E_{cap}` = battery capacity [Wh]
* :math:`C_{r,charge}` = C-Rate for charging [W/Wh]
* :math:`P_{out,max}` = maximum power flowing from battery to bus [W]
* :math:`C_{r,discharge}` = C-Rate for discharging [W/Wh]

.. figure:: /images/battery_losses.png
    :width: 60 %
    :alt: battery.png
    :align: center

    Fig.2: Diagram of the battery component including losses.

The amount of energy that the battery will be charged or discharged
takes the energy losses during the (dis-)charging process into account:

.. math::
    P_{charge,max} = P_{in,max} \\cdot \\mu_{charge}

    P_{out,max} = P_{discharge,max} \\cdot \\mu_{discharge}

* :math:`P_{charge,max}` = maximum chargeable power at the battery [W]
* :math:`\\mu_{charge}` = charging efficiency [-]
* :math:`P_{discharge,max}` = maximum dischargeable power at the battery [W]
* :math:`\\mu_{discharge}` = discharging efficiency [-]
"""

import oemof.solph as solph
from .component import Component
from oemof.outputlib import views


class Battery(Component):
    """
    :param name: unique name given to the battery component
    :type name: str
    :param bus_in_and_out: electricity bus the battery is connected to
    :type bus_in_and_out: str
    :param battery_capacity: battery capacity (assuming all the capacity
        can be used) [Wh]
    :type battery_capacity: numerical
    :param soc_init: initial state of charge [-]
    :type soc_init: numerical
    :param efficiency_charge: charging efficiency [-]
    :type efficiency_charge: numerical
    :param efficiency_discharge: discharging efficiency [-]
    :type efficiency_discharge: numerical
    :param loss_rate: loss rate [%/day]
    :type loss_rate: numerical
    :param symm_c_rate: flag to indicate if the c-rate is symmetrical
    :type symm_c_rate: boolean
    :param c_rate_symm: C-Rate for charging and discharging (only used if symm_c_rate==True) [-/h]
    :type c_rate_symm: numerical
    :param c_rate_charge: C-Rate for charging [-/h]
    :type c_rate_charge: numerical
    :param c_rate_discharge: C-Rate for discharging [-/h]
    :type c_rate_discharge: numerical
    :param soc_min: minimal state of charge [-]
    :type soc_min: numerical
    :param life_time: life time of the component [a]
    :type life_time: numerical
    :param vac_in: normal variable artificial costs for charging (in)
        the battery [EUR/Wh]
    :type vac_in: numerical
    :param vac_out: normal variable artificial costs for discharging (out)
        the battery [EUR/Wh]
    :type vac_out: numerical
    :param soc_wanted: if a soc level is set as wanted, the vac_low costs
        apply if the capacity is below that level [Wh]
    :type soc_wanted: numerical
    :param vac_low_in: variable artificial costs that apply (in) if the capacity
        level is below the wanted capacity level [EUR/Wh]
    :type vac_low_in: numerical
    :param vac_low_out: variable artificial costs that apply (in) if the capacity
        level is below the wanted capacity level [EUR/Wh]
    :type vac_low_out: numerical
    :param set_parameters(params): updates parameter default values
        (see generic Component class)
    :type set_parameters(params): function
    :param soc: state of charge [-]
    :type soc: numerical
    :param p_in_max: max. chargeable power [W]
    :type p_in_max: numerical
    :param p_out_max: max. dischargeable power [W]
    :type p_out_max: numerical
    :param loss_rate: adjusted loss rate to chosen timestep [%/timestep]
    :type loss_rate: numerical
    :param current_vac: current artificial costs for input and output [EUR/Wh]
    :type current_vac: list
    """

    def __init__(self, params):
        """Constructor method
        """
        # Call the init function of the mother class.
        Component.__init__(self)

        # ------------------- PARAMETERS -------------------
        self.name = "Battery_default_name"

        self.bus_in_and_out = None
        self.battery_capacity = 5000
        self.soc_init = 0.5
        # Efficiency charge [-].
        self.efficiency_charge = 0.95
        self.efficiency_discharge = 0.95
        # Loss rate [%/day]
        self.loss_rate = 0
        # C-Rate [-/h].
        # If [symm_c_rate = True]: c_rate_symm is used for both c_rate_charge and c_rate_discharge
        self.symm_c_rate = False
        self.c_rate_symm = 1
        self.c_rate_charge = 1
        self.c_rate_discharge = 1
        # minimal state of charge [-].
        self.soc_min = 0.1
        # Life time [a].
        self.life_time = 20
        # ToDo: set default value for degradation over lifetime
        # Degradation over lifetime [%]
        # self.degradation =

        # ------------------- PARAMETERS (VARIABLE ARTIFICIAL COSTS - VAC) -------------------
        # Normal var. art. costs for charging (in) and discharging (out) the
        # battery [EUR/Wh]. vac_out should be set to a minimal value to ensure
        # that the supply for the demand is first satisfied by the renewables
        # (costs are 0), and second satisfied by the battery and last by the grid.
        self.vac_in = None
        self.vac_out = None
        self.soc_wanted = None
        self.vac_low_in = 0
        self.vac_low_out = 0

        # ------------------- UPDATE PARAMETER DEFAULT VALUES -------------------
        if 'dod' in params:
            raise ValueError(
                'The parameter dod was renamed as soc_min. Please change your model description.')
        self.set_parameters(params)
        # Raise an error if the initial state of charge [-] is below minimal state of charge [-].
        if self.soc_init < self.soc_min:
            raise ValueError(
                'Initial state of charge is set below minimal state of charge! '
                'Please adjust soc_init or soc_min.')
        if self.symm_c_rate:
            self.c_rate_charge = self.c_rate_symm
            self.c_rate_discharge = self.c_rate_symm

        # ------------------- STATES AND DERIVED PROPERTIES -------------------
        self.soc = self.soc_init
        # The in- / and outflow of power are calculated using the battery capacity and the C-rate
        self.p_in_max = self.c_rate_charge * self.battery_capacity
        self.p_out_max = self.c_rate_discharge * self.battery_capacity
        self.loss_rate = (self.loss_rate / 24) * (self.sim_params.interval_time / 60)

        # ------------------- VARIABLE ARTIFICIAL COSTS -------------------
        self.current_vac = [0, 0]

    def prepare_simulation(self, components):
        """Prepares the simulation by setting the appropriate artificial costs

        :param components: List containing each component object (unused in this component)
        :type components: list
        """
        # Set the var. art. costs.
        vac_in = self.vac_in
        vac_out = self.vac_out

        if self.soc_wanted is not None and self.soc < self.soc_wanted:
            # If a wanted storage level is set and the storage level drops
            # below that wanted level, the low VAC apply.
            vac_in = self.vac_low_in
            vac_out = self.vac_low_out

        self.current_vac = [vac_in, vac_out]

        # ToDo: efficiency depending on the soc

        # ToDo: c_rate depending on the soc

    def add_to_oemof_model(self, busses, model):
        """Creates an oemof Generic Storage component from the information given in
        the Battery class, to be used in the oemof model.

        :param busses: List of the virtual buses used in the energy system
        :type busses: list
        :param model: current oemof model
        :type model: oemof model
        :return: oemof component
        """
        battery = solph.components.GenericStorage(
            label=self.name,
            inputs={busses[self.bus_in_and_out]: solph.Flow(
                    nominal_value=self.p_in_max, variable_costs=self.current_vac[0])
                    },
            outputs={busses[self.bus_in_and_out]: solph.Flow(
                nominal_value=self.p_out_max, variable_costs=self.current_vac[1])
            },
            loss_rate=self.loss_rate,
            initial_storage_level=self.soc,
            nominal_storage_capacity=self.battery_capacity,
            min_storage_level=self.soc_min,
            inflow_conversion_factor=self.efficiency_charge,
            outflow_conversion_factor=self.efficiency_discharge,
            balanced=False,
        )
        model.add(battery)
        return battery

    def update_states(self, results):
        """Updates the states of the battery component for each time step

        :param results: oemof results for the given time step
        :type results: object
        :return: updated state values for each state in the 'state' dict
        """
        data_storage = views.node(results, self.name)
        df_storage = data_storage["sequences"]

        # Loop Through the data frame values and update states accordingly.
        for i_result in df_storage:
            if i_result[1] == "capacity":
                if "soc" not in self.states:
                    # Initialize a.n array that tracks the state SoC
                    self.states["soc"] = [None] * self.sim_params.n_intervals
                # Check if this result is the state of charge.
                self.soc = df_storage[i_result][0] / self.battery_capacity
                self.states["soc"][self.sim_params.i_interval] = self.soc
