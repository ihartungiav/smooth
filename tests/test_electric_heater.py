from smooth.components.component_electric_heater import ElectricHeater
import oemof.solph as solph


def test_init():
    acdc = ElectricHeater({})

    params = {"power_max": 100}
    acdc = ElectricHeater(params)
    assert acdc.power_max == params["power_max"]


def test_create_oemof_model():
    acdc = ElectricHeater({
        "bus_th": "bus_el",
        "bus_el": "bus_th"
    })
    model = acdc.create_oemof_model({
        "bus_el": solph.Bus(label="bus_el"),
        "bus_th": solph.Bus(label="bus_th"),
    }, None)

    assert type(model) == solph.Transformer
    assert len(model.inputs) == 1
    assert len(model.outputs) == 1
