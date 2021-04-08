import smooth.framework.simulation_parameters as sim_params

import pytest


def test_params():
    # test constructor
    params = sim_params.SimulationParameters({})
    assert hasattr(params, "start_date")
    assert hasattr(params, "n_intervals")
    assert hasattr(params, "interval_time")
    assert hasattr(params, "date_time_index")
    assert hasattr(params, "sim_time_span")

    nice_sim_params = {
        "start_date": "1/1/2019",
        "n_intervals": 4,
        "interval_time": 8
    }

    faulty_sim_params = [
        ({"start_date": "foo"}, ValueError),
        ({"n_intervals": "bar"}, TypeError),
        ({"interval_time": "baz"}, ValueError),
        ({"not_a_param": None}, ValueError)
    ]

    # test good config
    params = sim_params.SimulationParameters(nice_sim_params)
    for k, v in nice_sim_params.items():
        assert getattr(params, k) == v, "Simulation parameter not set correctly"
    assert len(params.date_time_index.time) == 4
    assert params.date_time_index.freqstr == "8T"
    assert params.sim_time_span == 8*4

    # test bad configs
    for param, error in faulty_sim_params:
        with pytest.raises(error):
            sim_params.SimulationParameters(param)
