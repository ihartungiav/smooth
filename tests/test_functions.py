import smooth.framework.functions.functions as func
from smooth.framework.simulation_parameters import SimulationParameters

import os
import pytest


def test_read_data_file():
    test_path = os.path.join(os.path.dirname(__file__), 'test_timeseries')
    file_name = "test_csv.csv"
    # by index
    data = func.read_data_file(test_path, file_name, ",", 0)
    # by name
    data = func.read_data_file(test_path, file_name, ",", "Simple test csv")
    assert len(data) == 168
    for idx in range(len(data)):
        assert data[data.columns[0]][idx] == 1

def test_create_component_obj():
    #dummy sim_params
    sim_params = SimulationParameters({})
    test_path = os.path.join(os.path.dirname(__file__), 'test_timeseries')

    # can all components be created?
    _,_,files = next(os.walk("smooth/components/"))
    for f in files:
        if f == "__init__.py":
            continue
        if f == "component.py":
            # parent class
            continue
        if f.startswith("external"):
            # external components
            continue

        # get component name from file
        name, ext = f.split('.')
        # remove "component_" prefix from name
        name = "_".join(name.split("_")[1:])
        comp = {"component": name}

        # special arguments for some components
        if name == "electrolyzer_waste_heat":
            comp["bus_th"] = None
        if name == "fuel_cell_chp":
            comp["power_max"] = 1
        if name == "gas_engine_chp_biogas":
            comp["power_max"] = 1
        if name == "h2_chp":
            comp["power_max"] = 1
        if name.endswith("csv"):
            comp["csv_filename"] = "test_csv.csv"
            comp["path"] = test_path
        if name == "h2_refuel_cooling_system":
            comp["csv_filename"] = "test_csv.csv"
            comp["path"] = test_path
        if name == "air_source_heat_pump":
            # problem with oemof.thermal
            continue

        try:
            func.create_component_obj({"components": {"comp": comp}}, sim_params)
        except:
            raise Exception("Exeption while creating {}".format(name))
