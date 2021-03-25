from smooth.components.component_electrolyzer_waste_heat import ElectrolyzerWasteHeat
from smooth.framework.simulation_parameters import SimulationParameters
import oemof.solph as solph

import pytest


class TestBasic:

    sim_params = SimulationParameters({"interval_time": 30})

    def test_init(self):
        with pytest.raises(KeyError):
            ely = ElectrolyzerWasteHeat({"sim_params": self.sim_params})
        ely = ElectrolyzerWasteHeat({
            "bus_th": None,
            "power_max": 100,
            "sim_params": self.sim_params
        })
        assert ely.energy_max == 50  # 100W, 30 minutes
        assert ely.area_separator is not None

    def test_add_to_oemof_model(self):
        ely = ElectrolyzerWasteHeat({
            "bus_el": "bus1",
            "bus_h2": "bus2",
            "bus_th": "bus3",
            "sim_params": self.sim_params
        })
        oemof_model = solph.EnergySystem(
            timeindex=self.sim_params.date_time_index[0:1],
            freq='{}min'.format(self.sim_params.interval_time)
        )
        ely.add_to_oemof_model({
            "bus1": solph.Bus(label="bus1"),
            "bus2": solph.Bus(label="bus2"),
            "bus3": solph.Bus(label="bus3")
        }, oemof_model)
        assert ely.model_h2 is not None and ely.model_th is not None

        assert type(ely.model_th) == solph.custom.PiecewiseLinearTransformer
        assert len(ely.model_th.inputs) == 1
        assert len(ely.model_th.outputs) == 1

    def test_update_non_linear_behaviour(self):
        ely = ElectrolyzerWasteHeat({"bus_th": None, "sim_params": self.sim_params})
        ely.update_nonlinear_behaviour()

        # test supporting points. Assumes default values (apart from interval_time)
        # should any of these fail, have fun testing the associated functions

        n_supporting_point = 10
        temp = [295, 299, 303, 307, 310, 314, 317, 320, 323, 326, 327]
        h2 = [0, 103, 196, 283, 366, 445, 521, 594, 665, 733, 800]
        energy = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]

        for i in range(n_supporting_point + 1):
            points = ely.supporting_points
            assert temp[i] == int(points["temperature"][i])
            assert h2[i] == int(points["h2_produced"][i] * 1000)
            assert energy[i] == int(points["energy"][i] / 1000)
            assert points["energy_halved"][i] == points["energy"][i] / 2
            assert points["thermal_energy"][i] == 0


class TestUpdate:

    sim_params = SimulationParameters({"interval_time": 30, "n_intervals": 2})
    sim_params.i_interval = 0
    oemof_model = solph.EnergySystem(
        timeindex=sim_params.date_time_index[0:1],
        freq='{}min'.format(sim_params.interval_time)
    )

    def test_update_states(self):
        # simulate one smooth iteration
        # simulate a single electrolyzer with waste heat, not connected to other components
        bus_el = solph.Bus(label="bus_el")
        bus_h2 = solph.Bus(label="bus_h2")
        bus_th = solph.Bus(label="bus_th")
        self.oemof_model.add(bus_el)
        self.oemof_model.add(bus_h2)
        self.oemof_model.add(bus_th)

        ely = ElectrolyzerWasteHeat({
            "bus_el": "bus_el",
            "bus_h2": "bus_h2",
            "bus_th": "bus_th",
            "sim_params": self.sim_params
        })
        ely.add_to_oemof_model({
            "bus_el": bus_el,
            "bus_h2": bus_h2,
            "bus_th": bus_th
        }, self.oemof_model)

        model_to_solve = solph.Model(self.oemof_model)

        # solve model
        oemof_results = model_to_solve.solve(solver='cbc', solve_kwargs={'tee': False})
        assert oemof_results["Solver"][0]["Status"].value == "ok"
        results = solph.processing.results(model_to_solve)
        assert results is not None

        ely.update_states(results)
        # idle: cooling down, no water consumption
        assert ely.temperature < ely.temp_init
        assert ely.states["temperature"][0] == ely.temperature
        assert ely.states["water_consumption"][0] == 0
