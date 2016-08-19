from subprocess import Popen, PIPE, STDOUT

tag_hippy_start = "[HIPPY-START]"
tag_hippy_line  = "[HIPPY-LINE]"
tag_hippy_end   = "[HIPPY-END]"


class ProcInfo(self): 
 def __init__():
  self.heap_start_address   = -1
  self.heap_end_address     = -1
  self.glibc_start_address  = -1
  self.glibc_end_address    = -1
  return


def parseProgramOut(output):
 for line in output:
  if tag_hippy_start in line:
   
   
 


if __name__ == '__main__':

 #cmd = 'LD_PRELOAD=./tracer.so ./trace_me'
 #p = Popen(cmd, shell=True, stderr=STDOUT, close_fds=True)
 #output = p.stdout.read() 
 with open("./traced_out_sample") as f:
  content = f.readlines()
 parsed_out = parseProgramOut(content)


