
# http://divtable.com/generator/

from subprocess import Popen, PIPE, STDOUT

cmd = 'LD_PRELOAD=./tracer.so ./trace_me32'
p = Popen(cmd, shell=True, stderr=PIPE, close_fds=True)

output = p.stderr.read()

# now we have to parse output in order to retreive our output and not the one of the program
# on stderr.
print "\n\n--------------------"
print "----HIPPY REPORT----"
print "--------------------\n"

print output
