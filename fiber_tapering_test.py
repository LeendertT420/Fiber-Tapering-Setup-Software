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
        return pos
    

    def get_vel(self) -> float:
        """
        Queries the current velocity of the axis. 

        Returns:
            - vel (float) : current velocity in mm/s
        """
        command = str(self.axis_nr) + 'TV'
        vel = self.controller.query(command)
        return vel
    

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
        return des_pos
    

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
        return set_vel
    

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
        print(str(vel))
        command = str(self.axis_nr) + 'VA' + str(vel)
        self.controller.write(command)

    



class Motion_Controller():
    def __init__(self, home_positions : [float] = [0, 0, 0]) -> None:
        
        self.controller = self.get_controller()

        ax1 = Controller_Axis(1, self.controller, home_pos = home_positions[0])
        ax2 = Controller_Axis(2, self.controller, home_pos = home_positions[1])
        ax3 = Controller_Axis(3, self.controller, home_pos = home_positions[2])

        self.axes = [ax1, ax2, ax3]

        self.print_status()


    def get_controller(self) -> SerialInstrument:
        rm = ResourceManager()

        print(rm.list_resources())
        controller = rm.open_resource('ASRL3::INSTR',
                                baud_rate = 19200,
                                read_termination = '\r\n',
                                write_termination = '\r\n',
                                data_bits = 8)
        return controller


    def update_status(self) -> None:

        for ax in self.axes:
            ax.update_axis()
        
    


    def print_status(self) -> None:

        for ax in self.axes:
            ax.update_axis()
            print(f'Axis {ax.axis_nr}')
            print(f'pos: {ax.pos} mm')
            print(f'vel: {ax.vel} mm/s')
            print(f'des_pos: {ax.des_pos} mm')
            print(f'set_vel: {ax.set_vel} mm/s')
            print()
        print()





controller = Motion_Controller()

for ax in controller.axes:
    ax.set_velocity(0.2)
    ax.set_abs_pos(25)

while True:
    controller.print_status()
    time.sleep(0.5)




            




