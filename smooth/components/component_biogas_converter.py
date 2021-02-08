import oemof.solph as solph
from .component import Component


class BiogasConverter(Component):
    """
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

        self.heating_value_bg = ((self.ch4_share * self.mol_mass_ch4) /
                                 ((self.ch4_share * self.mol_mass_ch4) +
                                  (self.co2_share * self.mol_mass_co2))) * self.heating_value_ch4

    def create_oemof_model(self, busses, _):
        """Creates an oemof Source component from the information given in the Supply
        class, to be used in the oemof model.

        :param busses: List of the virtual buses used in the energy system
        :type busses: list
        :return: 'from_grid' oemof component
        """
        biogas_converter = solph.Source(
            label=self.name,
            inputs={busses[self.bg_in]: solph.Flow()},
            outputs={busses[self.bg_out]: solph.Flow()},
            conversion_factors={busses[self.bg_out]: self.kwh_1m3_bg / self.heating_value_bg}
        )
        return biogas_converter