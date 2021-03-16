from smooth.components.component_h2_chp import H2Chp
from smooth.framework.simulation_parameters import SimulationParameters
import oemof.solph as solph


class TestBasic:
    sim_params = SimulationParameters({})

    def test_init(self):

        comp = H2Chp({"sim_params": self.sim_params, "power_max": 1})
        assert comp.h2_input_max > 0

    def test_add_to_oemof_model(self):
        h2_chp = H2Chp({
            "power_max": 1,
            "bus_h2": "bus1",
            "bus_el": "bus2",
            "bus_th": "bus3",
            "sim_params": self.sim_params
        })

        oemof_model = solph.EnergySystem()
        h2_chp.add_to_oemof_model({
            "bus1": solph.Bus(label="bus1"),
            "bus2": solph.Bus(label="bus2"),
            "bus3": solph.Bus(label="bus3")
        }, oemof_model)
        assert h2_chp.model_el is not None and h2_chp.model_th is not None

        assert len(oemof_model.entities) == 2
        assert type(h2_chp.model_el) == solph.custom.PiecewiseLinearTransformer
        assert type(h2_chp.model_th) == solph.custom.PiecewiseLinearTransformer
        assert len(h2_chp.model_el.inputs) == 1
        assert len(h2_chp.model_el.outputs) == 1
        assert len(h2_chp.model_th.inputs) == 1
        assert len(h2_chp.model_th.outputs) == 1
