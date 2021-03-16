"""
This module represents the conversion of a biogas input in m3 to kg, where the
biogas composition is defined.

*****
Scope
*****
The biogas converter component is a virtual component, so would not be found in
a real life energy system. Its purpose is to transform a biogas bus with m3 units
into a biogas bus with kg units. This might be necessary because the Biogas SMR
PSA component, for instance, requires a biogas input in kg.

*******
Concept
*******
The biogas converter component takes in a biogas bus as an input and outputs a
different biogas bus. The composition of the biogas is defined, as well as
the energy content per m3 of biogas.

Biogas composition
------------------
The user can determine the desired composition of biogas by stating the
percentage share of methane and carbon dioxide in the gas. The default
share is chosen to be 75.7% methane, 24.3% carbon dioxide [1]. The lower
heating value (LHV) of methane is 13.9 kWh/kg [2], and the molar masses
of methane and carbon dioxide are 0.01604 kg/mol and 0.04401 kg/mol,
respectively. The method used to calculate the LHV of biogas is the same
as in the Gas Engine CHP Biogas component, and the equation used is as follows:

.. math::
    LHV_{Bg} = \\frac{CH_{4_{share}} \\cdot M_{CH_{4}}}{CH_{4_{share}} \\cdot
    M_{CH_{4}} + CO_{2_{share}} \\cdot M_{CO_{2}}} \\cdot LHV_{CH_{4}} \n

* :math:`LHV_{Bg}` = heating value of biogas [kWh/kg]
* :math:`CH_{4_{share}` = proportion of methane in biogas [-]
* :math:`M_{CH_{4}}` = molar mass of methane [kg/mol]
* :math:`CO_{2_{share}}` = proportion of carbon dioxide in biogas [-]
* :math:`M_{CO_{2}}` = molar mass of carbon dioxide [kg/mol]
* :math:`LHV_{CH_{4}}` = heating value of methane [kWh/kg]

References
----------
[1] Braga, L. B. et.al. (2013). Hydrogen production by biogas steam reforming:
A technical, economic and ecological analysis, Renewable and Sustainable
Energy Reviews.
[2] Linde Gas GmbH (2013). Rechnen Sie mit Wasserstoff. Die Datentabelle.
"""


import oemof.solph as solph
from .component import Component


class BiogasConverter(Component):
    """
    :param name: unique name given to the biogas converter component
    :type name: str
    :param bg_in: input biogas bus
    :type bg_in: str
    :param bg_out: output biogas bus
    :type bg_out: str
    :param ch4_share: proportion of methane in biogas [-]
    :type ch4_share: numerical
    :param co2_share: proportion of carbon dioxide in biogas [-]
    :type co2_share: numerical
    :param kwh_1m3_bg: energy content in 1m3 biogas [kWh/m3]
    :type kwh_1m3_bg: numerical
    :param set_parameters(params): updates parameter default values
        (see generic Component class)
    :type set_parameters(params): function
    :param mol_mass_ch4: molar mass of methane [kg/mol]
    :type mol_mass_ch4: numerical
    :param mol_mass_co2: molar mass of carbon dioxide [kg/mol]
    :type mol_mass_co2: numerical
    :param heating_value_ch4: heating value of methane [kWh/kg]
    :type heating_value_ch4: numerical
    :param heating_value_bg: heating value of biogas [kWh/kg]
    :type heating_value_bg: numerical
    """

    def __init__(self, params):
        """Constructor method
        """
        # Call the init function of the mother class.
        Component.__init__(self)

        # ------------- PARAMETERS -----------------
        self.name = 'Biogas_converter_default_name'
        self.bg_in = None
        self.bg_out = None
        self.ch4_share = 0.757
        self.co2_share = 0.243
        self.kwh_1m3_bg = 6.25

        # ------------- UPDATE PARAMETER DEFAULT VALUES -------------
        self.set_parameters(params)

        if self.ch4_share + self.co2_share != 1:
            raise ValueError("addition of all shares must be 1")

        self.mol_mass_ch4 = 0.01604  # [kg/mol]
        self.mol_mass_co2 = 0.04401  # [kg/mol]
        self.heating_value_ch4 = 13.9

        self.heating_value_bg = (
                                        (self.ch4_share * self.mol_mass_ch4) /
                                        ((self.ch4_share * self.mol_mass_ch4)
                                         + (self.co2_share * self.mol_mass_co2))
                                ) * self.heating_value_ch4

        self.conv = self.kwh_1m3_bg / self.heating_value_bg

    def add_to_oemof_model(self, busses, model):
        """Creates an oemof Transformer component from the information given in the
        BiogasConverter class, to be used in the oemof model

        :param busses: virtual buses used in the energy system
        :type busses: dict
        :param model: current oemof model
        :type model: oemof model
        :return: oemof component
        """
        biogas_converter = solph.Transformer(
            label=self.name,
            inputs={busses[self.bg_in]: solph.Flow()},
            outputs={busses[self.bg_out]: solph.Flow()},
            conversion_factors={busses[self.bg_out]: self.conv}
        )
        model.add(biogas_converter)
        return biogas_converter
