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

    def get_pos(self) -> float:
        command = str(self.axis_nr) + 'TP'
        pos = self.controller.query(command)
        return pos
    
    def get_vel(self) -> float:
        command = str(self.axis_nr) + 'TV'
        vel = self.controller.query(command)
        return vel
    
    def get_des_pos(self) -> float:
        command = str(self.axis_nr) + 'DP'
        des_pos = self.controller.query(command)
        return des_pos
    
    def get_set_vel(self) -> float:
        command = str(self.axis_nr) + 'DV'
        set_vel = self.controller.query(command)
        return set_vel
    
    def update_status(self) -> None:
        self.pos = self.get_pos()
        self.vel = self.get_vel()
        self.des_pos = self.get_des_pos()
        self.set_vel = self.get_set_vel()
    



class Motion_Controller():
    def __init__(self, home_positions : [float] = [0, 0, 0]) -> None:
        
        self.controller = self.get_controller()

        self.ax1 = Controller_Axis(1, home_pos = home_positions[0])
        self.ax2 = Controller_Axis(2, home_pos = home_positions[1])
        self.ax3 = Controller_Axis(3, home_pos = home_positions[2])

        self.print_status()


    def get_controller(self) -> SerialInstrument:
        rm = ResourceManager()

        print(rm.list_resources())
        controller = rm.open_resource('ASRL4::INSTR',
                                baud_rate = 19200,
                                read_termination = '\r\n',
                                write_termination = '\r\n',
                                data_bits = 8)
        return controller

    def update_status(self) -> None:

        positions = [None] * 3

        for ax in range(1, 4):
            positions[ax - 1] = self.get_pos(ax)
        
        self.pos_ax1, self.pos_ax2, self.pos_ax3 = positions 
            

    def get_pos(self, ax : int) -> float:
        command = str(ax) + 'TP'
        pos = self.controller.query(command)
        return pos
    
    def get_vel(self, ax : int) -> float:
        command = str(ax) + 'TV'
        vel = self.controller.query(command)
        return vel
    
    def get_des_pos(self, ax : int) -> float:
        command = str(ax) + 'DP'
        des_pos = self.controller.query(command)
        return des_pos
    
    def get_set_vel(self, ax : int) -> float:
        command = str(ax) + 'DV'
        set_vel = self.controller.query(command)
        return set_vel
    
    def set_abs_pos(self, ax : int, pos : int) -> None:
        command = 
    


    def print_status(self) -> None:
        self.update_status()

        print('current positions (mm)')
        print(f'axis 1: {self.pos_ax1}')
        print(f'axis 2: {self.pos_ax2}')
        print(f'axis 3: {self.pos_ax3}')


newport_controller = Motion_Controller()
            




