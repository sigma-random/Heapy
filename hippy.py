from subprocess import Popen, PIPE, STDOUT
import json
import platform

tag_hippy_start = "<hippy-d75d6fc7>"
tag_hippy_end   = "</hippy-d75d6fc7>"

api_call_json = []
proc_info_json = None

operations = { 'free': free, 'malloc': malloc, 'calloc': calloc, 'realloc': realloc }
procInfo = None
timeline = [State()] # a timeline is a list of State

class ProcInfo:
 def __init__(self,hstart,hend,libcstart,libcend,binaryarch):
  self.architecture         = binaryarch  # binary is 32 or 64 bit?
  self.heap_start_address   = hstart
  self.heap_end_address     = hend
  self.glibc_start_address  = libcstart
  self.glibc_end_address    = libcend
  return

 def getArchMutiplier():
     if "x86_64" in self.architecture:
         return 2
     else:
         return 1

'''
 This is a list of chunks currently allocated in a State
'''
class State(list):
 def __init__():
  self.errors = []
  self.info = []
  self.dump_id = -1 # this in order to correlate a State with a taken dump
  super().__init__(*args, **kwargs)
  return

 def getChunkAt(address):
     for i,chunk in enumerate(self):
         if chunk.addr == address:
            return i
     return -1 # well, chunk not found in the state


class Chunk():
 def __init__(self, addr, size, raw_size):
     self.addr = addr # start address of user data for this chunk
     self.raw_addr = hex(int(addr,16) - procInfo.getArchMutiplier() * 8)  # this is the real start address of the chunk
     self.size     = size     # size of the chunk as requested from the user
     self.raw_size = raw_size # raw size of the chunk ( the size returned from usable_size() )
     self.type     = getChunkType(raw_size)

 def getChunkType(raw_size):
     raw_size = int(raw_size,10)
     if raw_size >= 8 and raw_size <= 80:
         return "fast_chunk"
     if raw_size > 80 and raw_size < 512:
         return "small chunk"
     if raw_size >= 512:
         return "large chunk"
     return ""

def parseProgramOut(output):
 print_next_line = 0
 for line in output:
     if print_next_line == 1:
         dumped_json = json.loads(line)
         if dumped_json['type'] == "apicall":
             api_call_json.append(dumped_json)  # append this mini-json in the apicall list
         if dumped_json['type'] == "procinfo":
             proc_info_json = dumped_json
         print_next_line = 0
     if tag_hippy_start in line:
         print_next_line = 1

def malloc(state,api_args,api_info,api_ret):
    chunk = Chunk(api_ret,api_args['size'],api_info['usable_chunk_size'])
    state.append(chunk)

def free(state,api_args,api_info,api_ret):
    freed_address = api_args['address']
    if freed_address == "0":
        return
    else:
        index,res = state.getChunkAt(freed_address)
        del state[index] # remove the chunk from the State!

def calloc(state,api_args,api_info,api_ret):
    api_args['user_size'] = str(int(api_args['nmemb'],10) * int(api_args['membsize'],10))
    malloc(state,api_args,api_info,api_ret)

def realloc(state,api_args,api_info,api_ret):
    address_to_realloc = api_args['address']
    newsize = api_args['size']

    if address_to_realloc == "0":
        malloc(state,api_args,api_info,api_ret):
    elif newsize == "0":
        free(state,api_args,None,None):
    else:
        index,res = state.getChunkAt(address_to_realloc) # let's search the chunk that has been reallocated
        if api_ret == address_to_realloc:
            state(index) = Chunk(api_ret,api_args['size'],api_info['usable_chunk_size'])
        else:
            new_api_args = {}
            new_api_args['address'] = api_info['internal_api_call']['api_args']['address']
            free(state,new_api_args,None,None)
            timeline.append(state) # keep track of this free performed by the realloc
            malloc(state,api_args,api_info,api_ret):

def buildTimeline():
    for djson in api_call_json:
        api_name = djson['api_name']
        api_args = djson['api_args']
        api_info = djson.get('api_info',[])
        api_ret  = djson['api_return']
        op = operations(api_name)
        state = timeline[-1]
        op(state,api_args,api_info,api_ret)
        timeline.append(state)

'''
 Retrieve information about the process
 from the json and build the ProcInfo object
'''
def buildProcInfo():
    if proc_info_json.get('heap_range',[]) != []:
        heap_start_address  = djson['heap_start_address']
        heap_end_address    = djson['heap_end_address']
    #if proc_info_json.get('glibc_range',[]) != []:
    #    glibc_start_address = djson['glibc_start_address']
    #    glibc_end_address   = djson['glibc_end_address']
    arch = proc_info_json['arch']
    return procinfo(heap_start_address,heap_end_address,"","",arch)


if __name__ == '__main__':

 '''
 cmd = 'LD_PRELOAD=./tracer.so ./trace_me32'
 p = Popen(cmd, shell=True, stderr=PIPE, close_fds=True)
 output = p.stderr.read()
 print output
 '''
 with open("./traced_out_sample") as f:
  content = f.readlines()
 parseProgramOut(content)
 procInfo = buildProcInfo()
 buildTimeline()
 print timeline
