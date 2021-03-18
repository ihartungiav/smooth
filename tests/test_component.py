import smooth.components.component as com
import smooth.framework.simulation_parameters as sim_params

import pytest


class TestBasic:

    def test_init(self):
        component = com.Component()
        assert component is not None
        assert hasattr(component, "component")
        assert hasattr(component, "name")
        assert hasattr(component, "sim_params")

    def test_set_params(self):
        component = com.Component()
        # empty param
        component.set_parameters({})
        # good param
        component.set_parameters({"name": "component"})
        assert component.name == "component"
        # bad param
        with pytest.raises(ValueError):
            component.set_parameters({"foo": "bar"})

        # edge cases: costs and emissions need values
        with pytest.raises(AssertionError):
            component.set_parameters({"variable_costs": True})
        with pytest.raises(AssertionError):
            component.set_parameters({"artificial_costs": True})
        component.set_parameters({"dependency_flow_costs": 0})
        component.set_parameters({"variable_costs": True})

        with pytest.raises(AssertionError):
            component.set_parameters({"variable_emissions": True})
        component.set_parameters({"dependency_flow_emissions": 0})
        component.set_parameters({"variable_emissions": True})


class TestUpdate:

    params = sim_params.SimulationParameters({})

    def test_update_flows(self):
        pass  # needs oemof result

    def test_update_var_costs(self):
        component = com.Component()
        component.set_parameters({"sim_params": self.params})
        component.update_var_costs()
        assert "variable_costs" in component.results.keys()
        assert sum(component.results["variable_costs"]) == 0
        assert "art_costs" in component.results.keys()
        assert sum(component.results["art_costs"]) == 0

        # need flows for further testing. Flows are set using update_flows.

    def test_update_var_emissions(self):
        component = com.Component()
        component.set_parameters({"sim_params": self.params})
        component.update_var_emissions()
        assert "variable_emissions" in component.results.keys()
        assert sum(component.results["variable_emissions"]) == 0

        # need flows for further testing

    def test_get_costs(self):
        component = com.Component()
        component.set_parameters({"sim_params": self.params})
        component.update_var_costs()
        assert component.get_costs_and_art_costs() == 0
        component.set_parameters({
            "variable_costs": 3,
            "artificial_costs": 4,
            "dependency_flow_costs": ""
        })
        assert component.get_costs_and_art_costs() == 7

    def test_get_foreign_state_value(self):
        # TODO
        pass

    def test_generate_results(self):
        # check framework functions individually
        pass

    def test_check_validity(self):
        component = com.Component()
        component.check_validity()
