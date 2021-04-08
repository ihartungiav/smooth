from smooth.components.component_sink import Sink
import oemof.solph as solph


def test_init():
    s = Sink({})
    assert hasattr(s, "input_max")
    assert hasattr(s, "bus_in")
    assert s.commodity_costs == 0

    s = Sink({"name": "foo"})
    assert s.name == "foo"


def test_add_to_oemof_model():
    s = Sink({"bus_in": "foo"})
    oemof_model = solph.EnergySystem()
    component = s.add_to_oemof_model({"foo": solph.Bus(label="foo")}, oemof_model)
    assert type(component) == solph.network.Sink
    assert len(component.inputs) == 1
    assert len(component.outputs) == 0
