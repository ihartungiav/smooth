from smooth.components.component_compressor_h2 import CompressorH2
from smooth.framework.simulation_parameters import SimulationParameters
import oemof.solph as solph
from oemof.outputlib import processing

import pytest


class TestBasic:

    def test_init(self):
        ch2 = CompressorH2({})
        # R_H2 set properly? Compare floats
        assert abs(ch2.R_H2 - (8.314 / (2.016 * 1e-3))) < 1e-5

        ch2 = CompressorH2({"m_flow_max": 50})
        assert ch2.m_flow_max == 50

    def test_create_oemof_model(self):
        ch2 = CompressorH2({
            "bus_h2_in": "bus1",
            "bus_h2_out": "bus2",
            "bus_el": "bus3",
            "sim_params": SimulationParameters({"interval_time": 15}),
            "m_flow_max": 60
        })
        model = ch2.create_oemof_model({
            "bus1": solph.Bus(label="bus1"),
            "bus2": solph.Bus(label="bus2"),
            "bus3": solph.Bus(label="bus3"),
        }, None)
        assert type(model) == solph.Transformer
        assert len(model.inputs) == 2
        assert len(model.outputs) == 1
        for k,v in model.inputs.items():
            if str(k) == "bus1":
                assert v.nominal_value == 15
