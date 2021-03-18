from smooth.components.external_component import ExternalComponent
import smooth.framework.simulation_parameters as sim_params

import pytest


class TestBasic:

    def test_init(self):
        component = ExternalComponent()
        assert component is not None
        assert hasattr(component, "name")
        assert hasattr(component, "sim_params")

    def test_set_params(self):
        component = ExternalComponent()
        component.set_parameters({})
        # good param
        component.set_parameters({"name": "component"})
        assert component.name == "component"
        # bad param
        with pytest.raises(ValueError):
            component.set_parameters({"foo": "bar"})


class TestUpdate:

    params = sim_params.SimulationParameters({})

    def test_generate_results(self):
        component = ExternalComponent()
        component.set_parameters({})
        component.generate_results()

    def test_check_validity(self):
        component = ExternalComponent()
        component.set_parameters({})
        component.check_validity()
