from pyvisa import ResourceManager
from pyvisa.resources.serial import SerialInstrument
from axis_controller import AxisController
from typing import Tuple
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


    def home_all_axes(self) -> None:
        """
        Homes all axes
        """
        for ax in self.axes:
            ax.home()


    def stop_all_axes(self) -> None:
        """
        Stops all axes with the set deceleration.
        """
        self.controller.write('ST') 

    
    def any_axis_moving(self) -> bool:
        """
        Determines whether any of the axes are moving.

        Returns:
        - bool :    True if at least one of the axes is moving,
                    False if none of the axes is moving. 
        """
        for ax in self.axes:
            if ax.moving:
                return True
            
        return False


    def get_errors(self) -> Tuple[bool, str]:
        """
        Retrieves the error messages from the motion controller. The error code
        yields whether an error has occured (>0) or not (=0). If the error code 
        has 3 digits, its first digit yields the axis related to the error. If 
        it has two digits, the error is general and not related to a particular 
        axis. From the code and error message and text for exception that can be
        raised is constructed and returned. 

        returns:
            - error_occured (bool) :    True when error has occured,
                                        False if no error has occured.
            - exception_text (str) :    Text that is raised as Exception when
                                        error occurs.
        """
        command = 'TB?'
        error = self.controller.query(command)

        code, time, message = error.split(',')
    	
        error_occured = (int(code) > 0)

        if not error_occured:
            exception_text = None

        elif len(code) < 3:
            exception_text = f'''An error has occured on the 
                                 ESP300 Motion Controller:\n
                                 {message}'''
            
        else:
            axis_nr = int(code[0])
            exception_text =  f'''An error has occured on the 
                                 ESP300 Motion Controller:\n
                                 Axis {axis_nr}: {message}'''

        return error_occured, exception_text


    def perform_motion(self, positions : list[float],
                       velocities : list[float],
                       rel : bool = False) -> None:
        
        self.turn_on_all_axes()

        self.home_all_axes()

        self.update_status()

        for ax, pos, vel in zip(self.axes, positions, velocities):
            ax.set_vel(vel)
            if rel:
                ax.set_rel_pos(pos)
            else:
                ax.set_abs_pos(pos)

        self.monitor_motion()

        self.turn_off_all_axes()



    def monitor_motion(self, update_interval : float = 0.1) -> None:
        """
        Prints positions and velocities of all three axes in table format. If 
        any of the axes is moving, it will be updated every interval. 

        Params:
        - header (bool) :   Determines whether header with field names is printed.
                            Default is True. 
        """
        self.print_metrics(header=True, overwrite=False)
        
        while self.any_axis_moving():

            self.update_status()

            error_occured, message = self.get_errors()
            if error_occured:
                raise Exception(message)

            self.print_metrics(header = False, overwrite=True)

            time.sleep(update_interval)
        
        self.print_metrics(header=False, overwrite=True)

        print('\n\n')


    def print_metrics(self, header : bool,
                      overwrite : bool) -> None:
        

        if header:
            print('Axis'.ljust(7),
              'Position'.ljust(14),
              'Velocity'.ljust(16),
              'des_pos'.ljust(14),
              'des_vel'.ljust(16),
              'exp. completion time'.ljust(22),
              '% completed'.ljust(7))
    
        elif overwrite:
            print("\033[3A", end="")

        for ax in self.axes:
            print(f'{ax.axis_nr}'.ljust(7),
                  f'{ax.pos:.7f} mm'.ljust(14),
                  f'{ax.vel:.7f} mm/s'.ljust(16),
                  f'{ax.des_pos:.7f} mm'.ljust(14),
                  f'{ax.des_vel:.7f} mm/s'.ljust(16),
                  f'{ax.travel_time:.2f} s'.ljust(22),
                  f'{(ax.perc_done*100):.2f} %')
        



            
        

            