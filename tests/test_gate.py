from smooth.components.component_gate import Gate
import oemof.solph as solph

import pytest


def test_init():
    gate = Gate({})
    assert hasattr(gate, "max_input")
    assert hasattr(gate, "bus_in")
    assert hasattr(gate, "bus_out")
    # todo: include efficiency param when PR is merged
    params = {"max_input": 100}
    gate = Gate(params)
    assert gate.max_input == params["max_input"]

    faulty_params = [
        ({"max_input": -100}, ValueError),
        ({"not_a_param": None}, ValueError)
    ]

    for param, error in faulty_params:
        with pytest.raises(error):
            Gate(param)


def test_add_to_oemof_model():
    gate = Gate({
        "bus_in": "bus_in",
        "bus_out": "bus_out"
    })
    oemof_model = solph.EnergySystem()
    component = gate.add_to_oemof_model({
        "bus_in": solph.Bus(label="bus_in"),
        "bus_out": solph.Bus(label="bus_out"),
    }, oemof_model)

    assert type(component) == solph.Transformer
    assert len(component.inputs) == 1
    assert len(component.outputs) == 1
