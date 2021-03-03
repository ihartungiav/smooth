from smooth.components.component_power_converter import PowerConverter
import oemof.solph as solph


def test_init():
    power_converter = PowerConverter({})
    params = {"efficiency": 0, "output_power_max": 100}
    power_converter = PowerConverter(params)
    assert power_converter.efficiency == params["efficiency"]
    assert power_converter.output_power_max == params["output_power_max"]


def test_create_oemof_model():
    power_converter = PowerConverter({
        "bus_input": "bus_input",
        "bus_output": "bus_output"
    })
    model = power_converter.create_oemof_model({
        "bus_input": solph.Bus(label="bus_input"),
        "bus_output": solph.Bus(label="bus_output"),
    }, None)

    assert type(model) == solph.Transformer
    assert len(model.inputs) == 1
    assert len(model.outputs) == 1
