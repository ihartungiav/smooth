from smooth.components.component_electric_heater import ElectricHeater
import oemof.solph as solph


def test_init():
    heater = ElectricHeater({})

    params = {"power_max": 100}
    heater = ElectricHeater(params)
    assert heater.power_max == params["power_max"]


def test_add_to_oemof_model():
    heater = ElectricHeater({
        "bus_th": "bus_el",
        "bus_el": "bus_th"
    })
    model = solph.EnergySystem()
    component = heater.add_to_oemof_model({
        "bus_el": solph.Bus(label="bus_el"),
        "bus_th": solph.Bus(label="bus_th"),
    }, model)

    assert type(component) == solph.Transformer
    assert len(component.inputs) == 1
    assert len(component.outputs) == 1
