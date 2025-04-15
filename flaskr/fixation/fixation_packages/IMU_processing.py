# Mix of cited and original code.

# Steps 3, 4
import numpy as np
import quaternion
import math
from scipy import integrate
# from fixation_packages.ingestion import parse_pldata
from .ingestion import parse_pldata
from scipy.spatial.transform import Rotation as R

class IMU_Processor:
    def __init__(self, IMU_stream_data, image_width, image_height, camera_fov_h, camera_fov_v):
        self.IMU_stream_data = np.array([parse_pldata(x) for x in IMU_stream_data[1].iloc[:]])  # significant time cost here
        self.current_sample_idx = 0  # Initially set it to an invalid index (e.g., -1)
        
        # World scene camera variables
        self.camera_fov_h = camera_fov_h
        self.camera_fov_v = camera_fov_v
        self.image_width = image_width
        self.image_height = image_height

        self.current_orientation = self.get_quaternion(self.current_sample_idx)
        self.previous_orientation = None

        self.previous_time = None
        # self.linear_velocity = None     # no longer needed as the full optic flow equation needs Z (depth) to estimate optic flow
        self.angular_velocity = None
        self.update()
        print("IMU processor initialized")

    def update(self):
        self.current_sample_idx += 1
        if self.current_sample_idx >= self.IMU_stream_data.size:
            raise IndexError("Sample index exceeds data length.")
                
        self.previous_orientation = self.current_orientation
        self.update_orientation(self.current_sample_idx)

        self.previous_time = self.get_time_at(self.current_sample_idx-1)


        self.angular_velocity = self.get_angular_velocity()
        
    def get_current_sample_idx(self):
        return self.current_sample_idx

    def get_quaternion(self, sample_idx):
        q_w, q_x, q_y, q_z = self.IMU_stream_data[sample_idx]['orientation_0'], self.IMU_stream_data[sample_idx]['orientation_1'], self.IMU_stream_data[sample_idx]['orientation_2'], self.IMU_stream_data[sample_idx]['orientation_3']
        return np.quaternion(q_w, q_x, q_y, q_z)
    
    def get_angular_velocity(self):
        prev_quat = self.previous_orientation
        current_quat = self.current_orientation

        delta_quat = current_quat * prev_quat.inverse()
        log_q_delta = np.log(delta_quat)
        delta_time = self.get_current_time() - self.previous_time
        out = (2 * log_q_delta.imag) / delta_time
        return out
    
    def get_time_at(self, sample_idx):
        return self.IMU_stream_data[sample_idx]['timestamp']
    
    def get_current_time(self):
        return self.IMU_stream_data[self.current_sample_idx]['timestamp']
    
    def update_orientation(self, sample_idx):
        self.current_orientation = self.get_quaternion(sample_idx)
    
    # def calculate_optic_flow_vec(self, IMU_frame, next_frame):
    #     VEL_X = 'linear_velocity_0'
    #     VEL_Y = 'linear_velocity_1'
    #     VEL_Z = 'linear_velocity_2'

    #     delta_v_x = next_frame[VEL_X] - IMU_frame[VEL_X]
    #     delta_v_y = next_frame[VEL_Y] - IMU_frame[VEL_Y]
    #     delta_v_z = next_frame[VEL_Z] - IMU_frame[VEL_Z]
    #     delta_t = next_frame['timestamp'] - IMU_frame['timestamp']

    #     guh0 = (IMU_frame[VEL_X] + next_frame[VEL_X]) / 2 * delta_t
    #     guh1 = (IMU_frame[VEL_Y] + next_frame[VEL_Y]) / 2 * delta_t
    #     guh2 = (IMU_frame[VEL_Z] + next_frame[VEL_Z]) / 2 * delta_t

    #     return np.array([delta_v_x, delta_v_y, delta_v_z]), np.array([guh0, guh1, guh2])

    def calculate_rotational_optic_flow(self, raw_x, raw_y):
        omega_x, omega_y, omega_z = self.angular_velocity

        x_centered = self.image_width/2
        y_centered = self.image_height/2

        f_horizontal = self.image_width / (2 * math.tan(self.camera_fov_h/2))
        f_vertical = self.image_height / (2 * math.tan(self.camera_fov_v/2))

        x = (raw_x - x_centered)/f_horizontal
        y = (raw_y - y_centered)/f_vertical

        x_dot = x*y*omega_x - (1 + x*x)*omega_y + y*omega_z
        y_dot = (1 + y*y)*omega_x - x*y*omega_y - x*omega_z

        return np.array([x_dot, y_dot])

    def create_grid(self, shape, step):
        """Create a grid of points over the image."""
        h, w = shape
        y, x = np.mgrid[step//2:h:step, step//2:w:step]  # Generate grid points
        return np.float32(np.stack((x, y), axis=-1).reshape(-1, 1, 2))  # Reshape to (N, 1, 2)
    
    def compute_grid_rotational_flow(self, step):
        """Compute rotational optic flow over a grid."""
        grid_points = self.create_grid((self.image_height, self.image_width), step)

        flow_vectors = []
        for point in grid_points[:, 0, :]:  # point shape is (N, 2)
            raw_x, raw_y = point
            flow = self.calculate_rotational_optic_flow(raw_x, raw_y)
            flow_vectors.append(flow)

        return np.array(flow_vectors)
