from smooth.components.component_trailer_gate import TrailerGate
import oemof.solph as solph


def test_init():
    gate = TrailerGate({})
    assert hasattr(gate, "driver_costs")


def test_add_to_oemof_model():
    gate = TrailerGate({
        "bus_in": "bus_in",
        "bus_out": "bus_out"
    })
    comp = gate.add_to_oemof_model({
        "bus_in": solph.Bus(label="bus_in"),
        "bus_out": solph.Bus(label="bus_out"),
    }, solph.EnergySystem())

    assert type(comp) == solph.Transformer
    assert len(comp.inputs) == 1
    assert len(comp.outputs) == 1
