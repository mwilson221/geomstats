import logging
import random

import geomstats.backend as gs
from geomstats.learning._sklearn_wrapper import WrappedLinearRegression, WrappedPCA
from geomstats.learning.frechet_mean import FrechetMean

# TODO: create AAC and control flow with __new__


def _warn_max_iterations(iteration, max_iter):
    if iteration == max_iter:
        logging.warning(
            f"Maximum number of iterations {max_iter} reached. "
            "The estimate may be inaccurate"
        )


class AACFrechet:
    def __init__(
        self,
        metric,
        *,
        epsilon=1e-6,
        max_iter=20,
        init_point=None,
        mean_estimator_kwargs=None,
    ):
        self.metric = metric
        self.epsilon = epsilon
        self.max_iter = max_iter
        self.init_point = init_point

        mean_estimator_kwargs = mean_estimator_kwargs or {}
        self.mean_estimator = FrechetMean(
            self.metric.total_space_metric, **mean_estimator_kwargs
        )

        self.estimate_ = None
        self.n_iter_ = None

    def fit(self, X):
        previous_estimate = (
            random.choice(X) if self.init_point is None else self.init_point
        )
        aligned_X = X
        error = self.epsilon + 1
        iteration = 0
        while error > self.epsilon and iteration < self.max_iter:
            iteration += 1

            aligned_X = self.metric.align_point_to_point(previous_estimate, aligned_X)
            new_estimate = self.mean_estimator.fit(aligned_X).estimate_
            error = self.metric.total_space_metric.dist(previous_estimate, new_estimate)

            previous_estimate = new_estimate

        _warn_max_iterations(iteration, self.max_iter)

        self.estimate_ = new_estimate
        self.n_iter_ = iteration

        return self


class AACGPC:
    def __init__(
        self, metric, *, n_components=2, epsilon=1e-6, max_iter=20, init_point=None
    ):
        self.metric = metric
        self.epsilon = epsilon
        self.max_iter = max_iter
        self.init_point = init_point

        self.pca_solver = WrappedPCA(n_components=n_components)

    @property
    def components_(self):
        return self.pca_solver.reshaped_components_

    @property
    def explained_variance_(self):
        return self.pca_solver.explained_variance_

    @property
    def explained_variance_ratio_(self):
        return self.pca_solver.explained_variance_ratio_

    @property
    def singular_values_(self):
        return self.pca_solver.singular_values_

    @property
    def mean_(self):
        return self.pca_solver.reshaped_mean_

    def fit(self, X, y=None):
        x = random.choice(X) if self.init_point is None else self.init_point
        aligned_X = self.metric.align_point_to_point(x, X)

        self.pca_solver.fit(aligned_X)
        previous_expl = self.pca_solver.explained_variance_ratio_[0]

        error = self.epsilon + 1
        iteration = 0
        while error > self.epsilon and iteration < self.max_iter:
            iteration += 1
            mean = self.pca_solver.reshaped_mean_
            direc = self.pca_solver.reshaped_components_[0]

            geodesic = self.metric.total_space_metric.geodesic(
                initial_point=mean, initial_tangent_vec=direc
            )

            aligned_X = self.metric.align_point_to_geodesic(geodesic, aligned_X)
            self.pca_solver.fit(aligned_X)
            expl_ = self.pca_solver.explained_variance_ratio_[0]

            error = expl_ - previous_expl
            previous_expl = expl_

        _warn_max_iterations(iteration, self.max_iter)

        return self


class AACRegression:
    def __init__(
        self, metric, *, epsilon=1e-6, max_iter=20, init_point=None, model_kwargs=None
    ):
        self.metric = metric
        self.epsilon = epsilon
        self.max_iter = max_iter
        self.init_point = init_point

        # TODO: set regressor?
        model_kwargs = model_kwargs or {}
        self.regressor = WrappedLinearRegression(**model_kwargs)

    def fit(self, X, y):
        y_ = random.choice(y) if self.init_point is None else self.init_point
        aligned_y = self.metric.align_point_to_point(y_, y)

        self.regressor.fit(X, aligned_y)
        previous_y_pred = self.regressor.predict(X)

        error = self.epsilon + 1
        iteration = 0
        while error > self.epsilon and iteration < self.max_iter:
            iteration += 1
            aligned_y = self.metric.align_point_to_point(previous_y_pred, aligned_y)

            self.regressor.fit(X, aligned_y)
            y_pred = self.regressor.predict(X)

            # TODO: squared distances?
            error = gs.sum(self.metric.dist(previous_y_pred, y_pred))

            previous_y_pred = y_pred

        _warn_max_iterations(iteration, self.max_iter)

        return self

    def predict(self, X):
        return self.regressor.predict(X)
