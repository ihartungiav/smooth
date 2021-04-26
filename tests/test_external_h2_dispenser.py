from smooth.components.external_component_h2_dispenser import H2Dispenser

from os import path


def test_init():
    # basic creation
    test_path = path.join(path.dirname(__file__), 'test_timeseries')
    h2 = H2Dispenser({"csv_filename": "test_csv.csv", "path": test_path, })
    assert h2 is not None
    assert h2.csv_filename is not None

    # read in data
    assert h2.data is not None

    # calculated params
    assert h2.max_hourly_h2_demand == 1
