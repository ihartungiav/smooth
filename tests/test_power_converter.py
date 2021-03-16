from smooth.components.component_power_converter import PowerConverter
import oemof.solph as solph


def test_init():
    power_converter = PowerConverter({})
    params = {"efficiency": 0, "output_power_max": 100}
    power_converter = PowerConverter(params)
    assert power_converter.efficiency == params["efficiency"]
    assert power_converter.output_power_max == params["output_power_max"]


def test_add_to_oemof_model():
    power_converter = PowerConverter({
        "bus_input": "bus_input",
        "bus_output": "bus_output"
    })
    model = solph.EnergySystem()
    comp = power_converter.add_to_oemof_model({
        "bus_input": solph.Bus(label="bus_input"),
        "bus_output": solph.Bus(label="bus_output"),
    }, model)

    assert len(model.entities) == 1
    assert type(comp) == solph.Transformer
    assert len(comp.inputs) == 1
    assert len(comp.outputs) == 1
