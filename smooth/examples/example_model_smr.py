"""
This example illustrates a basic energy system with hydrogen production
from steam methane reforming, with a biogas supply as the input.

Biogas converter
----------------
The biogas converter component is used if the biogas supply is given
in m3, as the steam methane reformer component requires a kg input.
The percentage share of CH4 and CO2 in the biogas is defined, as
well as the energy content in 1m3 of biogas. As a result, the
amount of biogas supplied in kg is calculated. In the example below,
the percentage share or methane and carbon dioxide in the biogas is
65%/35%, respectively. It is also assumed that 1m3 of biogas is
the equivalent to 6.25 kWh.

.. code:: bash

components.append({
    'component': 'biogas_converter',
    'name': 'biogas_conv',
    'bg_in': 'bg_m3',
    'bg_out': 'bg_kg',
    'ch4_share': 0.65,  # methane content of 65%
    'co2_share': 0.35,
    'kwh_1m3_bg': 6.25  # Assumption 1 m³ biogas 5,0 – 7,5 kWh -> take 6,25 kWh
})

Biogas SMR + PSA
----------------
The biogas steam methane reforming with pressure swing adsorption component is
represented as shown below. Here, the maximum amount of biogas input per
time interval is 1000 kg, the amount of input fuel required to produce 1kg of
H2 in the process is the equivalent to 45.977 kWh, and the hydrogen recovery
from the PSA is 80%.

.. code:: bash

components.append({
    'component': 'biogas_smr_psa',
    'name': 'biogas_smr_psa',
    'bus_bg': 'bg_kg',
    'bus_el': 'bel',
    'bus_h2': 'bh2',
    'life_time': 20,
    'input_max': 1000,
    'fuel_kwh_1kg_h2': 45.977,
    'psa_eff': 0.8,
    # Foreign states
    'fs_component_name': ['biogas_conv'],
    'fs_attribute_name': ['heating_value_bg'],
    'capex': {
        'key': 'fix',
        'cost': 5000000,
        'fitting_value': 1,
        'dependant_value': None,
    },
    'opex': {
        'key': 'fix',
        'cost': 0.001 * 5000000,
        'fitting_value': 1,
        'dependant_value': None,
    }
})
"""

import os

# Define where Python should look for csv files
my_path = os.path.join(os.path.dirname(__file__), 'example_timeseries')

""" Create busses """
# create hydrogen bus
busses = ['bg_m3', 'bg_kg', 'bel', 'bh2', 'bh2_300', 'bh2_300_for_demand']


""" Define components """
components = list()

components.append({
    'component': 'supply',
    'name': 'biogas_supply',
    'bus_out': 'bg_m3',
    'output_max': 500,  # in m3/h
    'variable_costs': 10,
    'artificial_costs': 0,
    'dependency_flow_costs': ('biogas_supply', 'bg_m3')
})

components.append({
    'component': 'biogas_converter',
    'name': 'biogas_conv',
    'bg_in': 'bg_m3',
    'bg_out': 'bg_kg',
    'ch4_share': 0.65,  # methane content of 65%
    'co2_share': 0.35,
    'kwh_1m3_bg': 6.25  # Assumption 1 m³ biogas 5,0 – 7,5 kWh -> take 6,25 kWh
})

# Electricity supply
components.append({
    'component': 'supply',
    'name': 'elec_supply',
    'bus_out': 'bel',
    'output_max': 1000e9,
    'variable_costs': 18.55 / 100 / 1000,  # 18.55 ct/kWh
    'artificial_costs': 0,
    'dependency_flow_costs': ('elec_supply', 'bel'),
})

# Steam methane reformer + pressure swing adsorption
components.append({
    'component': 'biogas_smr_psa',
    'name': 'biogas_smr_psa',
    'bus_bg': 'bg_kg',
    'bus_el': 'bel',
    'bus_h2': 'bh2',
    'life_time': 20,
    'input_max': 1000,
    'fuel_kwh_1kg_h2': 45.977,
    'psa_eff': 0.8,
    # Foreign states
    'fs_component_name': ['biogas_conv'],
    'fs_attribute_name': ['heating_value_bg'],
    'capex': {
        'key': 'fix',
        'cost': 5000000,
        'fitting_value': 1,
        'dependant_value': None,
    },
    'opex': {
        'key': 'fix',
        'cost': 0.001 * 5000000,
        'fitting_value': 1,
        'dependant_value': None,
    }
})

# Compressor (40-300 bar)
# The maximum mass flow rate ('m_flow_max') parameter
# will be optimized in the optimization
components.append({
    'component': 'compressor_h2',
    'name': 'h2_compressor',
    # Busses
    'bus_h2_in': 'bh2',
    'bus_h2_out': 'bh2_300',
    # Parameters
    'bus_el': 'bel',
    'm_flow_max': 2000,
    'life_time': 20,
    # Foreign states
    'fs_component_name': [None, None],
    'fs_attribute_name': [15 + 1, 300],
    # Financials
    'capex': {
        'key': 'free',
        'fitting_value': [28063, 0.6378],
        'dependant_value': 'm_flow_max'
    },
    'opex': {
        'key': 'spec',
        'fitting_value': 0.04,
        'dependant_value': 'capex'
    }
})

# H2 storage (300 bar)
components.append({
    'component': 'storage_h2',
    'name': 'storage',
    'bus_in': 'bh2_300',
    'bus_out': 'bh2_300_for_demand',
    'p_min': 2.5,
    'p_max': 300,
    'storage_capacity': 300,   # MOEA
    'life_time': 20,
    'initial_storage_factor': 0.5,
    'vac_in': -100,
    'dependency_flow_costs': ('bh2_300', 'storage'),
    'capex': {
        'key': ['poly', 'spec'],
        'fitting_value': [[604.6, 0.5393], 'cost'],
        'dependant_value': ['p_max', 'storage_capacity']
    },
    'opex': {
        'key': 'spec',
        'fitting_value': 0.01,
        'dependant_value': 'capex'
    },
    'fix_emissions': {
        'key': ['poly', 'spec'],
        'fitting_value': [[68 / 5, 3 / 1750], 'cost'],
        'dependant_value': ['pressure', 'storage_capacity']
    }
})

# Gate H2
components.append({
    'component': 'gate',
    'name': 'storage_gate',
    'bus_in': 'bh2_300',
    'bus_out': 'bh2_300_for_demand',
    'max_input': 1000e3,
    'artificial_costs': -150,
    'dependency_flow_costs': ('bh2_300', 'storage_gate'),
})

# H2 Demand
components.append({
    'component': 'energy_demand_from_csv',
    'name': 'h2_demand',
    'bus_in': 'bh2_300_for_demand',
    'csv_filename': 'ts_demand_h2.csv',
    'nominal_value': 1,
    'column_title': 'Hydrogen load',
    'path': my_path
})

sim_params = {
    'start_date': '1/1/2019',
    'n_intervals': 10,
    'interval_time': 60,
    'interest_rate': 0.03,
    'print_progress': False,
    'show_debug_flag': False,
}

mymodel = {
    'busses': busses,
    'components': components,
    'sim_params': sim_params,
}
