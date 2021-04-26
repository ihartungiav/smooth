from smooth.components.component_energy_source_from_csv import EnergySourceFromCsv
from smooth.framework.simulation_parameters import SimulationParameters
import oemof.solph as solph
import os


class TestBasic:

    sim_params = SimulationParameters({})

    def test_init(self):

        test_path = os.path.join(os.path.dirname(__file__), 'test_timeseries')

        source = EnergySourceFromCsv({"csv_filename": "test_csv.csv", "path": test_path})
        assert hasattr(source, "nominal_value")
        assert hasattr(source, "csv_separator")
        assert hasattr(source, "column_title")
        assert hasattr(source, "bus_out")

        source = EnergySourceFromCsv({"csv_filename": "test_csv.csv", "path": test_path,
                                      "nominal_value": 2})
        assert source.nominal_value == 2

    def test_add_to_oemof_model(self):

        test_path = os.path.join(os.path.dirname(__file__), 'test_timeseries')
        self.sim_params.i_interval = 0

        source = EnergySourceFromCsv({"bus_out": "foo",
                                      "csv_filename": "test_csv.csv",
                                      "path": test_path,
                                      "sim_params": self.sim_params})
        oemof_model = solph.EnergySystem()
        component = source.add_to_oemof_model({"foo": solph.Bus(label="foo")}, oemof_model)
        assert type(component) == solph.network.Source
        assert len(component.inputs) == 0
        assert len(component.outputs) == 1
