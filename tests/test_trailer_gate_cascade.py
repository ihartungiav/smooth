from smooth.components.component_trailer_gate_cascade import TrailerGateCascade
import oemof.solph as solph


def test_init():
    gate = TrailerGateCascade({})
    assert hasattr(gate, "max_input")


def test_create_oemof_model():
    gate = TrailerGateCascade({
        "bus_in": "bus_in",
        "bus_out": "bus_out"
    })
    comp = gate.create_oemof_model({
        "bus_in": solph.Bus(label="bus_in"),
        "bus_out": solph.Bus(label="bus_out"),
    }, solph.EnergySystem())

    assert type(comp) == solph.Transformer
    assert len(comp.inputs) == 1
    assert len(comp.outputs) == 1
