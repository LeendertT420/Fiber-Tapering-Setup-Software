#made by: G.L. Timmerman
#group: QO Bouwmeester


from pyvisa.resources.serial import SerialInstrument


class AxisController():
    """
    Class for a one axis motorized actuator. This class contains attributes that
    store all relevant positional and velocity parameters of the axis. It also
    contains all methods needed to read and write information from and to the 
    axis. 

    params:
        - axis_nr (int) :   integer referring to the D-Sub connector port the 
                            axis is connected to on the back of the ESP300
                            motion controller. 
        - controller (SerialIntrument) :    SerialInstrument object from the pyvisa
                                            package that is used to send commands to 
                                            motion controller. 
        - home_pos (float) :    position that is refered to as the home position of 
                                the stage, the offset relative to which all positions
                                are measured. Default is 0.
    """
    def __init__(self, axis_nr : int,
                 controller : SerialInstrument,
                 home_pos : float = 0) -> None:
        
        self.axis_nr = axis_nr

        self.controller = controller
        
        self.home_pos = home_pos
        self.pos = None
        self.vel = None

        self.des_pos = None
        self.tot_travel_time = None

        self.set_vel = None



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
    

    def get_des_vel(self) -> float:
        """
        Queries the desired velocity of the axis. This is the velocity of the axis
        when moving to the destination position. This can be different from 
        what self.get_vel() returns or the argument given to self.set_vel()
        when the motor is homing (homing velocity can be different from set velocity),
        in between movements (stationary) or starting up a movement. 
        
        Returns:
            - des_vel (float) : set velocity in mm/s
        """
        command = str(self.axis_nr) + 'DV'
        des_vel = self.controller.query(command)
        return float(des_vel)
    

    def update_axis(self) -> None:
        """
        Update position and velocity metrics by calling the get functions.
        """
        self.pos = self.get_pos()
        self.vel = self.get_vel()
        self.set_vel = self.get_des_vel()


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

        self.des_pos = abs_pos 



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

        self.des_pos = abs_pos


    def set_velocity(self, vel : float) -> None:
        """
        Set the velocity of the axis in mm/s
        
        params:
            - vel (float) :     velocity in mm/s
        """
        command = str(self.axis_nr) + 'VA' + str(vel)
        self.controller.write(command)


    def is_moving(self) -> bool:
        """
        Returns boolean whether axis is moving.

        returns:
            - ismoving (bool) :     returns True if axis has non-zero velocity,
                                    returns False otherwise
        """
        ismoving = self.get_vel() != 0.0
        return ismoving
    

    def turn_on(self) -> None:
        """
        Turn on axis. Axis can only move when it is turned on.
        """
        command = str(self.axis_nr) + 'MO'
        self.controller.write(command)

    
    def turn_off(self) -> None:
        """
        Turn on axis. Axis cannot move when it is turned off.
        """
        command = str(self.axis_nr) + 'MF'
        self.controller.write(command)

    def home(self) -> None:
        """
        Moves to home position of axis
        """
        command = str(self.axis_nr) + 'OR0'
        self.controller.write(command)