import pytest
import fixation.fixation_packages.spatial_average as spatial_average
import numpy as np

class TestSpatialAverage:
    """
    
    calulcate global OF vec valid, empty
    linear_upsample valid, same hz, downsampled? (throw error)
    lienar_upsample_dataset valid, empty

    """
    
    def test_calculate_global_OF_vec_valid(self):
        vec1 = np.array([5, 2])
        vec2 = np.array([1, -1])
        vec3 = np.array([7, 7])
        vec4 = np.array([-2, -2])
        vec5 = np.array([100, -2])
        frame = [vec1, vec2, vec3, vec4, vec5]

        out = spatial_average.calculateGlobalOpticFlowVec(frame)

        # Below generated via manual calculation
        test = np.array([22.2, 0.8])
        assert np.array_equal(out, test)

    def test_calculate_global_OF_vec_empty(self):
        frame = []
        out = spatial_average.calculateGlobalOpticFlowVec(frame)
        
        test = np.array([0, 0])
        assert np.array_equal(out, test)

    def test_linear_upsample_valid(self):
        in_pt1 = np.array([0, 0])
        in_pt2 = np.array([3, 6])
        out = spatial_average.linear_upsample(50, 200, in_pt1, in_pt2)

        out_pt1 = np.array([0, 0])
        out_pt2 = np.array([1, 2])
        out_pt3 = np.array([2, 4])
        out_pt4 = np.array([3, 6])

        test = [out_pt1, out_pt2, out_pt3, out_pt4]
        assert np.array_equal(out, test)

    def test_linear_upsample_same_hz(self):
        in_pt1 = np.array([0, 0])
        in_pt2 = np.array([3, 6])
        out = spatial_average.linear_upsample(50, 50, in_pt1, in_pt2)

        out_pt1 = np.array([0, 0])
        out_pt2 = np.array([3, 6])

        test = [out_pt1, out_pt2]
        assert np.array_equal(out, test)


    def test_linear_upsample_downsample(self):
        in_pt1 = np.array([0, 0])
        in_pt2 = np.array([3, 6])

        with pytest.raises(ValueError) as e_info:
            spatial_average.linear_upsample(200, 50, in_pt1, in_pt2)
        assert str(e_info.value) == "Downsampling unsupported"


    def test_linear_upsample_dataset_valid(self):
        sample1 = np.array([0, 0])
        sample2 = np.array([3, 6])
        sample3 = np.array([6, 9])

        vec_list = [sample1, sample2, sample3]
        
        out = spatial_average.linear_upsample_dataset(50, 200, vec_list)
        
        i1 = np.array([0, 0])
        i2 = np.array([1, 2])
        i3 = np.array([2, 4])
        i4 = np.array([3, 6])
        i5 = np.array([4, 7])
        i6 = np.array([5, 8])
        i7 = np.array([6, 9])
        test = np.array([i1, i2, i3, i4, i5, i6, i7])

        assert np.array_equal(out, test)

    
    def test_linear_upsample_dataset_long(self):
        sample1 = np.array([0, 0])
        sample2 = np.array([3, 6])
        sample3 = np.array([6, 9])
        sample4 = np.array([0, 0])

        vec_list = [sample1, sample2, sample3, sample4]
        
        out = spatial_average.linear_upsample_dataset(50, 200, vec_list)
        
        i1 = np.array([0, 0])
        i2 = np.array([1, 2])
        i3 = np.array([2, 4])
        i4 = np.array([3, 6])
        i5 = np.array([4, 7])
        i6 = np.array([5, 8])
        i7 = np.array([6, 9])
        i8 = np.array([4, 6])
        i9 = np.array([2, 3])
        i10 = np.array([0, 0])
        test = np.array([i1, i2, i3, i4, i5, i6, i7, i8, i9, i10])

        assert np.array_equal(out, test)
    
    def test_linear_upsample_dataset_empty(self):
        with pytest.raises(ValueError) as excinfo:
            spatial_average.linear_upsample_dataset(50, 200, [])
        assert str(excinfo.value) == "Empty vec_list"
    