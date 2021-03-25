from smooth.components.component_biogas_converter import BiogasConverter
import oemof.solph as solph


def test_init():
    biogas_converter = BiogasConverter({})
    params = {"ch4_share": 0.5,
              "co2_share": 0.5}
    biogas_converter = BiogasConverter(params)
    assert biogas_converter.ch4_share == params["ch4_share"]


def test_add_to_oemof_model():
    biogas_converter = BiogasConverter({
        "bg_in": "bus_input",
        "bg_out": "bus_output"
    })
    comp = biogas_converter.add_to_oemof_model({
        "bus_input": solph.Bus(label="bg_in"),
        "bus_output": solph.Bus(label="bg_out"),
    }, solph.EnergySystem())

    assert type(comp) == solph.Transformer
    assert len(comp.inputs) == 1
    assert len(comp.outputs) == 1
