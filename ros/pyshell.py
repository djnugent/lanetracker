import subprocess
import time
import os


processes = []

@classmethod
def sys_call(cmd,wait=True):
    p = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if wait:
        p.wait()
        out,error = p.communicate()
        return out.decode("utf-8"), error.decode("utf-8"), cmd
    else:
        processes.append(p)
@staticmethod
def kill_all():
    for p in processes:
        # Get the process id & try to terminate it gracefuly
        pid = p.pid
        p.terminate()

        # Check if the process has really terminated & force kill if not.
        try:
            os.kill(pid, 0)
            p.kill()
            print "Forced kill"
        except OSError, e:
            print "Terminated gracefully"
            p.kill()
