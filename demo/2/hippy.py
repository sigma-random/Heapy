from subprocess import Popen, PIPE, STDOUT
import json
import copy
import sys
import random
import os
from hippy_gui_manager import HippyGuiManager
from shutil import copyfile

import pdb

tag_hippy_start = "<hippy-d75d6fc7>"
tag_hippy_end   = "</hippy-d75d6fc7>"
dump_name       = "heap_dump_"
libc_dump_name  = "libc_dump_"
libc_dump_path  = "./LibcDumps/"
gui_path        = "/home/degrigis/Project/Hippy/gui/base2.html"

api_call_json = []
proc_info_json = None


class ProcInfo():
 def __init__(self,hstart,hend,libcversion,libcstart,libcend,binaryarch):
  self.architecture         = binaryarch  # binary is 32 or 64 bit?
  self.heap_start_address   = hstart
  self.heap_end_address     = hend
  self.libc_version         = libcversion
  self.libc_start_address   = libcstart
  self.libc_end_address     = libcend
  return

 def getArchMutiplier(self):
     if self.architecture == "64":
         return 2
     else:
         return 1

 def __str__(self):
     repr = "********ProcInfo********\n" + "[+]arch: " + self.architecture + "\n[+]heap_range: " + self.heap_start_address + "-" + self.heap_end_address + "\n[+]libc_version: " + self.libc_version + "\n[+]libc_range: " + self.libc_start_address + "-" + self.libc_end_address + "\n"
     return repr
'''
 This is a list of chunks currently allocated in a State
'''
class State(list):

 def __init__(self):
  self.errors = []
  self.api_now = ""
  self.info = []
  self.fastchunks_bit = 1 # this bit is used internally by ptmalloc in order to understand if there are fastbin freed in memory
  self.dump_name = "" # this in order to correlate a State with a taken dump
  self.libc_dump_name = ""
  self.color = []
  self.last_heap_address = "0" # the highest address reached by the heap
  return

 def getChunkAt(self,address):
     for i,chunk in enumerate(self):
         if chunk.addr == address:
            return i,chunk
     return -1,None # well, chunk not found in the state

 def getChunkAtRawAddress(self,raw_address):
     for i,chunk in enumerate(self):
         if chunk.raw_addr == raw_address:
            return i,chunk
     return -1,None # well, again, chunk not found

 def __str__(self):
     repr = "********State********\n" + "[+]info: " + self.api_now + "\n[+]dump_name: " + self.dump_name + "\n[+]libc_dump_name: " + self.libc_dump_name + "\n"
     for chunk in self:
         repr+=chunk.__str__()
     repr+= "*********************\n"
     return repr


