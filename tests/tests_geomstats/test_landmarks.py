"""Unit tests for landmarks space."""

import random

import geomstats.backend as gs
from geomstats.geometry.euclidean import Euclidean
from geomstats.geometry.hypersphere import Hypersphere
from geomstats.geometry.landmarks import L2Metric, Landmarks
from tests.conftest import TestCase
from tests.data_generation import ManifoldTestData, RiemannianMetricTestData
from tests.parametrizers import ManifoldParametrizer, RiemannianMetricParametrizer


class TestLandmarks(TestCase, metaclass=ManifoldParametrizer):
    space = Landmarks
    skip_test_random_point_belongs = True

    class TestDataLandmarks(ManifoldTestData):
        dim_list = random.sample(range(2, 4), 2)
        n_landmarks_list = random.sample(range(1, 5), 2)
        space_args_list = [
            (Hypersphere(dim), n_landmarks)
            for dim, n_landmarks in zip(dim_list, n_landmarks_list)
        ] + [
            (Euclidean(dim + 1), n_landmarks)
            for dim, n_landmarks in zip(dim_list, n_landmarks_list)
        ]
        shape_list = [
            (n_landmark, dim + 1) for dim, n_landmark in zip(dim_list, n_landmarks_list)
        ] * 2
        n_points_list = random.sample(range(1, 7), 4)
        n_samples_list = random.sample(range(1, 7), 4)
        n_vecs_list = random.sample(range(2, 5), 2)

        def random_point_belongs_data(self):
            smoke_space_args_list = [(Hypersphere(2), 2), (Euclidean(2 + 1), 2)]
            smoke_n_points_list = [1, 2]
            return self._random_point_belongs_data(
                smoke_space_args_list,
                smoke_n_points_list,
                self.space_args_list,
                self.n_points_list,
            )

        def projection_belongs_data(self):
            return self._projection_belongs_data(
                self.space_args_list, self.shape_list, self.n_samples_list
            )

        def to_tangent_is_tangent_data(self):
            return self._to_tangent_is_tangent_data(
                Landmarks,
                self.space_args_list,
                self.shape_list,
                self.n_vecs_list,
            )

    testing_data = TestDataLandmarks()


