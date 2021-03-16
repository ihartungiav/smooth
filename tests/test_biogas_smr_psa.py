from smooth.components.component_biogas_smr_psa import BiogasSmrPsa
import oemof.solph as solph


def test_init():
    smr = BiogasSmrPsa({})
    params = {"input_max": 999}
    smr = BiogasSmrPsa(params)
    assert smr.input_max == params["input_max"]


def test_add_to_oemof_model():
    smr = BiogasSmrPsa({
        "bus_bg": "bus_biogas",
        "bus_el": "bus_electric",
        "bus_h2": "bus_hydrogen"
    })
    comp = smr.add_to_oemof_model({
        "bus_biogas": solph.Bus(label="bus_bg"),
        "bus_electric": solph.Bus(label="bus_el"),
        "bus_hydrogen": solph.Bus(label="bus_h2"),
    }, solph.EnergySystem())

    assert type(comp) == solph.Transformer
    assert len(comp.inputs) == 2
    assert len(comp.outputs) == 1