####################################################################################
#                                     chunk                                        #
####################################################################################
#
#                                full_chunk_size
# |--------------------------------------------------------------------------------|
# |
# |                                 raw_size ( returned from malloc)
# |                     |----------------------------------------------------------|
# |
#                       size ( requested by user )
# |                     |--------------------|
# ----------------------------------------------------------------------------------
# | size | N | M | PREV |           user_data         |   prev_size OR data        |
# ----------------------------------------------------------------------------------
# ^                     ^                                                          ^
# raw_addr             addr                                                   chunk_end_addr
#
class Chunk():
 def __init__(self, addr, size, raw_size,color, status ="allocated"):
     self.addr = addr # start address of user data for this chunk
     self.raw_addr = hex(int(addr,16) - procInfo.getArchMutiplier() * 4)  # this is the real start address of the chunk
     self.size     = size     # size of the chunk as requested from the user
     self.raw_size = raw_size # raw size of the chunk ( the size returned from usable_size() )
     self.full_chunk_size = str(int(raw_size,10) + procInfo.getArchMutiplier() * 4)
     self.chunk_end_addr = hex((int(self.raw_addr,16) + int(self.full_chunk_size,10)))
     self.type     = self.getChunkType(raw_size)
     self.status = status
     self.color = color

 def getChunkType(self,raw_size):
     raw_size = int(raw_size,10)
     arch_multiplier = procInfo.getArchMutiplier()

     # From libc code:
     #
     # define SIZE_SZ 8
     # define MALLOC_ALIGNMENT SIZE_SZ * 2
     # define NBINS             128
     # define NSMALLBINS         64
     # define SMALLBIN_WIDTH    MALLOC_ALIGNMENT
     # define SMALLBIN_CORRECTION (MALLOC_ALIGNMENT > 2 * SIZE_SZ)
     # define MIN_LARGE_SIZE    ((NSMALLBINS - SMALLBIN_CORRECTION) * SMALLBIN_WIDTH)
     size_sz = 4 * arch_multiplier
     malloc_alignment = 2 * 4 * arch_multiplier
     nsmallbins = 64
     smallbin_correction = malloc_alignment

     max_fast = (80 * size_sz / 4)
     max_small = 512 * arch_multiplier
     min_large = max_small

     if raw_size >= 8 and raw_size <= max_fast:  #https://github.com/sploitfun/lsploits/blob/master/glibc/malloc/malloc.c#L1600
         return "fast_chunk"
     if raw_size > max_fast and raw_size <= max_small:
         return "small chunk"
     if raw_size > min_large:
         return "large chunk"
     return ""

 def __str__(self):
     return "------CHUNK------\n[+]status: " + self.status + "\n[+]addr: " + self.addr + "\n[+]raw_addr: " + self.raw_addr +"\n[+]size: " + self.size + "\n[+]raw_size: " + self.raw_size + "\n[+]full_chunk_size: " + self.full_chunk_size + "\n[+]chunk_end_addr: " + self.chunk_end_addr + "\n[+]type: " + self.type + "\n" + "[+]color: " + str(self.color) +  "\n-----------------\n"


def parseProgramOut(output):
 print_next_line = 0
 for line in output:
     if print_next_line == 1:
         dumped_json = json.loads(line)
         if dumped_json['type'] == "apicall":
             api_call_json.append(dumped_json)  # append this mini-json in the apicall list
         if dumped_json['type'] == "procinfo":
             global proc_info_json
             proc_info_json = dumped_json
         print_next_line = 0
     if tag_hippy_start in line:
         print_next_line = 1

def malloc(state,api_args,api_info,api_ret,api_counter):

    if int(api_ret,16) > int(state.last_heap_address,16):
        state.last_heap_address = hex(int(api_ret,16) + int(api_info['usable_chunk_size'],10) + 0x200) # save the address of the allocated chunk if it is higher than the last saved one

    index,res = state.getChunkAt(str(api_ret)) # if something returns from this function we are allocating in a previous freed chunk

    if index != -1: # if true, we are reusing a previously freed chunk!
        prev_freed_chunk = state[index]

        usable_size = api_info['usable_chunk_size']


        if int(usable_size,10) < int(prev_freed_chunk.raw_size,10): # we have allocated a chunk in a bigger freed chunk ( we have a remainder ), let's update the chunk and create the reminder
            # calculate the remainder
            remainder_size = str(int(prev_freed_chunk.raw_size,10) - int(usable_size,10) - 8)
            remainder_addr = hex(int(api_ret,16) + int(usable_size,10) + procInfo.getArchMutiplier() * 4)
            black_color = ('0','0','0')
            chunk = Chunk(remainder_addr,remainder_size,remainder_size,black_color,"free")
            state.append(chunk)

        # let's update the reused chunk!
        prev_freed_chunk.size = api_args['size']
        prev_freed_chunk.raw_size = usable_size
        prev_freed_chunk.full_chunk_size = str(int(prev_freed_chunk.raw_size,10) + procInfo.getArchMutiplier() * 4)
        prev_freed_chunk.chunk_end_addr = hex((int(prev_freed_chunk.raw_addr,16) + int(prev_freed_chunk.full_chunk_size,10)))
        prev_freed_chunk.status = "allocated"
        prev_freed_chunk.type = prev_freed_chunk.getChunkType(usable_size)
        prev_freed_chunk.color = random_color() # since this is a new chunk let's pick another color


    else:
        chunk = Chunk(api_ret,api_args['size'],api_info['usable_chunk_size'],random_color())
        state.append(chunk)

    if state.api_now == "":
        state.api_now = "malloc(" + api_args['size'] + ") = " + api_ret  # keep track of the api called in this state
    if state.dump_name == "":
        state.dump_name = dump_name + api_counter
    if state.libc_dump_name == "":
        state.libc_dump_name = libc_dump_name + api_counter


