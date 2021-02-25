from smooth.components.component_energy_demand_from_csv import EnergyDemandFromCsv
from smooth.framework.simulation_parameters import SimulationParameters
import oemof.solph as solph
import os


class TestBasic:

    sim_params = SimulationParameters({})

    def test_init(self):

        test_path = os.path.join(os.path.dirname(__file__), 'test_timeseries')

        demand = EnergyDemandFromCsv({"csv_filename": "test_csv.csv", "path": test_path})
        assert hasattr(demand, "nominal_value")
        assert hasattr(demand, "csv_separator")
        assert hasattr(demand, "column_title")
        assert hasattr(demand, "bus_in")

        demand = EnergyDemandFromCsv({"csv_filename": "test_csv.csv", "path": test_path,
                                      "nominal_value": 2})
        assert demand.nominal_value == 2

        #todo: raise error if "None" is passed as csv_filename variable
        #todo: assert file is csv type

    def test_create_oemof_model(self):
 
        test_path = os.path.join(os.path.dirname(__file__), 'test_timeseries')
        self.sim_params.i_interval = 0

        demand = EnergyDemandFromCsv({"bus_in": "foo",
                                      "csv_filename": "test_csv.csv",
                                      "path": test_path,
                                      "sim_params": self.sim_params})

        model = demand.create_oemof_model({"foo": solph.Bus(label="foo")}, None)
        assert type(model) == solph.network.Sink
        assert len(model.inputs) == 1
        assert len(model.outputs) == 0
