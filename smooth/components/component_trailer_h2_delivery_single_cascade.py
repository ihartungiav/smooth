import oemof.solph as solph
from .component import Component
from oemof.outputlib import views


class TrailerH2DeliverySingleCascade(Component):
    """Component created for a hydrogen trailer delivery"""

    def __init__(self, params):

        # Call the init function of the mother class.
        Component.__init__(self)

        # ------------------- PARAMETERS -------------------
        self.name = 'Trailer_default_name'

        self.bus_in = None
        self.bus_out_1 = None
        self.bus_out_2 = None

        # ToDo: Calculate pressure of hydrogen in trailer
        # ToDo: At the moment only the variable costs per distance travelled are taken into
        #  consideration, but the update_var_costs() function can be modified to allow for
        #  the variable costs per kg of hydrogen transported as well
        # ToDo: At the moment, it is assumed that the hydrogen can be delivered within one
        #  hour - this needs to be changed if the single trip distance from the origin to
        #  destination is longer than 45 minutes (1 hour - 15 mins refuelling)

        # Trailer capacity (at maximum pressure) [kg]
        self.trailer_capacity = 900

        # Define the threshold value for the artificial costs.
        # The threshold for the destination storage to encourage/discourage the use of the trailer
        # (percentage of capacity) [-]
        self.fs_destination_storage_threshold_1 = None
        self.fs_destination_storage_threshold_2 = None
        # The amount of hydrogen needed [kg]
        self.hydrogen_needed = 0
        # The amount of hydrogen delivered to first destination [kg]
        self.output_h2_1 = 0
        # The amount of hydrogen delivered to second destination [kg]
        self.output_h2_2 = 0
        # The amount of hydrogen needed [kg]
        self.fs_origin_available_kg = None

        # ------------------- UPDATE PARAMETER DEFAULT VALUES -------------------
        self.set_parameters(params)

        # ------------------- INTERNAL VALUES -------------------
        # The current artificial cost value [EUR/kg].
        self.current_ac = 0

    def prepare_simulation(self, components):
        # Check level of destination storage component: if it is below specified threshold,
        # implement low artificial costs (to encourage system to fill it)
        # Check level of all non-central storage component and use the one with the highest amount of h2:
        # if it is below specified threshold, the trailer cannot take any hydrogen from it
        if self.fs_component_name is not None:
            # Obtains the origin storage level [kg]
            fs_origin_storage_level_kg_1 = self.get_foreign_state_value(components, index=0)
            # Obtains the origin min storage level [kg]
            fs_origin_min_storage_level_1 = self.get_foreign_state_value(components, index=1)
            # Obtains the origin capacity [kg]
            fs_origin_capacity_1 = self.get_foreign_state_value(components, index=2)

            # Obtains the available mass that can be taken from the origin storage [kg]
            fs_origin_available_kg_1 = min((fs_origin_storage_level_kg_1 - fs_origin_min_storage_level_1),
                                           fs_origin_capacity_1 / 2)

            # Get the availability mass of hydrogen of the fullest origin storage
            self.fs_origin_available_kg = fs_origin_available_kg_1

            # Obtains the first destination storage level [kg]
            fs_destination_storage_level_kg_1 = self.get_foreign_state_value(components, index=3)
            # Obtains the first destination storage capacity [kg]
            fs_destination_storage_capacity_1 = self.get_foreign_state_value(components, index=4)
            # Obtains the second destination storage level [kg]
            fs_destination_storage_level_kg_2 = self.get_foreign_state_value(components, index=5)
            # Obtains the second destination storage capacity [kg]
            fs_destination_storage_capacity_2 = self.get_foreign_state_value(components, index=6)

            # Obtains the available mass that can be delivered to the first destination storage [kg]
            fs_destination_available_storage_1 = \
                fs_destination_storage_capacity_1 - fs_destination_storage_level_kg_1

            # Obtains the available mass that can be delivered to the second destination storage [kg]
            fs_destination_available_storage_2 = \
                fs_destination_storage_capacity_2 - fs_destination_storage_level_kg_2

            # check threshold of first storage
            if fs_destination_storage_level_kg_1 \
                    < self.fs_destination_storage_threshold_1 * fs_destination_storage_capacity_1:
                # check threshold of second storage
                if fs_destination_storage_level_kg_2 \
                        < self.fs_destination_storage_threshold_2 * fs_destination_storage_capacity_2:
                    available_storage_tot = \
                        fs_destination_available_storage_1 + fs_destination_available_storage_2

                    # calculate the amount of hydrogen which gets delivered
                    if available_storage_tot >= self.trailer_capacity \
                            and self.fs_origin_available_kg >= self.trailer_capacity:
                        self.hydrogen_needed = self.trailer_capacity
                        # calculate the amount of hydrogen which gets delivered to storage one and two
                        if fs_destination_available_storage_1 >= self.trailer_capacity:
                            self.output_h2_1 = self.trailer_capacity
                            self.output_h2_2 = 0
                        else:
                            self.output_h2_1 = fs_destination_available_storage_1
                            self.output_h2_2 = \
                                self.trailer_capacity - fs_destination_available_storage_1

                    elif available_storage_tot \
                            > self.trailer_capacity > self.fs_origin_available_kg:
                        self.hydrogen_needed = self.fs_origin_available_kg
                        # calculate the amount of hydrogen which gets delivered to storage one and two
                        if self.fs_origin_available_kg <= fs_destination_available_storage_1:
                            self.output_h2_1 = self.fs_origin_available_kg
                            self.output_h2_2 = 0
                        else:
                            self.output_h2_1 = fs_destination_available_storage_1
                            self.output_h2_2 = \
                                self.fs_origin_available_kg - fs_destination_available_storage_1

                    else:
                        self.hydrogen_needed = available_storage_tot
                        self.output_h2_1 = fs_destination_available_storage_1
                        self.output_h2_2 = fs_destination_available_storage_2

                else:
                    available_storage = fs_destination_available_storage_1
                    self.output_h2_2 = 0

                    if available_storage >= self.trailer_capacity \
                            and self.fs_origin_available_kg >= self.trailer_capacity:
                        self.hydrogen_needed = self.trailer_capacity
                        self.output_h2_1 = self.trailer_capacity

                    elif available_storage \
                            > self.trailer_capacity > self.fs_origin_available_kg:
                        self.hydrogen_needed = self.fs_origin_available_kg
                        self.output_h2_1 = self.fs_origin_available_kg

                    else:
                        self.hydrogen_needed = available_storage
                        self.output_h2_1 = available_storage

            else:
                self.hydrogen_needed = 0

        self.current_ac = self.get_costs_and_art_costs()

    def create_oemof_model(self, busses, _):
        trailer = solph.Transformer(
            label=self.name,
            outputs={busses[self.bus_out_1]: solph.Flow(variable_costs=self.current_ac,
                                                        nominal_value=self.output_h2_1),
                     busses[self.bus_out_2]: solph.Flow(nominal_value=self.output_h2_2)},
            inputs={busses[self.bus_in]: solph.Flow(nominal_value=self.hydrogen_needed)})
        return trailer
