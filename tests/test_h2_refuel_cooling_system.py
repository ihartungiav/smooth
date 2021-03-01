from smooth.components.component_h2_refuel_cooling_system import H2RefuelCoolingSystem
from smooth.framework.simulation_parameters import SimulationParameters
import oemof.solph as solph
import os


class TestBasic:
    sim_params = SimulationParameters({})

    def test_init(self):
        test_path = os.path.join(os.path.dirname(__file__), 'test_timeseries')

        rcs = H2RefuelCoolingSystem({"csv_filename": "test_csv.csv", "path": test_path})
        assert hasattr(rcs, "nominal_value")
        assert hasattr(rcs, "csv_separator")
        assert hasattr(rcs, "column_title")
        assert hasattr(rcs, "bus_el")
        assert hasattr(rcs, "cool_spec_energy")
        assert hasattr(rcs, "standby_energy")
        assert hasattr(rcs, "number_of_units")

        rcs = H2RefuelCoolingSystem({"csv_filename": "test_csv.csv",
                                     "path": test_path,
                                     "nominal_value": 1,
                                     "cool_spec_energy": 600,
                                     "standby_energy": 3000})
        assert rcs.nominal_value == 1
        assert rcs.electrical_energy.loc[0][0] == 1000

    def test_create_oemof_model(self):
        test_path = os.path.join(os.path.dirname(__file__), 'test_timeseries')
        self.sim_params.i_interval = 0

        rcs = H2RefuelCoolingSystem({"bus_el": "foo",
                                     "csv_filename": "test_csv.csv",
                                     "path": test_path,
                                     "sim_params": self.sim_params})

        model = rcs.create_oemof_model({"foo": solph.Bus(label="foo")}, None)
        assert type(model) == solph.network.Sink
        assert len(model.inputs) == 1
        assert len(model.outputs) == 0
