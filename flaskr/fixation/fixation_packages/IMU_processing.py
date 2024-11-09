# Steps 3, 4
from fixation_packages.vector_operations import vector_subtraction

# calculates the optic flow vector given two IMU dataframes
def calculate_optic_flow_vec(IMU_frame, next_frame):
    VEL_X = 'linear_velocity_0'
    VEL_Y = 'linear_velocity_1'
    VEL_Z = 'linear_velocity_2'

    POS_X = 'position_0'
    POS_Y = 'position_1'
    POS_Z = 'position_2'

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

    delta_x = next_frame[POS_X] - IMU_frame[POS_X]
    delta_y = next_frame[POS_Y] - IMU_frame[POS_Y]
    delta_z = next_frame[POS_Z] - IMU_frame[POS_Z]

    delta_t = next_frame['timestamp'] - IMU_frame['timestamp']

    res_vec = (delta_v_x, delta_v_y, delta_v_z)

    print(res_vec)