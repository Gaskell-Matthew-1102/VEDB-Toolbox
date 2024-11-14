# Steps 3, 4
import numpy as np
from scipy import integrate

def quat_to_euler(quaternions):
    """
    Convert quaternions to Euler angles.
    
    Roll (φ) = atan2(2(w x + y z), 1 - 2(x^2 + y^2))
    Pitch (θ) = asin(2(w y - z x))
    Yaw (ψ) = atan2(2(w z + x y), 1 - 2(y^2 + z^2))
    """
    q_w, q_x, q_y, q_z = quaternions[:, 0], quaternions[:, 1], quaternions[:, 2], quaternions[:, 3]
    #Roll
    roll = np.degrees(np.arctan2(2 * (q_w * q_x + q_y * q_z), 1 - 2 * (q_x**2 + q_y**2)))
    #Pitch
    pitch = np.degrees(np.arcsin(2 * (q_w * q_y - q_z * q_x)))
    #Yaw
    yaw = np.degrees(np.arctan2(2 * (q_w * q_z + q_x * q_y), 1 - 2 * (q_y**2 + q_z**2)))

    return np.column_stack((roll, pitch, yaw))

# calculates the optic flow vector given two IMU dataframes
def calculate_optic_flow_vec(IMU_frame, next_frame):
    VEL_X = 'linear_velocity_0'
    VEL_Y = 'linear_velocity_1'
    VEL_Z = 'linear_velocity_2'


    #         Z (up, down)
    #         ^
    #         |
    #         |
    #         | 
    #         +-----------> Y   (left, right)
    #        /
    #       /
    #      /
    #     X (forward, backward)

    delta_v_x = next_frame[VEL_X] - IMU_frame[VEL_X]
    delta_v_y = next_frame[VEL_Y] - IMU_frame[VEL_Y]
    delta_v_z = next_frame[VEL_Z] - IMU_frame[VEL_Z]

    delta_t = next_frame['timestamp'] - IMU_frame['timestamp']

    guh0 = (IMU_frame[VEL_X] + next_frame[VEL_X])/2 * delta_t       # trapezoidal integration
    guh1 = (IMU_frame[VEL_Y] + next_frame[VEL_Y])/2 * delta_t
    guh2 = (IMU_frame[VEL_Z] + next_frame[VEL_Z])/2 * delta_t


    res_vec = (delta_v_x, delta_v_y, delta_v_z)
    guh_vec = (guh0, guh1, guh2)

    print(guh_vec)