from smooth.components.component_electrolyzer import Electrolyzer
from smooth.framework.simulation_parameters import SimulationParameters
import oemof.solph as solph


class TestBasic:

    sim_params = SimulationParameters({"interval_time": 30})

    def test_init(self):
        ely = Electrolyzer({"power_max": 100, "sim_params": self.sim_params})
        assert ely.energy_max == 50  # 100W, 30 minutes
        assert ely.max_production_per_step is not None

    def test_add_to_oemof_model(self):
        ely = Electrolyzer({
            "bus_el": "bus1",
            "bus_h2": "bus2",
            "sim_params": self.sim_params
        })
        oemof_model = solph.EnergySystem()
        component = ely.add_to_oemof_model({
            "bus1": solph.Bus(label="bus1"),
            "bus2": solph.Bus(label="bus2")
        }, oemof_model)
        assert type(component) == solph.custom.PiecewiseLinearTransformer
        assert len(component.inputs) == 1
        assert len(component.outputs) == 1

    def test_update_non_linear_behaviour(self):
        ely = Electrolyzer({"sim_params": self.sim_params})
        ely.update_nonlinear_behaviour()

        # test supporting points. Assumes default values (apart from interval_time)
        # should any of these fail, have fun testing the associated functions

        n_supporting_point = 10
        temp = [295, 299, 303, 307, 310, 314, 317, 320, 323, 326, 327]
        h2 = [0, 103, 196, 283, 366, 445, 521, 594, 665, 733, 800]
        energy = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]

        for i in range(n_supporting_point + 1):
            assert temp[i] == int(ely.supporting_points["temperature"][i])
            assert h2[i] == int(ely.supporting_points["h2_produced"][i] * 1000)
            assert energy[i] == int(ely.supporting_points["energy"][i] / 1000)


class TestUpdate:

    sim_params = SimulationParameters({"interval_time": 30, "n_intervals": 2})
    sim_params.i_interval = 0
    oemof_model = solph.EnergySystem(
        timeindex=sim_params.date_time_index[0:1],
        freq='{}min'.format(sim_params.interval_time)
    )

    def test_update_states(self):
        # simulate one smooth iteration
        # simulate a single electrolyzer, not connected to anything
        bus_el = solph.Bus(label="bus_el")
        bus_h2 = solph.Bus(label="bus_h2")
        self.oemof_model.add(bus_el)
        self.oemof_model.add(bus_h2)

        ely = Electrolyzer({
            "bus_el": "bus_el",
            "bus_h2": "bus_h2",
            "sim_params": self.sim_params
        })
        ely_model = ely.add_to_oemof_model({
            "bus_el": bus_el,
            "bus_h2": bus_h2
        }, self.oemof_model)
        self.oemof_model.add(ely_model)

        model_to_solve = solph.Model(self.oemof_model)

        # solve model
        oemof_results = model_to_solve.solve(solver='cbc', solve_kwargs={'tee': False})
        assert oemof_results["Solver"][0]["Status"].value == "ok"
        results = solph.processing.results(model_to_solve)
        assert results is not None

        old_temp = ely.temperature
        ely.update_states(results)
        # idle: cooling down, no water consumption
        assert ely.temperature < old_temp
        assert ely.states["temperature"][0] == ely.temperature
        assert ely.states["water_consumption"][0] == 0
