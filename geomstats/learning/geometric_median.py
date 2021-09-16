"""Geometric Median Estimation"""

import geomstats.backend as gs

class WeiszfeldAlgorithm:
    
    r"""Weiszfeld Algorithm for Manifolds.

    Parameters
    ----------
    metric : RiemannianMetric
        Riemannian metric.
    weights : array-like, [N]
        weights for weighted sum
        Optional, default : None.
            If None equal weights (1/N) are used for all points
    max_iter : int
        Maximum number of iterations for the algorithm.
        Optional, default: 100.
    lr : float
        Learning rate to be used for the algorithm
        Optional, default : 1.0
    init : array-like,
        initialization to be used in the start
        Optional, default : None
    print_every : int
        Print updated median after print_every iterations
        Optional, default : None

    References
    ----------
    .. [BJL2008]_ Bhatia, Jain, Lim. "Robust statstics on 
    Riemannian manifolds via the geometric median"
    """

    def __init__(self, metric,
                 max_iter=100,
                 lr=1.,
                 init=None,
                 print_every=None):

        self.metric = metric
        self.max_iter = max_iter
        self.lr = lr
        self.init = init
        self.print_every = print_every
        self.estimate_ = None
   
    def single_iteration(self, current_median, X, weights, lr):
        """Peforms single iteration of Weiszfeld Algorithm

        Parameters
        ---------
        current_median : array-like, shape={representation shape}
            current median
        X : array-like, shape=[..., {representation shape}]
            data for which geometric has to be found
        weights : array-like, shape=[N]
            weights for weighted sum     
        lr : float
            learning rate for the current iteration

        Returns
        -------
        updated_median: array-like, shape={representation shape}
            updated median after single iteration 
        """

        dists = self.metric.dist(current_median, X)
        sum = gs.sum(dists)
        if sum==0.0:
          return current_median
       
        logs = self.metric.log(X, current_median)
        mul = gs.divide(weights, dists)
        v_k = gs.sum(mul[:, None, None] * logs, axis=0) / gs.sum(mul) 
        updated_median = self.metric.exp(lr * v_k, current_median)
        return updated_median

    def fit(self, X, weights=None):
        """Compute the Geometric Median.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape=[..., {dim, [n, n]}]
            Training input samples.
        weights : array-like, shape=[...,]
            Weights associated to the points.
            Optional, default: None, in which case 
            it is equally weighted

        Returns
        -------
        self : object
            Returns self.
        """

        n_points = X.shape[0]
        current_median = X[0] if self.init is None else self.init
        if weights is None:
            weights = gs.ones((n_points,))/n_points 
        for iter in range(1,self.max_iter+1):
            current_median = self.single_iteration(
                current_median, X, weights, self.lr)
            if self.verbose is not None and (iter+1)%self.print_every == 0:
               print("iteration: {} curr_median: {}".format(iter, current_median))  
        self.estimate_ = current_median

        return self

