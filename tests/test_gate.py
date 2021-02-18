from smooth.components.component_gate import Gate
import oemof.solph as solph


def test_init():
    gate = Gate({})
    # todo: include test to assert max_input is above zero?
    assert gate.max_input >= 0
    # todo: include efficiency param when PR is merged
    params = {"max_input": 100}
    gate = Gate(params)
    assert gate.max_input == params["max_input"]


def test_create_oemof_model():
    gate = Gate({
        "bus_in": "bus_in",
        "bus_out": "bus_out"
    })
    model = gate.create_oemof_model({
        "bus_in": solph.Bus(label="bus_in"),
        "bus_out": solph.Bus(label="bus_out"),
    }, None)

    assert type(model) == solph.Transformer
    assert len(model.inputs) == 1
    assert len(model.outputs) == 1
