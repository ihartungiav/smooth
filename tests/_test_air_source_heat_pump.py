from smooth.components.component_air_source_heat_pump import AirSourceHeatPump
import oemof.solph as solph


def test_init():
    pump = AirSourceHeatPump({})
    # coefficients of performance computed?
    assert pump.cops is not None

    params = {"power_max": 0}
    pump = AirSourceHeatPump(params)
    assert pump.output_power_max == params["power_max"]


def test_add_to_oemof_model():
    pump = AirSourceHeatPump({
        "bus_el": "bus_el",
        "bus_th": "bus_th"
    })
    model = solph.EnergySystem()
    comp = pump.create_oemof_model({
        "bus_el": solph.Bus(label="bus_el"),
        "bus_th": solph.Bus(label="bus_th"),
    }, model)

    assert type(comp) == solph.Transformer
    assert len(comp.inputs) == 1
    assert len(comp.outputs) == 1
