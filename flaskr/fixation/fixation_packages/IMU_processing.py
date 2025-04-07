# Mix of cited and original code.

# Steps 3, 4
import numpy as np
from scipy import integrate
from fixation_packages.ingestion import parse_pldata
from scipy.spatial.transform import Rotation as R

class IMU_Processor:
    def __init__(self, IMU_stream_data):
        # self.IMU_stream_data = IMU_stream_data[1].iloc[:]
        self.IMU_stream_data = np.array([parse_pldata(x) for x in IMU_stream_data[1].iloc[:]])  # significant time cost here

        self.current_orientation = None
        self.previous_time = None
        self.angular_velocity = None  
        self.linear_velocity = None

        print("IMU processor init")

    def process_IMU_data(self, sample_idx):
        quaternion = self.get_quaternion(sample_idx)  # Method to extract the current quaternion
        angular_velocity = self.get_angular_velocity(sample_idx)  # Method to extract angular velocity
        
        # Step 2: If this is the first frame, initialize orientation and set time
        if self.current_orientation is None and sample_idx == 0:
            self.current_orientation = quaternion  # Initialize with the first quaternion
            self.previous_time = self.get_current_time(sample_idx)
            return
        
        # Step 3: Update orientation based on angular velocity
        current_time = self.get_current_time(sample_idx)  # Get the current time
        delta_time = current_time - self.previous_time
        
        # Use the angular velocity and time to update the orientation
        # self.update_orientation(angular_velocity, delta_time)
        self.update_orientation(sample_idx)
        
        # Step 4: Store the current time for the next frame
        self.previous_time = current_time

    def get_quaternion(self, sample_idx):
        q_w, q_x, q_y, q_z = self.IMU_stream_data[sample_idx]['orientation_0'], self.IMU_stream_data[sample_idx]['orientation_1'], self.IMU_stream_data[sample_idx]['orientation_2'], self.IMU_stream_data[sample_idx]['orientation_3']
        return np.array([q_w, q_x, q_y, q_z])
    
    def get_angular_velocity(self, sample_idx):
        alpha_x, alpha_y, alpha_z = self.IMU_stream_data[sample_idx]['angular_velocity_0'], self.IMU_stream_data[sample_idx]['angular_velocity_1'], self.IMU_stream_data[sample_idx]['angular_velocity_2']
        return np.array([alpha_x, alpha_y, alpha_z])
    
    def get_current_time(self, sample_idx):
        return self.IMU_stream_data[sample_idx]['timestamp']
    
    def update_orientation(self, sample_idx):
        # angular_velocity_quaternion = self.angular_velocity_to_quaternion(angular_velocity, dt)
        # self.current_orientation = self.current_orientation * angular_velocity_quaternion
        self.current_orientation = self.get_quaternion(sample_idx)

    def angular_velocity_to_quaternion(self, angular_velocity, dt):
        angle = np.linalg.norm(angular_velocity) * dt
        axis = angular_velocity / np.linalg.norm(angular_velocity)
        q_increment = R.from_rotvec(angle * axis).as_quat()
        return q_increment
    

    # The original code for this function was given to us by Brian Szekely, a PhD student and former student of Dr. MacNeilage's Self-Motion Lab
    def quat_to_euler(self, quaternions):
        """
        Convert quaternions to Euler angles.
        
        Roll (φ) = atan2(2(w x + y z), 1 - 2(x^2 + y^2))
        Pitch (θ) = asin(2(w y - z x))
        Yaw (ψ) = atan2(2(w z + x y), 1 - 2(y^2 + z^2))
        """
        # q_w, q_x, q_y, q_z = quaternions[0], quaternions[1], quaternions[2], quaternions[3]
        q_w, q_x, q_y, q_z = quaternions[:, 0], quaternions[:, 1], quaternions[:, 2], quaternions[:, 3]
        #Roll
        roll = np.degrees(np.arctan2(2 * (q_w * q_x + q_y * q_z), 1 - 2 * (q_x**2 + q_y**2)))
        #Pitch
        pitch = np.degrees(np.arcsin(2 * (q_w * q_y - q_z * q_x)))
        #Yaw
        yaw = np.degrees(np.arctan2(2 * (q_w * q_z + q_x * q_y), 1 - 2 * (q_y**2 + q_z**2)))

        return np.column_stack((roll, pitch, yaw))

    # This function is our original work.
    # calculates the optic flow vector given two IMU dataframes
    def calculate_optic_flow_vec(self, IMU_frame, next_frame):
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