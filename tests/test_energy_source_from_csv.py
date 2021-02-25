from smooth.components.component_energy_source_from_csv import EnergySourceFromCsv
import oemof.solph as solph


def test_init():
    #todo: define a csv filename so None type isn't taken
    source = EnergySourceFromCsv({})
    assert hasattr(source, "nominal_value")
    assert hasattr(source, "csv_separator")
    assert hasattr(source, "column_title")
    assert hasattr(source, "bus_out")

    source = EnergySourceFromCsv({"column_title": "foo"})
    assert source.column_title == "foo"


def test_create_oemof_model(self):
    source = EnergySourceFromCsv({"bus_out": "foo"})
    model = source.create_oemof_model({"foo": solph.Bus(label="foo")}, None)
    assert type(model) == solph.components.Source
    assert len(model.inputs) == 0
    assert len(model.outputs) == 1