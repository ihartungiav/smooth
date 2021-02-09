"""
Simple gate component with efficiency
"""

import oemof.solph as solph
from .component import Component


class GateTemp(Component):
    """
    :param name: unique name given to the gate component
    :type name: str
    :param max_input: maximum value that the gate can intake per timestep
    :type max_input: numerical
    :param bus_in: bus that enters the gate component
    :type bus_in: str
    :param bus_out: bus that leaves the gate component
    :type bus_out: str
    :param set_parameters(params): updates parameter default values (see generic Component class)
    :type set_parameters(params): function
    """

    def __init__(self, params):
        """Constructor method
        """
        # Call the init function of the mother class.
        Component.__init__(self)

        # ------------------- PARAMETERS -------------------
        self.name = 'Gate_default_name'
        # Busses
        self.bus_in = None
        self.bus_out = None
        self.efficiency = None

        # ------------------- UPDATE PARAMETER DEFAULT VALUES -------------------
        self.set_parameters(params)

    def create_oemof_model(self, busses, _):
        """Creates an oemof Transformer component from information given in
        the Gate class, to be used in the oemof model

        :param busses: virtual buses used in the energy system
        :type busses: list
        :return: oemof 'gate' component
        """
        gate = solph.Transformer(
            label=self.name,
            inputs={busses[self.bus_in]: solph.Flow()},
            outputs={busses[self.bus_out]: solph.Flow()},
            conversion_factors={busses[self.bus_out]: self.efficiency}
        )
        return gate
