from motion_controller_interface import MotionControllerInterface
import traceback
import time

if __name__ == '__main__':
    try:
        controller = MotionControllerInterface()
        controller.perform_motion(positions=[5, 5, 5],
                                  velocities=[.1, .1, .1])

    except:
        controller.exception_handler(traceback.format_exc())




