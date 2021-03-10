from smooth.components.component_stratified_thermal_storage import StratifiedThermalStorage
from smooth.framework.simulation_parameters import SimulationParameters
import oemof.solph as solph
import os


class TestBasic:

    sim_params = SimulationParameters({})
    test_path = os.path.join(os.path.dirname(__file__), 'test_timeseries')

    def test_init(self):

        sts = StratifiedThermalStorage({"sim_params": self.sim_params})
        assert sts.volume > 0

        # temperature from CSV: overide given argument
        sts = StratifiedThermalStorage({
            "sim_params": self.sim_params,
            "csv_filename": "test_csv.csv",
            "column_title": "Simple test csv",
            "temp_env": 0,
            "path": self.test_path
        })
        assert sts.temp_env != 0 and len(sts.temp_env) > 0

    def test_create_oemof_model(self):

        sts = StratifiedThermalStorage({
            "bus_in": "bus1",
            "bus_out": "bus2",
            "sim_params": self.sim_params
        })

        sts.sim_params.i_interval = 0

        comp = sts.create_oemof_model({
            "bus1": solph.Bus(label="bus1"),
            "bus2": solph.Bus(label="bus2")
        }, solph.EnergySystem())
        assert type(comp) == solph.components.GenericStorage
        assert len(comp.inputs) == 1
        assert len(comp.outputs) == 1
