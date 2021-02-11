from smooth.components.component_sink import Sink
import oemof.solph as solph


def test_init():
    s = Sink({})
    assert hasattr(s, "input_max")
    assert hasattr(s, "bus_in")
    assert s.commodity_costs == 0

    s = Sink({"name": "foo"})
    assert s.name == "foo"


def test_create_oemof_model():
    s = Sink({"bus_in": "foo"})
    model = s.create_oemof_model({"foo": solph.Bus(label="foo")}, None)
    assert type(model) == solph.network.Sink
    assert len(model.inputs) == 1
    assert len(model.outputs) == 0
