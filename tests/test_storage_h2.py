from smooth.components.component_storage_h2 import StorageH2
from smooth.framework.simulation_parameters import SimulationParameters
import oemof.solph as solph


class TestBasic:

    sim_params = SimulationParameters({})

    def test_init(self):
        s = StorageH2({"sim_params": self.sim_params})
        assert hasattr(s, "bus_in")
        assert hasattr(s, "bus_out")

        assert 0 < s.initial_storage_factor < 1

        assert s.storage_level_wanted is None

        s = StorageH2({"sim_params": self.sim_params,
                       "storage_capacity": 100,
                       "initial_storage_factor": 0.8,
                       "slw_factor": 0.8})

        assert s.storage_level_init == 80
        assert s.storage_level_wanted == 80

    def test_prepare_simulation(self):
        s = StorageH2({"sim_params": self.sim_params,
                       "vac_in": 3,
                       "vac_out": 4})

        # uninitialized
        assert s.current_vac == [0, 0]

        # set VAC
        s.prepare_simulation(None)
        assert s.current_vac == [3, 4]

        s = StorageH2({"sim_params": self.sim_params,
                       "storage_capacity": 100,
                       "vac_low_in": 1,
                       "vac_low_out": 2,
                       "vac_in": 3,
                       "vac_out": 4,
                       "slw_factor": 1,
                       "initial_storage_factor": 0.5})

        s.prepare_simulation(None)
        assert s.current_vac == [1, 2]
        assert s.delta_max == 100

    def test_add_to_oemof_model(self):
        s = StorageH2({
          "bus_in": "foo",
          "bus_out": "bar",
          "sim_params": self.sim_params
        })

        oemof_model = solph.EnergySystem()
        component = s.add_to_oemof_model({"foo": solph.Bus(label="foo"),
                                          "bar": solph.Bus(label="bar")}, oemof_model)
        assert type(component) == solph.components.GenericStorage
        assert len(component.inputs) == 1
        assert len(component.outputs) == 1


class TestUpdate:

    sim_params = SimulationParameters({"interval_time": 30, "n_intervals": 2})
    sim_params.i_interval = 0
    oemof_model = solph.EnergySystem(
        timeindex=sim_params.date_time_index[0:1],
        freq='{}min'.format(sim_params.interval_time)
    )

    def test_update_states(self):
        # simulate one smooth iteration
        # simulate a single hydrogen storage, not connected to anything
        bus_in = solph.Bus(label="foo")
        bus_out = solph.Bus(label="bar")
        self.oemof_model.add(bus_in)
        self.oemof_model.add(bus_out)

        s = StorageH2({
            "bus_in": "bus_in",
            "bus_out": "bus_out",
            "sim_params": self.sim_params
        })
        storage_h2_model = s.add_to_oemof_model({
            "bus_in": bus_in,
            "bus_out": bus_out
        }, self.oemof_model)
        self.oemof_model.add(storage_h2_model)

        model_to_solve = solph.Model(self.oemof_model)

        # solve model
        oemof_results = model_to_solve.solve(solver='cbc', solve_kwargs={'tee': False})
        assert oemof_results["Solver"][0]["Status"] == "ok"
        results = solph.processing.results(model_to_solve)
        assert results is not None

        # update storage states
        s.update_states(results)
        s.update_var_costs()
        s.update_var_emissions()
        s.generate_results()

        assert hasattr(s, "states")
        assert "storage_level" in s.states.keys()
        assert "pressure" in s.states.keys()
        assert len(s.states["storage_level"]) == self.sim_params.n_intervals
        assert len(s.states["pressure"]) == self.sim_params.n_intervals
        assert s.states["storage_level"][self.sim_params.i_interval] == s.storage_level
        assert s.states["pressure"][self.sim_params.i_interval] == s.pressure
        assert s.storage_level > s.storage_level_min
