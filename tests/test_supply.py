from smooth.components.component_supply import Supply
import oemof.solph as solph


def test_init():
    s = Supply({})
    assert hasattr(s, "output_max")
    assert hasattr(s, "bus_out")

    s = Supply({"name": "foo"})
    assert s.name == "foo"


def test_prepare_simulation():
    s = Supply({})
    s.prepare_simulation(None)

    s = Supply({
        "fs_component_name": "foo",
        "fs_attribute_name": "life_time",
        "fs_low_art_cost": 3,
        "fs_high_art_cost": 4,
        "fs_threshold": 5
    })

    s2 = Supply({
        "name": "foo",
        "life_time": 10
    })
    s.prepare_simulation([s, s2])
    assert s.artificial_costs == 4
    assert s.current_ac == 4


def test_create_oemof_model():
    s = Supply({"bus_out": "foo"})
    model = s.create_oemof_model({"foo": solph.Bus(label="foo")}, None)
    assert type(model) == solph.network.Source
    assert len(model.inputs) == 0
    assert len(model.outputs) == 1
