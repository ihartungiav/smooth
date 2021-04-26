"""
This module represents a biogas steam methane reformer that produces hydrogen,
combined with the pressure swing adsorption process to produce 99.9 %
pure hydrogen.

*****
Scope
*****
The primary production of hydrogen is currently from the process
of steam methane reforming (SMR), using natural gas as the feed material. Biogas
can be used as an alternative feed material, which has a similar composition to
natural gas. The utilisation of biogas can be beneficial due to biogas
being a renewable resource, and its usage can lead to less methane emissions
in the atmosphere. Pressure swing adsorption (PSA) is a process used in
combination with SMR to purify the output hydrogen stream to a level of
approximately 99.9 % [1].

*******
Concept
*******
The biogas SMR PSA component takes in a biogas bus and electricity bus as
inputs, with a hydrogen bus output. An oemof Transformer component is
chosen for this component, and is illustrated in Figure 1.

.. figure:: /images/steam_methane_reformer.png
    :width: 60 %
    :alt: steam_methane_reformer.png
    :align: center

    Fig.1: Simple diagram of a biogas steam methane reformer

Hydrogen production from SMR
----------------------------
The amount of hydrogen produced in SMR from the chosen composition
of biogas is calculated based on results from [2]. The default amount of
input fuel required to produce 1kg of H2 is 45.977 kWh, and using
this value along with the LHV of biogas, the amount of biogas
required to produce 1kg of H2 is determined:

.. math::
    Bg_{kg H2} = \\frac{fuel_{kg H2}}{LHV_{Bg}}

* :math:`Bg_{kg H2}` = biogas required to produce one kg H2 [kg]
* :math:`fuel_{kg H2}` = specific fuel consumption per kg of H2 produced [kWh/kg]
* :math:`LHV_{Bg}` = heating value of biogas [kWh/kg]

In order to calculate how much hydrogen will be produced in SMR from the input
amount of biogas, the conversion efficiency is calculated:

.. math::
    smr_{eff} = \\frac{1}{Bg_{kg H2}}

* :math:`smr_{eff}` = conversion efficiency of biogas to hydrogen in SMR process [-]

Hydrogen purification with PSA
------------------------------
The hydrogen produced in SMR contains many impurities such as carbon dioxide
and carbon monoxide, and these can be removed using the PSA process.
The default efficiency of the PSA process is taken to be 90 % [3], so the
overall efficiency of the SMR PSA process is determiend by:

.. math::
    overall_{eff} = smr_{eff} \\cdot psa_{eff}

* :math:`overall_{eff}` = overall efficiency of biogas to 99.9 % pure hydrogen in
  SMR and PSA process [-]
* :math:`psa_{eff}` = efficiency of inpure to pure hydrogen is PSA process [-]

Energy consumption
-----------------------
The default energy consumption of the combined SMR and PSA process per kg of
H2 produced is 5.557 kWh/kg [1]. Thus the energy consumption per kg of biogas
 used is:

.. math::
    EC_{kg Bg} = \\frac{5.557}{Bg_{kg H2}} * 1000

* :math:`EC_{kg Bg}` = energy required per kg of biogas used [Wh/kg]

References
----------
[1] Song, C. et.al. (2015). Optimization of steam methane reforming coupled
with pressure swing adsorption hydrogen production process by heat integration,
Applied Energy.
[2] Minh, D. P. et.al. (2018). Hydrogen Production From Biogas Reforming:
An Overview of Steam Reforming, Dry Reforming, Dual Reforming and
Tri-Reforming of Methane.
[3] Air Liquide Engineering & Construction (2021). Druckwechseladsorption
Wasserstoffreinigung Rückgewinnung und Reinigung von Wasserstoff durch PSA.
"""

from smooth.components.component import Component
import oemof.solph as solph


class BiogasSmrPsa(Component):
    """
    :param name: unique name given to the biogas SMR PSA component
    :type name: str
    :param bus_bg: biogas bus that is the input of the component
    :type bus_bg: str
    :param bus_el: electricity bus that is the input of the component
    :type bus_el: str
    :param bus_h2: 99.9 % pure hydrogen bus that is the output of the component
    :type bus_h2: str
    :param life_time: lifetime of the component [a]
    :type life_time: numerical
    :param input_max: maximum biogas input per interval [kg/*]
    :type input_max: numerical
    :param fuel_kwh_1kg_h2: specific fuel consumption per kg of H2 produced [kWh/kg]
    :type fuel_kwh_1kg_h2: numerical
    :param psa_eff: efficiency of the PSA process [-]
    :type psa_eff: numerical
    :param energy_cnsmp_1kg_h2: specific energy consumption of the combined SMR and PSA
        process in terms of hydrogen production [kWh/kg]
    :type energy_cnsmp_1kg_h2: numerical
    :param set_parameters(params): updates parameter default values (see generic Component
        class)
    :type set_parameters(params): function
    :param smr_psa_eff: total efficiency of biogas to 99.9 % pure hydrogen in SMR and
        PSA process [-]
    :type smr_psa_eff: numerical
    :param energy_cnsmp_1kg_bg: specific energy consumption of the combined SMR and PSA
        process in terms of biogas consumption [Wh/kg]
    :type energy_cnsmp_1kg_bg: numerical
    """

    def __init__(self, params):
        """Constructor method
        """
        # Call the init function of the mother class.
        Component.__init__(self)

        # ------------------- PARAMETERS -------------------
        self.name = 'Biogas_SMR_PSA_default_name'
        self.bus_bg = None
        self.bus_el = None
        self.bus_h2 = None
        self.life_time = 20
        self.input_max = 500
        self.fuel_kwh_1kg_h2 = 45.977
        self.psa_eff = 0.9
        self.energy_cnsmp_1kg_h2 = 5.557

        self.set_parameters(params)

        self.smr_psa_eff = None
        self.energy_cnsmp_1kg_bg = None

    def prepare_simulation(self, components):
        """Prepares the simulation by calculating the specific compression energy

        :param components: list containing each component object
        :type components: list
        :return: the specific compression energy [Wh/kg]
        """

        heating_value_bg = self.get_foreign_state_value(components, 0)
        bg_1kg_h2 = self.fuel_kwh_1kg_h2 / heating_value_bg
        smr_eff = 1 / bg_1kg_h2
        self.smr_psa_eff = smr_eff * self.psa_eff
        self.energy_cnsmp_1kg_bg = (5.557 / bg_1kg_h2) * 1000

    def add_to_oemof_model(self, busses, model):
        """Creates an oemof Transformer component using the information given in
        the BiogasSteamReformer class, to be used in the oemof model

        :param busses: buses used in the energy system
        :type busses: dict
        :param model: current oemof model
        :type model: oemof model
        :return: oemof component
        """
        biogas_smr_psa = solph.Transformer(
            label=self.name,
            inputs={busses[self.bus_bg]: solph.Flow(
                variable_costs=0),
                    busses[self.bus_el]: solph.Flow(
                        variable_costs=0
                    )},
            outputs={busses[self.bus_h2]: solph.Flow()},
            conversion_factors={busses[self.bus_h2]: self.smr_psa_eff,
                                busses[self.bus_el]: self.energy_cnsmp_1kg_bg}
                                )
        model.add(biogas_smr_psa)
        return biogas_smr_psa
