"""
.. module:: test_simple
  :synopsis: Test Simple
.. moduleauthor:: David Eriksson <dme65@cornell.edu>
"""

from src import *
from poap.controller import ThreadController, BasicWorkerThread
import numpy as np
import os.path


def main():
    if not os.path.exists("./logfiles"):
        os.makedirs("logfiles")
    if os.path.exists("./logfiles/test_simple.log"):
        os.remove("./logfiles/test_simple.log")
    logging.basicConfig(filename="./logfiles/test_simple.log",
                        level=logging.INFO)

    print("\nNumber of threads: 4")
    print("Maximum number of evaluations: 1000")
    print("Search strategy: CandidateDYCORS")
    print("Experimental design: Latin Hypercube")
    print("Ensemble surrogates: Cubic RBF, domain scaled to unit box")

    nthreads = 4
    maxeval = 1000
    nsamples = nthreads

    data = Ackley(dim=10)
    print(data.info)

    weights = np.array([0.1, 0.3, 0.5, 0.8, 0.95, 1.0])

    # Create a strategy and a controller
    controller = ThreadController()
    controller.strategy = \
        SyncStrategyNoConstraints(
            worker_id=0, data=data,
            maxeval=maxeval, nsamples=nsamples,
            exp_design=LatinHypercube(dim=data.dim, npts=2*(data.dim+1)),
            response_surface=RSUnitbox(RBFInterpolant(surftype=CubicRBFSurface, maxp=maxeval),data),
            sampling_method=CandidateDYCORS(data=data, numcand=100*data.dim, weights=weights))

    # Launch the threads and give them access to the objective function
    for _ in range(nthreads):
        worker = BasicWorkerThread(controller, data.objfunction)
        controller.launch_worker(worker)

    # Run the optimization strategy
    result = controller.run()

    print('Best value found: {0}'.format(result.value))
    print('Best solution found: {0}\n'.format(
        np.array_str(result.params[0], max_line_width=np.inf,
                     precision=5, suppress_small=True)))


if __name__ == '__main__':
    main()
