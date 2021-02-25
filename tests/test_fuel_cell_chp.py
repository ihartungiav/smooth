from smooth.components.component_fuel_cell_chp import FuelCellChp
from smooth.framework.simulation_parameters import SimulationParameters
import oemof.solph as solph


# todo: figure out how to do tests for get_el_energy_by_h2 and get_th_energy_by_h2

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
        if not isinstance(fc_chp.bp_load_el, list):
            # todo: maybe comments are not necessary
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

    def test_create_oemof_model(self):
        fc_chp = FuelCellChp({
            "bus_h2": "foo",
            "bus_el": "bar",
            "bus_th": "baz",
            "sim_params": self.sim_params
        })

        model_el = None
        model_th = None
        
        fc_chp_el = fc_chp.create_oemof_model({
            "foo": solph.Bus(label="foo"),
            "bar": solph.Bus(label="bar")}, model_el)

        fc_chp_th = fc_chp.create_oemof_model({
            "foo": solph.Bus(label="foo"),
            "baz": solph.Bus(label="baz")}, model_th)

        assert type(fc_chp_el) == solph.custom.PiecewiseLinearTransformer
        assert type(fc_chp_th) == solph.custom.PiecewiseLinearTransformer
        assert len(fc_chp_el.inputs) == 1
