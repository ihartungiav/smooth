from smooth.components.component_dc_ac_inverter import DcAcInverter
import oemof.solph as solph


def test_init():
    dcac = DcAcInverter({})

    params = {"output_power_max": 0}
    dcac = DcAcInverter(params)
    assert dcac.output_power_max == params["output_power_max"]


def test_create_oemof_model():
    dcac = DcAcInverter({
        "bus_el_ac": "bus_ac",
        "bus_el_dc": "bus_dc"
    })
    model = dcac.create_oemof_model({
        "bus_ac": solph.Bus(label="bus_ac"),
        "bus_dc": solph.Bus(label="bus_dc"),
    }, None)

    assert type(model) == solph.Transformer
    assert len(model.inputs) == 1
    assert len(model.outputs) == 1
