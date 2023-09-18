from pyvisa import ResourceManager
from pyvisa.resources.serial import SerialInstrument
import time

class Controller_Axis():
    def __init__(self, axis_nr : int,
                 controller : SerialInstrument,
                 home_pos : float = 0) -> None:
        
        self.axis_nr = axis_nr

        self.controller = controller
        
        self.home_pos = home_pos
        self.pos = None
        self.vel = None
        self.des_pos = None
        self.set_vel = None

        self.update_axis()


    def get_pos(self) -> float:
        """
        Queries the current position of the axis relative to the home postion. 

        Returns:
            - pos (float) : current position in mm
        """
        command = str(self.axis_nr) + 'TP'
        pos = self.controller.query(command)
        return float(pos)
    

    def get_vel(self) -> float:
        """
        Queries the current velocity of the axis. 

        Returns:
            - vel (float) : current velocity in mm/s
        """
        command = str(self.axis_nr) + 'TV'
        vel = self.controller.query(command)
        return float(vel)
    

    def get_des_pos(self) -> float:
        """
        Queries the destination position of the axis relative to the home 
        position. Only relevant if the axis is moving. It gives the position 
        the axis is moving to. 

        Returns:
            - des_pos (float) : destination position in mm
        """
        command = str(self.axis_nr) + 'DP'
        des_pos = self.controller.query(command)
        return float(des_pos)
    

    def get_set_vel(self) -> float:
        """
        Queries the set velocity of the axis. This is the velocity of the axis
        when moving to the destination position. This can be different from 
        what self.get_vel() returns when the motor is homing (homing velocity
        can be different from set velocity), in between movements (stationary)
        or starting up a movement. 
        
        Returns:
            - set_vel (float) : set velocity in mm/s
        """
        command = str(self.axis_nr) + 'DV'
        set_vel = self.controller.query(command)
        return float(set_vel)
    

    def update_axis(self) -> None:
        """
        Update position and velocity metrics by calling the get functions.
        """
        self.pos = self.get_pos()
        self.vel = self.get_vel()
        self.des_pos = self.get_des_pos()
        self.set_vel = self.get_set_vel()


    def set_abs_pos(self, abs_pos : float) -> None:
        """
        Set the absolute destination position of the axis relative to the home
        position. 

        params:
            - abs_pos (float) : absolute position to move to in mm
        """
        if abs_pos < self.home_pos or abs_pos > 25 + self.home_pos:
            raise Exception("Position is out of range")
        
        command = str(self.axis_nr) + 'PA' + str(abs_pos)
        self.controller.write(command)


    def set_rel_pos(self, rel_pos : float) -> None:
        """
        Set the destination position of the axis relative to its current position.  

        params:
            - rel_pos (float) : relative position to move to in mm
        """
        abs_pos = rel_pos + self.get_pos()

        if abs_pos < self.home_pos or abs_pos > 25 + self.home_pos:
            raise Exception("Position is out of range")
        
        command = str(self.axis_nr) + 'PR' + str(rel_pos)
        self.controller.write(command)


    def set_velocity(self, vel : float) -> None:
        command = str(self.axis_nr) + 'VA' + str(vel)
        self.controller.write(command)


    def is_moving(self) -> bool:
        return float(self.get_vel()) != 0.0
    



class Motion_Controller():
    def __init__(self, home_positions : [float] = [0, 0, 0]) -> None:
        
        self.controller = self.get_controller()

        ax1 = Controller_Axis(1, self.controller, home_pos = home_positions[0])
        ax2 = Controller_Axis(2, self.controller, home_pos = home_positions[1])
        ax3 = Controller_Axis(3, self.controller, home_pos = home_positions[2])

        self.axes = [ax1, ax2, ax3]

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


    def print_status(self, header : bool = True) -> None:
        """
        Prints positions and velocities of all three axes in table format

        Params:
        - header (bool) :   Determines whether header with field names is printed.
                            Default is True. 
        """

        if header:
            print('Axis'.ljust(7),
                  'Position'.ljust(14),
                  'Velocity'.ljust(16),
                  'des_pos'.ljust(14),
                  'set_vel'.ljust(16))
        
        for ax in self.axes:   
            print(f'{ax.axis_nr}'.ljust(7),
                  f'{ax.pos} mm'.ljust(14),
                  f'{ax.vel} mm/s'.ljust(16),
                  f'{ax.des_pos} mm'.ljust(14),
                  f'{ax.set_vel} mm/s'.ljust(16))






if __name__ == '__main__':


    controller = Motion_Controller()

    for ax in controller.axes:
       ax.set_velocity(0.2)
       ax.set_abs_pos(0)

    header = True

    while controller.any_axis_moving():
        controller.update_status()
        controller.print_status(header=header)
        print("\033[3A", end="")

        header = False

        time.sleep(0.2)


    controller.print_status(header=header)


COLOR = {
    "HEADER": "\033[95m",
    "BLUE": "\033[94m",
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "ENDC": "\033[0m",
}
print()
print('code made by \033[94mG\033[94m\033[93me\033[93m\033[92me\033[92m\033[91mr\033[91m\033[94mt \033[94m\033[93mT\033[93m\033[92mi\033[92m\033[91mm\033[91m\033[94mm\033[94m\033[93me\033[93m\033[92mr\033[92m\033[91mm\033[91m\033[94ma\033[94m\033[93mn\033[93m\033[0m')
            




