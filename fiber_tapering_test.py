from motion_controller_interface import MotionControllerInterface
import time


def main(controller : MotionControllerInterface) -> None:

    controller.turn_on_all_axes()



    controller.print_status(update_interval=1)

    controller.turn_off_all_axes()


def exception_handler(controller : MotionControllerInterface) -> None:
    controller.stop_all_axes()
    controller.turn_off_all_axes()


if __name__ == '__main__':
    try:
        controller = MotionControllerInterface()
        main(controller)
    except Exception as err:
        print(err)
        exception_handler(controller)




