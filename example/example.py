from cluster_helper.cluster import cluster_view
import argparse
import time
import imp

from IPython.parallel import require


def long_computation(x, y, z):
    import time
    import socket
    time.sleep(1)
    return (socket.gethostname(), x + y + z)

@require("cluster_helper")
def require_test(x):
    return True

def context_test(x):
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="example script for doing parallel "
                                     "work with IPython.")
    parser.add_argument("--scheduler", dest='scheduler', required=True,
                        help="scheduler to use (lsf, sge, torque, slurm, or pbs)")
    parser.add_argument("--queue", dest='queue', required=True,
                        help="queue to use on scheduler.")
    parser.add_argument("--num_jobs", dest='num_jobs', required=True,
                        type=int, help="number of jobs to run in parallel.")
    parser.add_argument("--cores_per_job", dest="cores_per_job", default=1,
                        type=int, help="number of cores for each job.")
    parser.add_argument("--profile", dest="profile", default=None,
                        help="Optional profile to test.")
    parser.add_argument("--resources", dest="resources", default=None,
                        help="Native specification flags to the scheduler")
    parser.add_argument("--timeout", dest="timeout", default=15,
                        help="Time (in minutes) to wait before timing out.")
    parser.add_argument("--memory", dest="mem", default=1,
                        help="Memory in GB to reserve.")

    args = parser.parse_args()
    args.resources = {'resources': args.resources,
                      'mem': args.mem}

    with cluster_view(args.scheduler, args.queue, args.num_jobs,
                      cores_per_job=args.cores_per_job,
                      start_wait=args.timeout,
                      profile=args.profile, extra_params=args.resources) as view:
        print "First check to see if we can talk to the engines."
        results = view.map(lambda x: "hello world!", range(5))
        print ("This long computation that waits for 5 seconds before returning "
               "takes a while to run serially..")
        start_time = time.time()
        results = map(long_computation, range(20), range(20, 40), range(40, 60))
        print results
        print "That took {0} seconds.".format(time.time() - start_time)

        print "Running it in parallel goes much faster..."
        start_time = time.time()
        results = view.map(long_computation, range(20), range(20, 40), range(40, 60))
        print results
        print "That took {0} seconds.".format(time.time() - start_time)

        try:
            imp.find_module('dill')
            found = True
        except ImportError:
            found=False

        if False:
            def make_closure(a):
                """make a function with a closure, and return it"""
                def has_closure(b):
                    return a * b
                return has_closure
            closure = make_closure(5)
            print "With dill installed, we can pickle closures without an error!"
            print closure
            print view.map(closure, [3])



            with open("test", "w") as test_handle:
                print "Does context break it?"
                print view.map(context_test, [3])

                print "Does context break it with a closure?"
                print view.map(closure, [3])

            print "But wrapping functions with @reqiure is broken."
            print view.map(require_test, [3])