def free(state,api_args,api_info,api_ret,api_counter):
    freed_address = api_args['address']
    if freed_address == "0":
        return
    else:
        index,res = state.getChunkAt(freed_address)
        if index != -1 and len(state) == 1 and state[index].type != "fast_chunk": # there is only one chunk in the state and we are freeing it, coalescing with the top chunk ( if it is not a fastchunk! )
            del state[index]
        else:
            state[index].status = "free" # change the status of the chunk
            state[index].color = ('0','0','0')
            if state[index].type == "fast_chunk": # if we are freeing a fast_chunk
                state.fastchunks_bit = 0 # following ptmalloc whenever a fastbin is released the fastchunks_bit is cleared, now if it will be resetted to 1 it means that a call to malloc_consolidate has been done.

        if state.api_now == "":
            state.api_now = "free(" + freed_address + ")"
        if state.dump_name == "":
            state.dump_name = dump_name + api_counter
        if state.libc_dump_name == "":
            state.libc_dump_name = libc_dump_name + api_counter

def calloc(state,api_args,api_info,api_ret,api_counter):
    api_args['size'] = str(int(api_args['nmemb'],10) * int(api_args['membsize'],10))
    state.api_now = "calloc(" + api_args['nmemb'] + "," + api_args['membsize'] + ") = " + api_ret
    if state.dump_name == "":
        state.dump_name = dump_name + api_counter
    if state.libc_dump_name == "":
        state.libc_dump_name = libc_dump_name + api_counter
    malloc(state,api_args,api_info,api_ret,None)

def realloc(state,api_args,api_info,api_ret,api_counter):
    address_to_realloc = api_args['address']
    newsize = api_args['size']

    if address_to_realloc == "0":
        malloc(state,api_args,api_info,api_ret)
    elif newsize == "0":
        free(state,api_args,None,None,None)
    else:
        index,res = state.getChunkAt(address_to_realloc) # let's search the chunk that has been reallocated
        if api_ret == address_to_realloc:
            state[index] = Chunk(api_ret,api_args['size'],api_info['usable_chunk_size'],random_color())
            state.api_now = "realloc(" + address_to_realloc + "," + newsize + ") = " + api_ret
            state.dump_name = dump_name + api_counter
            state.libc_dump_name = libc_dump_name + api_counter
        else:
            new_api_args = {}
            new_api_args['address'] = api_info['internal_api_call']['api_args']['address']
            state.api_now = "realloc(" + address_to_realloc + "," + newsize + ") = " + api_ret
            state.dump_name = dump_name + api_counter
            state.libc_dump_name = libc_dump_name + api_counter
            free(state,new_api_args,None,None,None)
            malloc(state,api_args,api_info,api_ret,None)

def sort(state):
    state = state.sort(key=lambda chunk: chunk.raw_addr)


# for example in the libc 2.19 the information about flags are at the line 34 of the libc_dump file.
# in another libc version it could be in another position.
supported_libc = {"2.19-32" : 34 ,  "2.19-64" : 60, "2.23-32": 61 ,  "2.23-64": 90 }

# This function check the bit FASTCHUNKS_BIT in order to discover if it has been resetted to 1
# and so if malloc_consolidate has been called
def check_malloc_consolidate(libc_dump_name):
    f = open(libc_dump_path + libc_dump_name)
    libc_version = procInfo.libc_version
    arch = procInfo.architecture
    fastbin_bit_line = supported_libc.get(libc_version+"-"+arch,0)

    if fastbin_bit_line == 0:
        print "[ERROR] Libc not supported"
        sys.exit(0)

    line_cont = 1
    for line in f.readlines():
        if line_cont == fastbin_bit_line:
            flags_dword = line.split(" ")[2] # the second dword contains the flag we need
            if flags_dword[7] == '1':
                return True
            else:
                return False
        line_cont += 1



