from smooth.components.component_compressor_h2 import CompressorH2
from smooth.framework.simulation_parameters import SimulationParameters
import oemof.solph as solph


class TestBasic:

    def test_init(self):
        ch2 = CompressorH2({})
        # R_H2 set properly? Compare floats
        assert abs(ch2.R_H2 - (8.314 / (2.016 * 1e-3))) < 1e-5

        ch2 = CompressorH2({"m_flow_max": 50})
        assert ch2.m_flow_max == 50

    def test_add_to_oemof_model(self):
        ch2 = CompressorH2({
            "bus_h2_in": "bus1",
            "bus_h2_out": "bus2",
            "bus_el": "bus3",
            "sim_params": SimulationParameters({"interval_time": 15}),
            "m_flow_max": 60
        })
        oemof_model = solph.EnergySystem()
        component = ch2.add_to_oemof_model({
            "bus1": solph.Bus(label="bus1"),
            "bus2": solph.Bus(label="bus2"),
            "bus3": solph.Bus(label="bus3"),
        }, oemof_model)
        assert type(component) == solph.Transformer
        assert len(component.inputs) == 2
        assert len(component.outputs) == 1
        for k, v in component.inputs.items():
            if str(k) == "bus1":
                assert v.nominal_value == 15
