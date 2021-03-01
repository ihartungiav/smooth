"""
This module represents a hydrogen compressor.

******
Scope
******
A hydrogen compressor is used in energy systems as a means of increasing
the pressure of hydrogen to suitable levels for feeding into other components
in the system or satisfying energy demands.

*******
Concept
*******
The hydrogen compressor is powered by electricity and intakes a low
pressure hydrogen flow while outputting a hgh pressure hydrogen flow.
The efficiency of the compressor is assumed to be 88.8%.

.. figure:: /images/hydrogen_compressor.png
    :width: 60 %
    :alt: hydrogen_compressor.png
    :align: center

    Fig.1: Simple diagram of a hydrogen compressor.

Specific compression energy
---------------------------
The specific compression energy is calculated by first obtaining the
compression ratio:

.. math::
    p_{ratio} = \\frac{p_{out}}{p_{in}}

* :math:`p_{ratio}` = compression ratio
* :math:`p_{out}` = outlet pressure [bar]
* :math:`p_{in}` = inlet pressure [bar]

Then the output temperature is calculated, and the initial assumption
for the polytropic exponent is assumed to be 1.6:

.. math::
    T_{out} = min(max(T_{in}, T_{in} \\cdot p_{ratio} ^ \\frac{n_{init} - 1}{n_{init}}),
    T_{in} + 60)

* :math:`T_{out}` = output temperature [K]
* :math:`T_{in}` = input temperature [K]
* :math:`n_{init}` = initial polytropic exponent

Then the temperature ratio is calculated:

.. math::
    T_{ratio} = \\frac{T_{out}}{T_{in}}

* :math:`T_{ratio}` = temperature ratio

Then the polytropic exponent is calculated:

.. math::
    n = \\frac{1}{1 - \\frac{log_{T_{ratio}}}{log_{p,ratio}}}

The compressibility factors of the hydrogen entering and leaving
the compressor is then calculated using interpolation considering
varying temperature, pressure and compressibility factor values
(see the calculate_compressibility_factor function). The real
gas compressibility factor is calculated using these two values
as follows:

.. math::
    Z_{real} = \\frac{Z_{in} + Z_{out}}{2}

* :math:`Z_{real}` = real gas compressibility factor
* :math:`Z_{in}` = compressibility factor on entry
* :math:`Z_{out}` = compressibility factor on exit

Thus the specific compression work is finally calculated:

.. math::
    c_{w_{1}} = \\frac{1}{\\mu} \\cdot R_{H_{2}} \\cdot T_{in} \\cdot \\frac{n}{n-1}
    \\cdot p_{ratio} ^ {(\\frac{n-1}{n} -1)} \\cdot \\frac{Z_{real}}{1000}

* :math:`c_{w_{1}}` = specific compression work [kJ/kg]
* :math:`\\mu` = compression efficiency
* :math:`R_{H_{2}}` = hydrogen gas constant

Finally, the specific compression work is converted into the amount of
electrical energy required to compress 1 kg of hydrogen:

.. math::
    c_{w_{2}} = \\frac{c_{w_{1}}}{3.6}

* :math:`c_{w_{2}}` = specific compression energy [Wh/kg]

"""

import oemof.solph as solph
from .component import Component
from math import log
import numpy as np
from scipy import interpolate


def calculate_compressibility_factor(p_in, p_out, temp_in, temp_out):
    """Calculates the compressibility factor through interpolation.

    :param p_in: inlet pressure [bar]
    :type p_in: numerical
    :param p_out: outlet pressure [bar]
    :type p_out: numerical
    :param temp_in: inlet temperature of the hydrogen [K]
    :type temp_in: numerical
    :param temp_out: outlet temperature of the hydrogen [K]
    :type temp_out: numerical
    """
    temp = np.transpose([200, 300, 400, 500, 600, 800, 1000, 2000])

    p = [1, 10, 20, 40, 60, 80, 100, 200, 400, 600, 800, 1000]

    z = [
        [1.0007, 1.0066, 1.0134, 1.0275, 1.0422, 1.0575, 1.0734, 1.163, 1.355, 1.555, 1.753, 1.936],
        [1.0005, 1.0059, 1.0117, 1.0236, 1.0357, 1.0479, 1.0603, 1.124, 1.253, 1.383, 1.510, 1.636],
        [1.0004, 1.0048, 1.0096, 1.0192, 1.0289, 1.0386, 1.0484, 1.098, 1.196, 1.293, 1.388, 1.481],
        [1.0004, 1.0040, 1.0080, 1.0160, 1.0240, 1.0320, 1.0400, 1.080, 1.159, 1.236, 1.311, 1.385],
        [1.0003, 1.0034, 1.0068, 1.0136, 1.0204, 1.0272, 1.0340, 1.068, 1.133, 1.197, 1.259, 1.320],
        [1.0002, 1.0026, 1.0052, 1.0104, 1.0156, 1.0208, 1.0259, 1.051, 1.100, 1.147, 1.193, 1.237],
        [1.0002, 1.0021, 1.0042, 1.0084, 1.0126, 1.0168, 1.0209, 1.041, 1.080, 1.117, 1.153, 1.187],
        [1.0009, 1.0013, 1.0023, 1.0044, 1.0065, 1.0086, 1.0107, 1.021, 1.040, 1.057, 1.073, 1.088],
    ]

    interp_func = interpolate.interp2d(p, temp, z)

    z_in = interp_func(p_in, temp_in)
    z_out = interp_func(p_out, temp_out)

    return [z_in, z_out]


