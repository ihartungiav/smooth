"""
This example represents a simple electric energy system model definition.

1. The virtual busses to be used in the system are defined as a list. In this
example, an AC current electricity bus with medium voltage (*bel_ac_mv_grid*),
an AC current electricity bus with low voltage (*bel_ac_lv_grid*),
a DC current electricity bus connected to the battery (*bel_dc_bat*),
a DC current electricity bus connected to the PV system (*bel_dc_pv*),
and a thermal bus (*bth*) are used.

.. code:: bash

    busses = ['bel_ac_mv_grid', 'bel_ac_lv_grid', 'bel_dc_bat', 'bel_dc_pv', 'bth']

2. The components are created in a list. An example of a component being
added to the list is as follows:

.. code:: bash

    components.append({
        'component': 'supply',
        'name': 'from_grid',
        'bus_out': 'bel_ac_mv_grid',
        'output_max': 950 * 1e3,
        'variable_costs': 0.16 / 1000,
        'dependency_flow_costs': ('from_grid', 'bel_ac_mv_grid'),
        'life_time': 50,
    })

3. The simulation parameters are stated:

.. code:: bash

    sim_params = {
        'start_date': '1/1/2019',
        'n_intervals': 24,
        'interval_time': 60,
        'interest_rate': 0.03,
        'print_progress': True,
        'show_debug_flag': False,
    }

4. A model is created containing the above three elements

.. code:: bash

    mymodel = {
        'busses': busses,
        'components': components,
        'sim_params': sim_params
    }

Now this model definition is ready to be used in either a simulation or an
optimization.
"""
import os

# Define where Python should look for csv files
my_path = os.path.join(os.path.dirname(__file__), 'example_timeseries')

# Create busses list
busses = ['bel_ac_mv_grid', 'bel_ac_lv_grid', 'bel_dc_bat', 'bel_dc_pv', 'bth']

# Define components list
components = list()
components.append({
    'component': 'supply',
    'name': 'from_grid',
    'bus_out': 'bel_ac_mv_grid',
    'output_max': 950 * 1e3,
    'variable_costs': 0.16 / 1000,
    'dependency_flow_costs': ('from_grid', 'bel_ac_mv_grid'),
    'life_time': 50,
})

components.append({
    'component': 'sink',
    'name': 'to_grid',
    'bus_in': 'bel_ac_mv_grid',
    'artificial_costs': 10,
    'input_max': 1 * 1e6,
    'dependency_flow_costs': ('bel_ac_mv_grid', 'to_grid'),
})

components.append({
    'component': 'power_converter',
    'name': 'local_transformer_station',
    'bus_input': 'bel_ac_mv_grid',
    'bus_output': 'bel_ac_lv_grid',
    'output_power_max': 1 * 1e6,
    'efficiency': 0.98,
})

components.append({
    'component': 'energy_source_from_csv',
    'name': 'solar_output',
    'bus_out': 'bel_dc_pv',
    'csv_filename': 'ts_oemof_test_input_data.csv',
    'csv_separator': ',',
    'nominal_value': 1000000,
    'column_title': 'pv',
    'path': my_path
})

components.append({
    'component': 'power_converter',
    'name': 'dc_ac_inverter_pv',
    'bus_input': 'bel_dc_pv',
    'bus_output': 'bel_ac_lv_grid',
    'output_power_max': 800000,
    'efficiency': 0.98,
})

components.append({
    'component': 'energy_demand_from_csv',
    'name': 'ac_lv_demand',
    'bus_in': 'bel_ac_lv_grid',
    'csv_filename': 'ts_oemof_test_input_data.csv',
    'csv_separator': ',',
    'nominal_value': 1000000,
    'column_title': 'demand_el',
    'path': my_path
})

components.append({
    'component': 'battery',
    'name': 'li_battery',
    'bus_in_and_out': 'bel_dc_bat',
    'battery_capacity': 200000,
    'soc_init': 0.15,
    'symm_c_rate': True,
    'c_rate_symm': 1,
    'capex': {
        'key': ['spec', 'poly'],
        'fitting_value': [100, ['cost', 10]],
        'dependant_value': ['battery_capacity', 'c_rate_symm'],
    },
    'opex': {
        'key': 'spec',
        'fitting_value': 0.02,
        'dependant_value': 'capex'
    },
    'life_time': 15,
    'soc_min': 0.1,
    'loss_rate': 0.001,  # [(%*100)/day]
    # __B1: limit grid: charge always (from PV and grid) use only for power peaks
    'vac_in': -0.20 / 1000,
    'vac_out': 0.25 / 1000,
})

components.append({
    'component': 'power_converter',
    'name': 'ac_dc_inverter_bat_in',
    'bus_input': 'bel_ac_lv_grid',
    'bus_output': 'bel_dc_bat',
    'output_power_max': 800000,
    'efficiency': 0.98,
})

components.append({
    'component': 'power_converter',
    'name': 'dc_ac_inverter_bat_out',
    'bus_input': 'bel_dc_bat',
    'bus_output': 'bel_ac_lv_grid',
    'output_power_max': 1000000,
    'efficiency': 0.98,
})

components.append({
    'component': 'electric_heater',
    'name': 'Electric_heater',
    'bus_el': 'bel_ac_lv_grid',
    'bus_th': 'bth',
    'power_max': 10000000,
    'efficiency': 0.98,
})

components.append({
    'component': 'energy_demand_from_csv',
    'name': 'heat_demand',
    'bus_in': 'bth',
    'csv_filename': 'ts_oemof_test_input_data.csv',
    'csv_separator': ',',
    'nominal_value': 1000000,
    'column_title': 'demand_th',
    'path': my_path
})

sim_params = {
    'start_date': '1/1/2019',
    'n_intervals': 24,
    'interval_time': 60,
    'interest_rate': 0.03,
    'print_progress': True,
    'show_debug_flag': False,
}

mymodel = {
    'busses': busses,
    'components': components,
    'sim_params': sim_params,
}
