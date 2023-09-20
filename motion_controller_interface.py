from pyvisa import ResourceManager
from pyvisa.resources.serial import SerialInstrument
from axis_controller import AxisController
import time


class MotionControllerInterface():
    def __init__(self, home_positions : [float] = [0, 0, 0]) -> None:
        
        self.controller = self.get_controller()

        self.ax1 = AxisController(1, self.controller, home_pos = home_positions[0])
        self.ax2 = AxisController(2, self.controller, home_pos = home_positions[1])
        self.ax3 = AxisController(3, self.controller, home_pos = home_positions[2])

        self.axes = [self.ax1, self.ax2, self.ax3]

        self.update_status()


    def get_controller(self) -> SerialInstrument:
        """
        Find instruments and creates instrument object to send
        commands to the ESP300 motion controller
        
        Returns: 
        - controller (SerialInstrument) :   instrument object from PyVisa package
                                            that is used to send commands to controller"""

        rm = ResourceManager()
        resources = rm.list_resources()

        if len(resources) == 0:
            raise Exception('No resources found')

        print('Found resources:')
        for resource in resources:
            print(resource)
            
        for instr in resources:
            try:
                instrument = rm.open_resource(instr,
                                baud_rate = 19200,
                                read_termination = '\r\n',
                                write_termination = '\r\n',
                                data_bits = 8)
                
                instrument_id = instrument.query("*IDN?")

                if instrument_id == 'ESP300 Version 3.08 09/09/02':
                    print(f'Motion controller succesfully found!')
                    print(f'Instrument ID: \033[92m{instrument_id}\033[0m')
                    return instrument
                else:
                    continue
                
            except:
                continue

        raise Exception('ESP300 motion controller was not found.')


    def update_status(self) -> None:
        """
        Update status of all axes. 
        """
        for ax in self.axes:
            ax.update_axis()


    def turn_on_all_axes(self) -> None:
        """
        Turns on all axes
        """
        for ax in self.axes:
            ax.turn_on()


    def turn_off_all_axes(self) -> None:
        """
        Turns off all axes
        """
        for ax in self.axes:
            ax.turn_off()
        
    
    def any_axis_moving(self) -> bool:
        """
        Determines whether any of the axes are moving.

        Returns:
        - bool :    True if at least one of the axes is moving,
                    False if none of the axes is moving. 
        """
        for ax in self.axes:
            if ax.is_moving():
                return True
            
        return False


    def print_status(self, update_interval : float = 0.1) -> None:
        """
        Prints positions and velocities of all three axes in table format. If 
        any of the axes is moving, it will be updated every interval. 

        Params:
        - header (bool) :   Determines whether header with field names is printed.
                            Default is True. 
        """

        print('Axis'.ljust(7),
              'Position'.ljust(14),
              'Velocity'.ljust(16),
              'des_pos'.ljust(14),
              'des_vel'.ljust(16),
              'exp. completion time'.ljust(22),
              '% completed'.ljust(7))
        
        first_iteration = True

        while self.any_axis_moving() or first_iteration:

            self.update_status()
                
            for ax in self.axes:
                completion_time = abs(ax.pos-ax.des_pos)/ax.vel

                if first_iteration: 
                    tot_completion_time = completion_time

                perc_complete = (tot_completion_time - completion_time) / tot_completion_time


                print(f'{ax.axis_nr}'.ljust(7),
                      f'{ax.pos:.7f} mm'.ljust(14),
                      f'{ax.vel:.7f} mm/s'.ljust(16),
                      f'{ax.des_pos:.7f} mm'.ljust(14),
                      f'{ax.set_vel:.7f} mm/s'.ljust(16),
                      f'{completion_time:.2f} s'.ljust(22),
                      f'{(perc_complete*100):.2f} %')
                
            print("\033[3A", end="")

            first_iteration = False

            time.sleep(update_interval)

            
        

            