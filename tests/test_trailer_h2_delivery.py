from smooth.components.component_trailer_h2_delivery import TrailerH2Delivery
import oemof.solph as solph


def test_init():
    trailer = TrailerH2Delivery({})
    assert trailer.trailer_capacity > 0
    assert hasattr(trailer, "current_ac")


def test_add_to_oemof_model():
    trailer = TrailerH2Delivery({
        "bus_in": "bus_in",
        "bus_out": "bus_out"
    })
    comp = trailer.add_to_oemof_model({
        "bus_in": solph.Bus(label="bus_in"),
        "bus_out": solph.Bus(label="bus_out"),
    }, solph.EnergySystem())

    assert type(comp) == solph.Transformer
    assert len(comp.inputs) == 1
    assert len(comp.outputs) == 1
