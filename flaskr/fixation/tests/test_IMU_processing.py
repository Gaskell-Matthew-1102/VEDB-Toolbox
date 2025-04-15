import pytest
import fixation.fixation_packages.IMU_processing as IMU_processing
import pandas as pd
import numpy as np
import msgpack
import quaternion

d = {
        'timestamp':[0.0, 0.05, 0.11, 0.15, 0.20],
        'orientation_0':[0.0, 0.0, 0.707, 0.707, 0.0],
        'orientation_1':[0.0, 0.707, 0.0, 0.707, 0.0], 
        'orientation_2':[0.707, 0.707, 0.707, 0.0, 0.707], 
        'orientation_3':[0.707, 0.0, 0.0, 0.0, 0.707]
    }

d1 = {
        'timestamp':0.0,
        'orientation_0':0.0,
        'orientation_1':0.0, 
        'orientation_2':0.707, 
        'orientation_3':0.707
    }
d2 = {
        'timestamp':0.05,
        'orientation_0':0.0,
        'orientation_1':0.707, 
        'orientation_2':0.707, 
        'orientation_3':0.0
    }
d3 = {
        'timestamp':0.11,
        'orientation_0':0.707,
        'orientation_1':0.0, 
        'orientation_2':0.707, 
        'orientation_3':0.0
    }
d4 = {
        'timestamp':0.15,
        'orientation_0':0.707,
        'orientation_1':0.707, 
        'orientation_2':0.0, 
        'orientation_3':0.0
    }
d5 = {
        'timestamp':0.20,
        'orientation_0':0.0,
        'orientation_1':0.0, 
        'orientation_2':0.707, 
        'orientation_3':0.707
    }

@pytest.fixture
def setup(mocker):
    ex_df = pd.DataFrame(data=d)
    fake_imu_data = (None, ex_df)
    
    mocker.patch('fixation.fixation_packages.IMU_processing.parse_pldata', side_effect=[d1, d2, d3, d4, d5])
    imu = IMU_processing.IMU_Processor(fake_imu_data, 2048, 1536, 90, 90)
    yield imu

class TestIMUProcessing:
    def test_get_quaternion(self, setup):
        q1 = setup.get_quaternion(0)
        test_q1 = np.quaternion(0.0, 0.0, 0.707, 0.707)
        assert q1 == test_q1

        q2 = setup.get_quaternion(1)
        test_q2 = np.quaternion(0.00, 0.707, 0.707, 0.0)
        assert q2 == test_q2

    def test_get_quaternion_invalid_idx(self, setup):
        with pytest.raises(IndexError) as e_info:
            setup.get_quaternion(5)

    def test_get_angular_velocity(self, setup):
        ang_vel = setup.get_angular_velocity()

        # calculated manually
        assert ang_vel[0] - (-24.184) < 0.01
        assert ang_vel[1] - (24.184) < 0.01
        assert ang_vel[2] - (-24.184) < 0.01

        setup.update()
        ang_vel = setup.get_angular_velocity()
        assert ang_vel[0] - (-20.153) < 0.01
        assert ang_vel[1] - (-20.153) < 0.01
        assert ang_vel[2] - (20.153) < 0.01

    def test_get_time_at(self, setup):
        t1 = setup.get_time_at(0)
        assert t1 == 0.00

        t2 = setup.get_time_at(1)
        assert t2 == 0.05

        t3 = setup.get_time_at(2)
        assert t3 == 0.11

    def test_get_time_at_invalid_idx(self, setup):
        with pytest.raises(IndexError) as e_info:
            setup.get_time_at(1000)

    def test_get_current_time(self, setup):
        t = setup.get_current_time()
        assert t == 0.05

        setup.update()
        t = setup.get_current_time()
        assert t == 0.11

        setup.update()
        t = setup.get_current_time()
        assert t == 0.15

    def test_get_current_sample_idx(self, setup):
        assert setup.get_current_sample_idx() == 1
        setup.update()
        assert setup.get_current_sample_idx() == 2

    def test_calculate_rotational_optic_flow(self, setup):
        out = setup.compute_grid_rotational_flow(100, 100)
        print(out)
        assert out == None

        setup.update()
        out = setup.compute_grid_rotational_flow(100, 100)
        assert out == 0

    def test_calculate_rotational_optic_flow(self, setup):
        a = setup.calculate_rotational_optic_flow(100)
        print(a)
        assert a == 0
        

if __name__ == "__main__":
    setup()