# coalesc together all the chunks that are not fastchunks
def coalesc(state,consolidate):
    tocoalesc = []
    for i,chunk in enumerate(state):
        if chunk.status == "allocated" or ( chunk.type == "fast_chunk" and consolidate == False ): # stop collecting address to coalesc in this cases
            if len(tocoalesc) == 0: # in this case we have a series of allocated chunk
                tocoalesc = []
                continue
            if len(tocoalesc) == 1: # in this case we have an isolated free chunk that we can't coalesc...
                tocoalesc = []
                continue
            if len(tocoalesc) > 1: # we have some chunks to coalesc!
                # now let's pop the chunk that will coalesc the others
                first_index = tocoalesc[0] # let's extract the index of the first chunk
                first_chunk = state[tocoalesc[0]] # and the chunk too
                new_size = int(first_chunk.size,10)
                new_raw_size = int(first_chunk.raw_size,10)
                tocoalesc.pop(0)

                for c_index in tocoalesc:
                    chunk_to_merge = state[c_index]
                    new_size += int(chunk_to_merge.size,10)
                    new_raw_size += int(chunk_to_merge.raw_size,10)

                # finish to coalesc, let's remove the coalesced chunks and
                # substitute the first_chunk with the coalesced one

                for index in sorted(tocoalesc, reverse=True):
                    del state[index]

                state[first_index] = Chunk(first_chunk.addr,str(new_size),str(new_raw_size),('0','0','0'),"free")
                tocoalesc = [] # clean the tocoalesc

        if chunk.status == "free": # we are considering only free chunks that are not fast_chunks
            tocoalesc.append(i) # save the index of the free chunk

        if chunk.status == "top": # we hitted the top chunk
            if len(tocoalesc) == 0: # nothing to do here
                continue
            if len(tocoalesc) >= 1: # we hitted the top with some free chunks
                for index in sorted(tocoalesc, reverse=True):
                    del state[index]


def docoalesc(state):
    consolidate = False # this flag indicates if fastchunks must be coalesced or not ( this will be true only if malloc_consolidate has been called )
    if state.fastchunks_bit == 0: # if it is 0 let's check from the libc dump if it is now 1 again ( this would mean that a malloc_consolidate has been called )
        if check_malloc_consolidate(state.libc_dump_name) == True:
            consolidate = True
    coalesc(state,consolidate)

def buildTimeline():
    for djson in api_call_json:
        api_name = djson['api_name']
        api_args = djson['api_args']
        api_counter = djson['api_counter']
        api_info = djson.get('api_info',[])
        api_ret  = djson.get('api_return',[])
        op = operations[api_name]
        state = timeline[-1]
        state.api_now = ""
        state.dump_name = ""
        state.libc_dump_name = ""
        state.info = []
        state.errors = []
        op(state,api_args,api_info,api_ret,api_counter)
        sort(state)
        topchunk = Chunk("0","0","0","0","top")
        state.append(topchunk) # dirty hack to detect the top chunk during coalescing
        docoalesc(state)
        state.pop() # remove the top chunk, we don't need to insert it in the timeline :-)
        timeline.append(copy.deepcopy(state))

'''
 Retrieve information about the process
 from the json and build the ProcInfo object
'''
def buildProcInfo():
    heap_range = proc_info_json.get('heap_range',[])
    if  heap_range != []:
        heap_start_address  = heap_range['heap_start_address']
        heap_end_address    = heap_range['heap_end_address']
    libc_version = proc_info_json.get('libc_version',[])
    libc_range = proc_info_json.get('libc_range',[])
    if libc_range != []:
        libc_start_address = libc_range['libc_start_address']
        libc_end_address   = libc_range['libc_end_address']
    arch = proc_info_json['arch']
    return ProcInfo(heap_start_address,heap_end_address,libc_version,libc_start_address,libc_end_address,arch)

def random_color(r=150, g=150, b=150):
    red = (random.randrange(0, 256) + r) / 2
    green = (random.randrange(0, 256) + g) / 2
    blue = (random.randrange(0, 256) + b) / 2
    return (str(red), str(green), str(blue))

