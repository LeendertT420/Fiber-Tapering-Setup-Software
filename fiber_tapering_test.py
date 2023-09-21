from motion_controller_interface import MotionControllerInterface
import time

if __name__ == '__main__':
    controller = MotionControllerInterface()

    controller.turn_on_all_axes()

    for ax in controller.axes:
       ax.set_velocity(0.05)
       ax.set_abs_pos(23)

    controller.print_status(update_interval=1)

    controller.turn_off_all_axes()

COLOR = {
    "HEADER": "\033[95m",
    "BLUE": "\033[94m",
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "ENDC": "\033[0m",
}
print()
print('code made by \033[95mG\033[95m\033[93me\033[93m\033[92me\033[92m\033[91mr\033[91m\033[94mt \033[94m\033[93mT\033[93m\033[92mi\033[92m\033[91mm\033[91m\033[94mm\033[94m\033[93me\033[93m\033[92mr\033[92m\033[91mm\033[91m\033[94ma\033[94m\033[93mn\033[93m\033[0m')
            




