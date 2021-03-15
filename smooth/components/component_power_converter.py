"""
This module represents a generic power converter. It can be used to model AC-DC, DC-AC, AC-AC or
DC-DC converters.

******
Scope
******
Power converters play an important role in diverse renewable energy
systems, by regulating and shaping electrical signals in the
appropriate forms for other components in the system and the demands.

*******
Concept
*******
A simple power converter component is created which intakes an AC or DC electric bus and transforms
it into a different AC or DC electric bus with an assumed constant efficiency. The default
efficiency is taken to be 95%, as stated in [1][2] for AC-DC converters.
In [3] the efficiency for a DC-AC converter is given with 99%. This value should hence be modified
by the user in the model definition. The amount of electricity that can leave the converter is
limited by the defined maximum power.

.. figure:: /images/power_converter.png
    :width: 60 %
    :alt: power_converter.png
    :align: center

    Fig.1: Simple diagram of a power converter.

References
----------
[1] Harrison, K.W. et. al. (2009). The Wind-to-Hydrogen Project: Operational Experience,
Performance Testing, and Systems Integration, NREL.
https://www.nrel.gov/docs/fy09osti/44082.pdf
[2] Hayashi, Y. (2013). High Power Density Rectifier for Highly Efficient Future DC
Distribution System, NTT Facilities Japan.
[3] Sunny Highpower PEAK3 inverter (see manufacturer PDF)
"""

import oemof.solph as solph
from .component import Component


class PowerConverter(Component):
    """
    :param name: unique name given to the AC-DC converter component
    :type name: str
    :param bus_input: electric input bus the converter is connected to
    :type bus_input: str
    :param bus_output: electric output bus the converter is connected to
    :type bus_output: str
    :param output_power_max: maximum output power [W]
    :type output_power_max: numerical
    :param efficiency: efficiency of the converter
    :type efficiency: numerical

    """

    def __init__(self, params):
        """Constructor method
        """
        # Call the init function of the mother class.
        Component.__init__(self)

        # ------------------- PARAMETERS -------------------
        self.name = "power converter default name"
        # Define the AC electric bus the converter is connected to
        self.bus_input = None
        # Define the DC electric bus the converter is connected to
        self.bus_output = None

        # Max. output power [W]
        self.output_power_max = 10000

        # The efficiency of an AC-DC converter
        self.efficiency = 0.95

        self.set_parameters(params)

    def add_to_oemof_model(self, busses, model):
        """Creates an oemof Transformer component using the information given in
        the PowerConverter class, to be used in the oemof model

        :param busses: virtual buses used in the energy system
        :type busses: dict
        :param model: current oemof model
        :type model: oemof model
        :return: oemof component
        """
        power_converter = solph.Transformer(
            label=self.name,
            inputs={busses[self.bus_input]: solph.Flow()},
            outputs={busses[self.bus_output]: solph.Flow(
                nominal_value=self.output_power_max
            )},
            conversion_factors={busses[self.bus_output]: self.efficiency})

        model.add(power_converter)
        return power_converter
