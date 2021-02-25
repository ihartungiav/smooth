from smooth.components.component_ac_dc_converter import AcDcConverter
import oemof.solph as solph


def test_init():
    acdc = AcDcConverter({})

    params = {"efficiency": 0, "output_power_max": 100}
    acdc = AcDcConverter(params)
    assert acdc.efficiency == params["efficiency"]
    assert acdc.output_power_max == params["output_power_max"]


def test_create_oemof_model():
    acdc = AcDcConverter({
        "bus_el_ac": "bus_el_ac",
        "bus_el_dc": "bus_el_dc"
    })
    model = acdc.create_oemof_model({
        "bus_el_ac": solph.Bus(label="bus_el_ac"),
        "bus_el_dc": solph.Bus(label="bus_el_dc"),
    }, None)

    assert type(model) == solph.Transformer
    assert len(model.inputs) == 1
    assert len(model.outputs) == 1