class TestL2Metric(TestCase, metaclass=RiemannianMetricParametrizer):
    metric = connection = L2Metric
    skip_test_parallel_transport_ivp_is_isometry = True
    skip_test_parallel_transport_bvp_is_isometry = True
    skip_test_exp_geodesic_ivp = True
    skip_test_exp_belongs = True
    skip_test_exp_shape = True
    skip_test_log_shape = True

    class TestDataL2Metric(RiemannianMetricTestData):

        dim_list = random.sample(range(2, 4), 2)
        n_landmarks_list = random.sample(range(2, 5), 2)
        metric_args_list = [
            (Hypersphere(dim), n_landmarks)
            for dim, n_landmarks in zip(dim_list, n_landmarks_list)
        ] + [
            (Euclidean(dim + 1), n_landmarks)
            for dim, n_landmarks in zip(dim_list, n_landmarks_list)
        ]
        space_list = [Landmarks(*metric_arg) for metric_arg in metric_args_list]
        shape_list = [
            (n_landmark, dim + 1) for dim, n_landmark in zip(dim_list, n_landmarks_list)
        ] * 2
        n_points_list = random.sample(range(2, 5), 2)
        n_samples_list = random.sample(range(2, 5), 2)
        n_points_a_list = random.sample(range(2, 5), 2)
        n_points_b_list = [1]
        batch_size_list = random.sample(range(2, 5), 2)
        alpha_list = [1] * 4
        n_rungs_list = [1] * 4
        scheme_list = ["pole"] * 4

        def exp_shape_data(self):
            return self._exp_shape_data(
                self.metric_args_list,
                self.space_list,
                self.shape_list,
                self.batch_size_list,
            )

        def log_shape_data(self):
            return self._log_shape_data(
                self.metric_args_list,
                self.space_list,
                self.batch_size_list,
            )

        def squared_dist_is_symmetric_data(self):
            return self._squared_dist_is_symmetric_data(
                self.metric_args_list,
                self.space_list,
                self.n_points_a_list,
                self.n_points_b_list,
                atol=gs.atol * 1000,
            )

        def exp_belongs_data(self):
            return self._exp_belongs_data(
                self.metric_args_list,
                self.space_list,
                self.shape_list,
                self.n_samples_list,
                belongs_atol=gs.atol * 10000,
            )

        def log_is_tangent_data(self):
            return self._log_is_tangent_data(
                self.metric_args_list,
                self.space_list,
                self.n_samples_list,
                is_tangent_atol=gs.atol * 1000,
            )

        def geodesic_ivp_belongs_data(self):
            return self._geodesic_ivp_belongs_data(
                self.metric_args_list,
                self.space_list,
                self.shape_list,
                self.n_points_list,
                belongs_atol=gs.atol * 1000,
            )

        def geodesic_bvp_belongs_data(self):
            return self._geodesic_bvp_belongs_data(
                self.metric_args_list,
                self.space_list,
                self.n_points_list,
                belongs_atol=gs.atol * 100,
            )

        def log_exp_composition_data(self):
            return self._log_exp_composition_data(
                self.metric_args_list,
                self.space_list,
                self.n_samples_list,
                rtol=gs.rtol * 1000,
                atol=gs.atol * 1000,
            )

        def exp_log_composition_data(self):
            return self._exp_log_composition_data(
                self.metric_args_list,
                self.space_list,
                self.shape_list,
                self.n_samples_list,
                rtol=gs.rtol * 10000,
                atol=gs.atol * 10000,
            )

        def exp_ladder_parallel_transport_data(self):
            return self._exp_ladder_parallel_transport_data(
                self.metric_args_list,
                self.space_list,
                self.shape_list,
                self.n_samples_list,
                self.n_rungs_list,
                self.alpha_list,
                self.scheme_list,
            )

        def exp_geodesic_ivp_data(self):
            return self._exp_geodesic_ivp_data(
                self.metric_args_list,
                self.space_list,
                self.shape_list,
                self.n_samples_list,
                self.n_points_list,
                rtol=gs.rtol * 10000,
                atol=gs.atol * 10000,
            )

        def parallel_transport_ivp_is_isometry_data(self):
            return self._parallel_transport_ivp_is_isometry_data(
                self.metric_args_list,
                self.space_list,
                self.shape_list,
                self.n_samples_list,
                is_tangent_atol=gs.atol * 1000,
                atol=gs.atol * 100,
            )

        def parallel_transport_bvp_is_isometry_data(self):
            return self._parallel_transport_bvp_is_isometry_data(
                self.metric_args_list,
                self.space_list,
                self.shape_list,
                self.n_samples_list,
                is_tangent_atol=gs.atol * 100,
                atol=gs.atol * 100,
            )

        def l2_metric_inner_product_vectorization_data(self):
            smoke_data =[]
            return self.generate_tests(smoke_data)

        def l2_metric_exp_vectorization_data(self):
            smoke_data=[]
            return self.generate_tests(smoke_data)

        def l2_metric_log_vectorization_data(self):
            smoke_data=[]
            return self.generate_tests(smoke_data)
            

    testing_data = TestDataL2Metric()


    @geomstats.tests.np_autograd_and_tf_only
    def test_l2_metric_inner_product_vectorization(self, l2_metric_s2):
        """Test the vectorization inner_product."""
        n_samples = self.n_landmark_sets
        landmarks_ab = l2_metric_s2.geodesic(self.landmarks_a, self.landmarks_b)
        landmarks_bc = l2_metric_s2.geodesic(self.landmarks_b, self.landmarks_c)
        landmarks_ab = landmarks_ab(self.times)
        landmarks_bc = landmarks_bc(self.times)

        tangent_vecs = l2_metric_s2.log(
            point=landmarks_bc, base_point=landmarks_ab
        )

        result = l2_metric_s2.inner_product(
            tangent_vecs, tangent_vecs, landmarks_ab
        )

        self.assertAllClose(gs.shape(result), (n_samples,))

    @geomstats.tests.np_autograd_and_tf_only
    def test_l2_metric_exp_vectorization(self, l2_metric_s2):
        """Test the vectorization of exp."""
        landmarks_ab = l2_metric_s2.geodesic(self.landmarks_a, self.landmarks_b)
        landmarks_bc = l2_metric_s2.geodesic(self.landmarks_b, self.landmarks_c)
        landmarks_ab = landmarks_ab(self.times)
        landmarks_bc = landmarks_bc(self.times)

        tangent_vecs = l2_metric_s2.log(
            point=landmarks_bc, base_point=landmarks_ab
        )

        result = self.l2_metric_s2.exp(
            tangent_vec=tangent_vecs, base_point=landmarks_ab
        )
        self.assertAllClose(gs.shape(result), gs.shape(landmarks_ab))

    @geomstats.tests.np_autograd_and_tf_only
    def test_l2_metric_log_vectorization(self, l2_metric_s2):
        """Test the vectorization of log."""
        landmarks_ab = l2_metric_s2.geodesic(self.landmarks_a, self.landmarks_b)
        landmarks_bc = l2_metric_s2.geodesic(self.landmarks_b, self.landmarks_c)
        landmarks_ab = landmarks_ab(self.times)
        landmarks_bc = landmarks_bc(self.times)

        tangent_vecs = l2_metric_s2.log(
            point=landmarks_bc, base_point=landmarks_ab
        )

        result = tangent_vecs
        self.assertAllClose(gs.shape(result), gs.shape(landmarks_ab))

    @geomstats.tests.np_autograd_and_tf_only
    def test_l2_metric_geodesic(self, l2_metric_s2):
        """Test the geodesic method of L2Metric."""
        landmarks_ab = l2_metric_s2.geodesic(self.landmarks_a, self.landmarks_b)
        landmarks_ab = landmarks_ab(self.times)

        result = landmarks_ab
        expected = []
        for k in range(self.n_sampling_points):
            geod = l2_metric_s2.ambient_metric.geodesic(
                initial_point=self.landmarks_a[k, :], end_point=self.landmarks_b[k, :]
            )
            expected.append(geod(self.times))
        expected = gs.stack(expected, axis=1)

        self.assertAllClose(result, expected)


