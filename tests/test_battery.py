from smooth.components.component_battery import Battery
from smooth.framework.simulation_parameters import SimulationParameters
import oemof.solph as solph

import pytest


class TestBasic:

    sim_params = SimulationParameters({"interval_time": 30})

    def test_init(self):
        b = Battery({"sim_params": self.sim_params})
        assert hasattr(b, "bus_in_and_out")
        assert hasattr(b, "soc")

        # SOC init below min
        with pytest.raises(ValueError):
            b = Battery({
                "soc_init": 0,
                "soc_min": 0.1
            })

        # loss rate per day
        b = Battery({
            "sim_params": self.sim_params,
            "loss_rate": 12  # 50% per hour
        })
        assert b.loss_rate == 0.5

    def test_prepare_simulation(self):
        b = Battery({
            "vac_in": 3,
            "vac_out": 4,
            "sim_params": self.sim_params
        })

        # uninitialized
        assert b.current_vac == [0, 0]

        # set VAC
        b.prepare_simulation(None)
        assert b.current_vac == [3, 4]

        b = Battery({
            "vac_low_in": 1,
            "vac_low_out": 2,
            "vac_in": 3,
            "vac_out": 4,
            "soc_wanted": 1,
            "soc_init": 0.5,
            "sim_params": self.sim_params
        })
        b.prepare_simulation(None)
        assert b.current_vac == [1, 2]

        b = Battery({
            "efficiency_charge": 1,
            "efficiency_discharge": 2,
            "c_rate_charge": 3,
            "c_rate_discharge": 3,
            "battery_capacity": 4,
            "sim_params": self.sim_params
        })
        b.prepare_simulation(None)
        assert b.p_in_max == 12
        assert b.p_out_max == 12

    def test_add_to_oemof_model(self):
        b = Battery({
            "bus_in_and_out": "foo",
            "sim_params": self.sim_params
        })
        oemof_model = solph.EnergySystem()
        component = b.add_to_oemof_model({"foo": solph.Bus(label="foo")}, oemof_model)
        assert type(component) == solph.components.GenericStorage
        assert len(component.inputs) == 1
        assert len(component.outputs) == 1


class TestUpdate:

    sim_params = SimulationParameters({"interval_time": 60, "n_intervals": 2})
    sim_params.i_interval = 0
    oemof_model = solph.EnergySystem(
        timeindex=sim_params.date_time_index[0:1],
        freq='{}min'.format(sim_params.interval_time)
    )

    def test_update_states(self):
        # simulate one smooth iteration
        # build energy model with two batteries, connected by a bus
        bus = solph.Bus(label="foo")
        self.oemof_model.add(bus)
        b1 = Battery({
            "name": "bat1",
            "bus_in_and_out": "foo",
            "soc_init": 1,
            "loss_rate": 12,  # 0.5/h
            "sim_params": self.sim_params
        })
        b1.prepare_simulation(None)
        b1.add_to_oemof_model({"foo": bus}, self.oemof_model)
        b2 = Battery({
            "name": "bat2",
            "bus_in_and_out": "foo",
            "sim_params": self.sim_params
        })
        b2.prepare_simulation(None)
        b2.add_to_oemof_model({"foo": bus}, self.oemof_model)
        model_to_solve = solph.Model(self.oemof_model)
        # solve model
        oemof_results = model_to_solve.solve(solver='cbc', solve_kwargs={'tee': False})
        assert oemof_results["Solver"][0]["Status"].value == "ok"
        results = solph.processing.results(model_to_solve)
        assert results is not None

        # update battery states
        for battery in [b1, b2]:
            battery.update_flows(results)
            battery.update_states(results)
            battery.update_var_costs()
            battery.update_var_emissions()
            battery.generate_results()

            assert hasattr(battery, "states")
            assert "soc" in battery.states.keys()
            assert len(battery.states["soc"]) == self.sim_params.n_intervals
            assert battery.states["soc"][self.sim_params.i_interval] == battery.soc
            assert battery.soc > battery.soc_min

        # check loss rate
        assert b1.soc == 0.5  # todo: Fail, but why??
        assert b2.soc == b2.soc_init
