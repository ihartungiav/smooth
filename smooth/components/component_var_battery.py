from .component_battery import Battery


class VarBattery(Battery):
    """ Stationary batteries of different types can be created through this class

    The main use is to model different types of batteries within this component and let the
    optimizer choose which of these is best suited in a given energy system.

    The battery_type defines which battery is being used. The capacity and capex can be specified
    for each type.

    :param self.name: unique name of the component
    :type self.name: str

    :param self.battery_type: set the battery type to be used
    :type self.battery_type: int (1-6)

    :param self.battery_capacity_bt1: Storage capacity of specific battery type [W]
    :type self.battery_capacity_bt1: int

    :param self.capex_l1: Capex for each battery type
    :type self.capex_l1: dict

    """

    # def __init__(self, params):
    def __init__(self, *args, **kwargs):

        # Call the init function of the mother class.
        super(VarBattery, self).__init__(*args, **kwargs)

        # ------------------- PARAMETERS -------------------
        self.battery_type = 1

        # Battery capacity (assuming all the capacity can be used) [Wh].
        # Battery type 1: Li_battery 1 - 50 kWh
        self.battery_capacity_bt1 = 10 * 1e3
        # Battery type 2: Li_battery 50 - 1000 kWh
        self.battery_capacity_bt2 = 100 * 1e3
        # Battery type 3: Li_battery > 1000 kWh
        self.battery_capacity_bt3 = 1 * 1e6
        # Battery type 4: ????
        self.battery_capacity_bt4 = 1
        # Battery type 5: ????
        self.battery_capacity_bt5 = 1
        # Battery type 6: ????
        self.battery_capacity_bt6 = 1

        # Capex for each battery type
        self.capex_bt1 = {
            'key': ['poly'],
            'fitting_value': [
                [0, 2109.62368e-3, -147.52325e-6, 6.97016e-9, -0.13996-12, 0.00102e-15]
            ],
            'dependant_value': ['battery_capacity']},

        self.capex_bt2 = {
             'key': ['poly'],
             'fitting_value': [[0, 1000.2 / 1e3, -0.4983 / 1e6]],
             'dependant_value': ['battery_capacity']},

        self.capex_bt3 = {
             'key': ['poly', 'spec'],
             'fitting_value': [[0.353, 0.149], 'cost'],
             'dependant_value': ['c_rate_charge', 'battery_capacity']},

        self.capex_bt4 = {
            'key': ['poly'],
            'fitting_value': [[1, 1]],
            'dependant_value': ['output_max']}

        self.capex_bt5 = {
            'key': ['poly'],
            'fitting_value': [[1, 1]],
            'dependant_value': ['output_max']}

        self.capex_bt6 = {
            'key': ['poly'],
            'fitting_value': [[1, 1]],
            'dependant_value': ['output_max']}

        # ------------------- UPDATE PARAMETER DEFAULT VALUES -------------------
        # self.set_parameters(params)
        self.__dict__.update(*args, **kwargs)
        if self.battery_type == 1:
            self.battery_capacity = self.battery_capacity_bt1
            self.capex = self.capex_bt1
        elif self.battery_type == 2:
            self.battery_capacity = self.battery_capacity_bt2
            self.capex = self.capex_bt2
        elif self.battery_type == 3:
            self.battery_capacity = self.battery_capacity_bt3
            self.capex = self.capex_bt3
        elif self.battery_type == 4:
            self.battery_capacity = self.battery_capacity_bt4
            self.capex = self.capex_bt4
        elif self.battery_type == 5:
            self.battery_capacity = self.battery_capacity_bt5
            self.capex = self.capex_bt5
        elif self.battery_type == 6:
            self.battery_capacity = self.battery_capacity_bt6
            self.capex = self.capex_bt6

        self.c_rate_discharge = self.c_rate
        self.c_rate_charge = self.c_rate
        # This value can be used as faktor in capex to add an insignificant cost for higher c-rates.
        # The optimization then strives towards a low c-rate,
        # even for price models which are otherwise independet of the c-rate
        self.c_rate_insig_cost = 1 + self.c_rate * 0.00001
