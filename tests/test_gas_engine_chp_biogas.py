from smooth.components.component_gas_engine_chp_biogas import GasEngineChpBiogas
from smooth.framework.simulation_parameters import SimulationParameters
import oemof.solph as solph
import pytest


class TestBasic:
    sim_params = SimulationParameters({})

    def test_init(self):
        comp = GasEngineChpBiogas({"sim_params": self.sim_params, "power_max": 1})
        assert comp.bg_input_max > 0

        with pytest.raises(ValueError):
            # share != 1
            GasEngineChpBiogas({
                "sim_params": self.sim_params,
                "power_max": 1,
                "ch4_share": 0,
                "co2_share": 0
            })

    def test_add_to_oemof_model(self):
        comp = GasEngineChpBiogas({
            "power_max": 1,
            "bus_bg": "bus1",
            "bus_el": "bus2",
            "bus_th": "bus3",
            "sim_params": self.sim_params
        })

        oemof_model = solph.EnergySystem(
            timeindex=self.sim_params.date_time_index[0:1],
            freq='{}min'.format(self.sim_params.interval_time)
        )
        comp.add_to_oemof_model({
            "bus1": solph.Bus(label="bus1"),
            "bus2": solph.Bus(label="bus2"),
            "bus3": solph.Bus(label="bus3")
        }, oemof_model)
        assert comp.model_el is not None and comp.model_th is not None

        assert type(comp.model_el) == solph.custom.PiecewiseLinearTransformer
        assert type(comp.model_th) == solph.custom.PiecewiseLinearTransformer
        assert len(comp.model_el.inputs) == 1
        assert len(comp.model_el.outputs) == 1
        assert len(comp.model_th.inputs) == 1
        assert len(comp.model_th.outputs) == 1
