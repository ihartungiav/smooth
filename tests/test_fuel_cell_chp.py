from smooth.components.component_fuel_cell_chp import FuelCellChp
from smooth.framework.simulation_parameters import SimulationParameters
import oemof.solph as solph


# todo: figure out how to do tests for get_el_energy_by_h2 and get_th_energy_by_h2
# todo: test constraints/flows are equal into each component

class TestBasic:
    sim_params = SimulationParameters({})

    def test_init(self):
        fc_chp = FuelCellChp({"sim_params": self.sim_params})
        assert hasattr(fc_chp, "bus_h2")
        assert hasattr(fc_chp, "bus_el")
        assert hasattr(fc_chp, "bus_th")
        assert hasattr(fc_chp, "life_time")
        assert hasattr(fc_chp, "heating_value_h2")

        fc_chp = FuelCellChp({"sim_params": self.sim_params, "power_max": 100})
        assert fc_chp.power_max == 100
        assert fc_chp.h2_input_max == 20000 / 2463087
        # todo: move to actual component, then test what happens when other type is passed in
        if not isinstance(fc_chp.bp_load_el, list):
            raise TypeError("A list is needed for the electrical efficiency load break points!")
        if not isinstance(fc_chp.bp_eff_el, list):
            raise TypeError("A list is needed for the electrical efficiency break points!")
        if not isinstance(fc_chp.bp_load_th, list):
            raise TypeError("A list is needed for the thermal efficiency load break points!")
        if not isinstance(fc_chp.bp_eff_th, list):
            raise TypeError("A list is needed for the thermal efficiency break points!")

        bp_ld_el = [0.0, 0.0481, 0.0694, 0.0931, 0.1272, 0.1616, 0.2444, 0.5912, 1.0]
        h2_cons_el = [this_bp * (20000/2463087) for this_bp in bp_ld_el]

        for i in range(len(h2_cons_el)):
            assert h2_cons_el[i] == fc_chp.bp_h2_consumed_el[i]

        bp_ld_th = [0.0, 0.0517, 0.1589, 0.2482, 1.0]
        h2_cons_th = [this_bp * (20000/2463087) for this_bp in bp_ld_th]

        for i in range(len(h2_cons_th)):
            assert h2_cons_th[i] == fc_chp.bp_h2_consumed_th[i]

    def test_add_to_oemof_model(self):
        fc_chp = FuelCellChp({
            "bus_h2": "bus1",
            "bus_el": "bus2",
            "bus_th": "bus3",
            "sim_params": self.sim_params
        })

        oemof_model = solph.EnergySystem(
            timeindex=self.sim_params.date_time_index[0:1],
            freq='{}min'.format(self.sim_params.interval_time)
        )
        fc_chp.add_to_oemof_model({
            "bus1": solph.Bus(label="bus1"),
            "bus2": solph.Bus(label="bus2"),
            "bus3": solph.Bus(label="bus3")
        }, oemof_model)
        assert fc_chp.model_el is not None and fc_chp.model_th is not None

        assert type(fc_chp.model_el) == solph.custom.PiecewiseLinearTransformer
        assert type(fc_chp.model_th) == solph.custom.PiecewiseLinearTransformer
        assert len(fc_chp.model_el.inputs) == 1
        assert len(fc_chp.model_el.outputs) == 1
        assert len(fc_chp.model_th.inputs) == 1
        assert len(fc_chp.model_th.outputs) == 1
