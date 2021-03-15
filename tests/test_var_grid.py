from smooth.components.component_var_grid import VarGrid
import oemof.solph as solph


def test_init():
    vg = VarGrid({})
    assert hasattr(vg, "output_max")
    assert hasattr(vg, "bus_out")

    vg = VarGrid({"name": "foo"})
    assert vg.name == "foo"


def test_prepare_simulation():
    vg = VarGrid({})
    vg.prepare_simulation(None)

    vg = VarGrid({
        "fs_component_name": "foo",
        "fs_attribute_name": "life_time",
        "fs_low_art_cost": 3,
        "fs_high_art_cost": 4,
        "fs_threshold": 5,
        "grid_level": 1,
        "variable_costs_l1": 0.5,
    })

    vg2 = VarGrid({
        "name": "foo",
        "life_time": 10
    })
    vg.prepare_simulation([vg, vg2])
    assert vg.artificial_costs == 4
    assert vg.current_ac == 4 + 0.5


def test_add_to_oemof_model():
    vg = VarGrid({"bus_out": "foo"})
    model = solph.EnergySystem()
    comp = vg.add_to_oemof_model({"foo": solph.Bus(label="foo")}, model)
    assert len(model.entities) == 1
    assert type(comp) == solph.network.Source
    assert len(comp.inputs) == 0
    assert len(comp.outputs) == 1