class CompressorH2(Component):
    """
    :param name: unique name given to the compressor component
    :type name: str
    :param bus_h2_in: lower pressure hydrogen bus that is an input of
        the compressor
    :type bus_h2_in: str
    :param bus_el: electricity bus that is an input of the compressor
    :type bus_el: str
    :param bus_h2_out: higher pressure hydrogen bus that is the output
        of the compressor
    :type bus_h2_out: str
    :param m_flow_max: maximum mass flow through the compressor [kg/h]
    :type m_flow_max: numerical
    :param life_time: life time of the component [a]
    :type life_time: numerical
    :param temp_in: temperature of hydrogen on entry to the compressor [K]
    :type temp_in: numerical
    :param efficiency: overall efficiency of the compressor [-]
    :type efficiency: numerical
    :param set_parameters(params): updates parameter default values
        (see generic Component class)
    :type set_parameters(params): function
    :param spec_compression_energy: specific compression energy
        (electrical energy needed per kg H2) [Wh/kg]
    :type spec_compression_energy: numerical
    :param R: gas constant (R) [J/(K*mol)]
    :type R: numerical
    :param Mr_H2: molar mass of H2 [kg/mol]
    :type Mr_H2: numerical
    :param R_H2: specific gas constant for H2 [J/(K*kg)]
    :type R_H2: numerical
    """

    def __init__(self, params):
        """Constructor method
        """
        # Call the init function of th mother class.
        Component.__init__(self)
        # ------------------- PARAMETERS -------------------
        self.name = 'Compressor_default_name'
        self.bus_h2_in = None
        self.bus_h2_out = None
        self.bus_el = None
        self.m_flow_max = 33.6
        self.life_time = 20
        # It is assumed that hydrogen always enters the compressor at room temperature [K]
        self.temp_in = 293.15
        # value taken from MATLAB
        self.efficiency = 0.88829

        # ------------------- UPDATE PARAMETER DEFAULT VALUES -------------------
        self.set_parameters(params)

        # ------------------- ENERGY NEED FOR COMPRESSION -------------------
        # Specific compression energy (electrical energy needed per kg H2) [Wh/kg].
        self.spec_compression_energy = None

        # ------------------- CONSTANT PARAMETERS -------------------
        # Mr_H2 = Molar mass of H2 [kg/mol], R = the gas constant (R) [J/(K*mol)]
        self.R = 8.314
        self.Mr_H2 = 2.016 * 1e-3
        self.R_H2 = self.R / self.Mr_H2

    def create_oemof_model(self, busses, _):
        """Creates an oemof Transformer component using the information given in
        the CompressorH2 class, to be used in the oemof model

        :param busses: virtual buses used in the energy system
        :type busses: list
        :return: the oemof compressor component
        """
        compressor = solph.Transformer(
            label=self.name,
            inputs={
                busses[self.bus_h2_in]: solph.Flow(
                    nominal_value=self.m_flow_max * self.sim_params.interval_time / 60),
                busses[self.bus_el]: solph.Flow()},
            outputs={busses[self.bus_h2_out]: solph.Flow()},
            conversion_factors={
                busses[self.bus_h2_in]: 1,
                busses[self.bus_el]: self.spec_compression_energy,
                busses[self.bus_h2_out]: 1})

        return compressor

    def prepare_simulation(self, components):
        """Prepares the simulation by calculating the specific compression energy

        :param components: list containing each component object
        :type components: list
        :return: the specific compression energy [Wh/kg]
        """
        # The compressor has two foreign states, the inlet pressure and the
        # outlet pressure. Usually this is the storage pressure of the storage
        # at that bus. But a fixed pressure can also be set.

        # Get the inlet pressure [bar].
        p_in = self.get_foreign_state_value(components, 0)
        # Get the outlet pressure [bar].
        p_out = self.get_foreign_state_value(components, 1)

        # If the pressure difference is lower than 0.01 [bar], the specific
        # compression energy is zero
        if p_out - p_in < 0.01:
            spec_compression_work = 0
        else:
            # Get the compression ratio [-]
            p_ratio = p_out / p_in

            # Initial assumption for the polytropic exponent, value taken from MATLAB [-]
            n_initial = 1.6
            # Calculates the output temperature [K]
            temp_out = min(max(self.temp_in,
                               self.temp_in * p_ratio ** ((n_initial - 1) / n_initial)),
                           self.temp_in + 60)
            # Get temperature ratio [-]
            temp_ratio = temp_out / self.temp_in
            # Calculates the polytropic exponent [-]
            n = 1 / (1 - (log(temp_ratio) / log(p_ratio)))
            # Gets the compressibility factors of the hydrogen entering and
            # leaving the compressor [-]
            [z_in, z_out] = calculate_compressibility_factor(p_in, p_out, self.temp_in, temp_out)
            real_gas = (z_in + z_out) / 2
            # Specific compression work [kJ/kg]
            spec_compression_work = (
                (1 / self.efficiency) *
                self.R_H2 *
                self.temp_in *
                (n / (n - 1)) *
                ((((p_ratio) ** ((n - 1) / n))) - 1) *
                real_gas) / 1000

        # Convert specific compression work into electrical energy needed per kg H2 [Wh/kg]
        self.spec_compression_energy = float(spec_compression_work / 3.6)

    def update_states(self, results):
        """Updates the states in the compressor component

        :param results: oemof results object for the given time step
        :type results: object
        :return: updated values for each state in the 'states' dict
        """
        # Update the states of the compressor

        # If the states dict of this object wasn't created yet, it's done here.
        if 'specific_compression_work' not in self.states:
            self.states['specific_compression_work'] = [None] * self.sim_params.n_intervals

        self.states['specific_compression_work'][self.sim_params.i_interval] \
            = self.spec_compression_energy
