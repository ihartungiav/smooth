from smooth.components.component_pem_electrolyzer import PemElectrolyzer
from smooth.framework.simulation_parameters import SimulationParameters
import oemof.solph as solph


class TestBasic:

    def test_init(self):

        comp = PemElectrolyzer({})
        assert len(comp.bp_waste_heat_energy) > 0

    def test_add_to_oemof_model(self):
        sim_params = SimulationParameters({})
        comp = PemElectrolyzer({
            "bus_h2": "bus1",
            "bus_el": "bus2",
            "bus_th": "bus3",
            "sim_params": sim_params
        })

        oemof_model = solph.EnergySystem(
            timeindex=sim_params.date_time_index[0:1],
            freq='{}min'.format(sim_params.interval_time)
        )
        comp.add_to_oemof_model({
            "bus1": solph.Bus(label="bus1"),
            "bus2": solph.Bus(label="bus2"),
            "bus3": solph.Bus(label="bus3")
        }, oemof_model)
        assert comp.model_h2 is not None and comp.model_th is not None

        assert type(comp.model_h2) == solph.custom.PiecewiseLinearTransformer
        assert type(comp.model_th) == solph.custom.PiecewiseLinearTransformer
        assert len(comp.model_h2.inputs) == 1
        assert len(comp.model_h2.outputs) == 1
        assert len(comp.model_th.inputs) == 1
        assert len(comp.model_th.outputs) == 1