# this function will search the chunk inside the hex-dump taken
def searchChunkInHexDump(chunk,start_addr_line,end_addr_line,hlog,line_counter):

    r,g,b = chunk.color[0],chunk.color[1],chunk.color[2]
    space_skip = 1 # number of space to skip in the .txt dump ( basically where we will put the tag for the color )
    start_found = False
    end_found = False

    print "Searching chunk boundaries in this range " + hex(start_addr_line) + " - " + hex(end_addr_line) + "\n"

    for _addr in xrange(start_addr_line,end_addr_line,4): # actually the last address checked here is int(splitted_line[0],16) + 0x1c, since xrange exclude the last boundary
        print "Checking " + hex(_addr) + "\n"
        if hex(_addr) == chunk.raw_addr:
            color_div = "<font color = \"rgb(" + r + "," + g + "," + b +")\">"
            log = str(line_counter) + "-" + str(space_skip) + "-" + color_div + "\n"
            hlog.write(log)
            start_found = True
            print "FOUND START"
        elif hex(_addr) == hex(int(chunk.chunk_end_addr,16) - 0x4): # this is the start address of the last dword of this chunk
            end_color_div = "</font>"
            log = str(line_counter) + "-" + str(space_skip) + "-" + end_color_div + "\n"
            hlog.write(log)
            end_found = True
            print "FOUND END"

        space_skip += 1

    if start_found == True and end_found == True: # start addresss and end address in the same line
        return 1
    if start_found == True and end_found == False: # start address of the chunk is in this line
        return 2
    if start_found == False and end_found == True: # end address of the chunk is in this line
        return 3


def doHexDumpTag(chunk,dump_name):
    logname = "./HexDumpTags.log"
    if not os.path.exists(logname): # this log will be used in order to create the colored hexdump html
        open(logname, 'w+').close()

    hlog = open("./HexDumpTags.log","a")
    r,g,b = chunk.color[0],chunk.color[1],chunk.color[2]

    dump_path = "./HeapDumps/" + dump_name

    with open(dump_path) as f:

        line_counter = -1
        start_found = False
        end_found = False

        for line in f:
            line_counter += 1
            splitted_line = line.split(" ")
            start_addr_line = int(splitted_line[0],16)
            end_addr_line   = int(splitted_line[0],16) + 0x20 # 0x20 coz we print 8 dword per line in the dumper
            start_found = False

            # let's try to search the boundary of this chunk inside the current line under analysis
            res = searchChunkInHexDump(chunk,start_addr_line,end_addr_line,hlog,line_counter)

            if res == 1:
                return
            if res == 2:
                start_found = True
                continue
            if res == 3 and start_found == True:
                return
            else:
                print "Something strange happen, skipping this chunk"

def buildHtml(timeline):
    print "[+]Generating report"
    hippy_gui_manager = HippyGuiManager(len(timeline))
    prev_state = None
    for index,state in enumerate(timeline):
        try:
            next_state = timeline[index+1] # try to retrieve the next state ( will be useful to print the next api call)
        except:
            next_state = None
        hippy_gui_manager.run(prev_state,state,next_state,procInfo)
        prev_state = state

operations = {'free': free, 'malloc': malloc, 'calloc': calloc, 'realloc': realloc}
procInfo = None
timeline = [State()]  # a timeline is a list of State


if __name__ == '__main__':

    progam_to_trace = sys.argv[1]  # first argument is the path to the program to trace

    cmd = "LD_PRELOAD=./tracer.so" + " " + progam_to_trace

    working_directory = os.getcwd()

    if len(sys.argv) == 3:
        input_program = sys.argv[2]
        cmd += " <" + input_program

    p = Popen(cmd, shell=True, stderr=PIPE, close_fds=True)
    output = p.stderr.read()

    # dump the output on file in order to lately read it line by line
    with open("./traced_out", "w") as f:
        f.write(output)

    f = open("./traced_out")
    content = f.readlines()
    f.close()

    parseProgramOut(content)
    procInfo = buildProcInfo()

    print procInfo
    buildTimeline()
    timeline = timeline[:-1] # remove last state
    cont = 1

    for s in timeline:
        print "timeline[" + str(cont) + "]:\n"
        print s
        cont+=1

    buildHtml(timeline)
