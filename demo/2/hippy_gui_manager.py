import os
import copy
import sys
from bs4 import BeautifulSoup
import pdb

# configurable parameter libc-version dependent
# these are the lines to take in order to retrieve the malloc_state
# from the libc data segment
# f.i. 2.23-32 is the libc 2.23 on 32 bit, 61-96 means that from line 61 to 95 of the hexdump we have the info about bins
supported_libc = {"2.19-64": "60-128", "2.23-32": "61-95" , "2.23-64": "89-158"}

class HippyGuiManager:

    def __init__(self,number_of_states):
        self.html_report_base = "/home/degrigis/Project/Hippy/gui/base2.html" # base html to modify in order to draw the current state
        self.html_report_folder = "./StateHtmlReports" # this folder will contains all the html generated that describe a state
        self.html_report_current_name = "heapstate_X"  # this will be the name of the generated html report
        self.html_report_counter = 1
        self.heap_dump_folder = "./HeapDumps/"
        self.libc_dump_folder = "./LibcDumps/"
        self.current_state_obj = "" # passed later in the run method
        self.current_state_heap_dump = "" # passed later in the run method
        self.current_state_libc_dump = "" # passed later in the run method
        self.soup = []
        self.proc_info = []
        self.number_of_states = number_of_states
        return

    def run(self,prev_state,current_state_obj, next_state, proc_info):
        self.current_state_obj = current_state_obj # the current state to draw on html
        self.proc_info = proc_info
        #self.current_state_heap_dump = current_state_heap_dump # this is the hexdump taken of the heap of the program
        #self.current_state_libc_dump = current_state_libc_dump # this is the hexdump taken of the libc data ( the bins )

        if not os.path.exists(self.html_report_folder):
            os.makedirs(self.html_report_folder)

        self.soup = BeautifulSoup(open(self.html_report_base),"html.parser") # let's open the html_report_base as a soup structure
        html_report_full_path = self.html_report_folder + "/" + self.html_report_current_name.replace("X",str(self.html_report_counter)) # compose finally the name of the html_report_path
        self.html_report_counter = self.html_report_counter + 1 # and increment it :-)

        # now let's start the serious business
        self.write_state_info(prev_state,next_state)
        self.write_generic_info(prev_state,next_state)
        self.build_heap_state()
        self.paste_heap_dump(self.current_state_obj,proc_info)
        self.paste_libc_dump(self.current_state_obj,proc_info)

        # a pinch of javascript for better navigation between reports

        div_script = self.soup.find(id="lolscripts")

        if self.html_report_counter > self.number_of_states:
            javascript_next = "function next_page(){ window.location.href = \"./heapstate_" + str(self.html_report_counter-1) + "\";}"
        else:
            javascript_next = "function next_page(){ window.location.href = \"./heapstate_" + str(self.html_report_counter) + "\";}"

        if self.html_report_counter-1 == 1:
            javascript_prev = "function prev_page(){ window.location.href = \"./heapstate_" + str(self.html_report_counter-1) + "\";}"
        else:
            javascript_prev = "function prev_page(){ window.location.href = \"./heapstate_" + str(self.html_report_counter-2) + "\";}"

        div_script.append(javascript_next)
        div_script.append(javascript_prev)

        # ok, let's save the modified html
        heap_state_html = self.soup.prettify("utf-8")
        with open(html_report_full_path, "wb") as file:
            file.write(heap_state_html)

        self.soup = []

    def write_generic_info(self,prev_state,next_state):
        div_info = self.soup.find(id="ginfo") # insert the name of the api now
        center_text = self.soup.new_tag('center')
        ginfo = "heap-range:   " + self.proc_info.heap_start_address + " - " + self.proc_info.heap_end_address + " | " + "libc-range:   " + self.proc_info.libc_start_address + " - " + self.proc_info.libc_end_address + " | " + "libc-version: " + self.proc_info.libc_version
        center_text.string = ginfo

        div_info.append(center_text)



    # this function will write the current api invoked and other information
    # related to the state of the heap
    def write_state_info(self,prev_state,next_state):
        div_info = self.soup.find(id="info") # insert the name of the api now

        if prev_state != None:
            center_tag =  self.soup.new_tag("center")
            div_info_line = self.soup.new_tag('div')
            div_info_line.string = "PREVCALL: " + str(prev_state.api_now)
            div_info_line['style'] = "font-size:10;font-family: monospace;"
            center_tag.append(div_info_line)
            div_info.append(center_tag)

        center_tag =  self.soup.new_tag("center")
        center_tag['style'] = "background:#ccff99;"
        div_info_line = self.soup.new_tag('div')
        center_tag.string = "CURRENTCALL: " + self.current_state_obj.api_now
        div_info_line['style'] = "font-size:20;font-family: monospace;"
        center_tag.append(div_info_line)
        div_info.append(center_tag)

        if next_state != None:
            center_tag =  self.soup.new_tag("center")
            div_info_line = self.soup.new_tag('div')
            div_info_line.string = "NEXTCALL: " + str(next_state.api_now)
            div_info_line['style'] = "font-size:10;font-family: monospace;"
            center_tag.append(div_info_line)
            div_info.append(center_tag)
            div_info.append(center_tag)

    # this function insert inside the heap_state div of the base html
    # the square related to the heap chunks
    def build_heap_state(self):
        for chunk in self.current_state_obj: # now let's append all the block related to chunks
            if chunk.status == "allocated":
                r,g,b = chunk.color[0],chunk.color[1],chunk.color[2]
                div_heap_state = self.soup.find(id="heap_state")
                block_tag = self.soup.new_tag("div")
                block_tag['class'] = "block normal"
                block_layout = "width: 100%; height: 6%; background-color: rgb(RXXX, GXXX, BXXX);;"
                block_layout = block_layout.replace("RXXX",r)
                block_layout = block_layout.replace("GXXX",g)
                block_layout = block_layout.replace("BXXX",b)
                block_tag['style'] = block_layout
                block_tag.string = chunk.raw_addr + "-" + chunk.type + "[" + chunk.full_chunk_size + "]"
                div_heap_state.append(block_tag)
            if chunk.status == "free":
                div_heap_state = self.soup.find(id="heap_state")
                block_tag = self.soup.new_tag("div")
                block_tag['class'] = "block normal"
                block_layout = "width: 100%; height: 6%; background-color: rgb(255, 255, 255);;"
                block_tag['style'] = block_layout
                block_tag.string = "[F]" + chunk.raw_addr + "-" + chunk.type + "[" + chunk.full_chunk_size + "]"
                div_heap_state.append(block_tag)

        div_heap_state = self.soup.find(id="heap_state")
        block_tag = self.soup.new_tag("div")
        block_tag['class'] = "block normal"
        block_layout = "width: 100%; height: 100%; background-color: rgb(0, 255, 0);;"
        block_tag['style'] = block_layout
        block_tag.string = "TOP CHUNK"
        div_heap_state.append(block_tag)

    # Given a memory address and a state this function builds the correspondance between
    # a memory address and its content, it also tries to tag a memory address with a
    # chunk. The final result is something like that:
    #----------------------------------------
    #     memaddr        content     chunk_n
    # ---------------------------------------
    # 0x55daa2522000 |  0x00000000 |  chunk0
    # 0x55daa2522004 |  0x00000000 |  chunk0
    # 0x55daa2522008 |  0x00000041 |  chunk0
    # 0x55daa252200c |  0x00000023 |  chunk1
    #    [ ... ]           [...]       [...]
    # 0x55daa252201c |  0x00000013 |  chunk1
    #----------------------------------------
    def getMemoryAddrTableRepr(self,current_memory_addr,line,state,last_addr_end, last_identified_chunk):
        table = []
        cont = 0  # number of the dword in the line
        addr_end = last_addr_end
        current_chunk = last_identified_chunk
        current_memory_addr = int(current_memory_addr,16)
        for addr in xrange(current_memory_addr,current_memory_addr+0x20,0x4):
            if addr_end != 0 and addr < addr_end: # in this case we have identified a chunk previously!
                mytuple = (hex(addr),line[cont].rstrip(),current_chunk.color)
                table.append(mytuple)
            elif addr_end != 0 and addr > addr_end: # we have overtaken the end address of the chunk identified
                addr_end = 0 # reset
                last_identified_chunk = []

            if addr_end == 0: # no chunk identified yet...
                chunk_index, current_chunk = state.getChunkAtRawAddress(hex(addr))
                if chunk_index != -1: # we have identified correctly a chunk at the raw address
                    addr_end = addr + int(current_chunk.full_chunk_size,10) - 0x1
                    mytuple = (hex(addr),line[cont].rstrip(),current_chunk.color)
                    table.append(mytuple)
                else:
                    mytuple = (hex(addr),line[cont].rstrip(),('0','0','0'))
                    table.append(mytuple)
            cont+=1 # next dword
        return addr_end, current_chunk,table



    def paste_heap_dump(self,state,proc_info):
        heap_dump_full_path = self.heap_dump_folder + state.dump_name
        f = open(heap_dump_full_path, "r")
        highest_heap_address = state.last_heap_address # this is useful in order to reduce the amount of dword pasted in the html ( more light html! )

        div_heapdump = self.soup.find(id="heapdump") # insert the name of the api now
        last_addr_end = 0
        last_identified_chunk = []

        for line in f.readlines():
            # first entry of the line is the memory address
            current_memory_addr = line.split(" ")[0]
            if int(current_memory_addr,16) < int(highest_heap_address,16): # print only until the highest address reached during the execution until now
                font_tag = self.soup.new_tag('font')
                font_tag['style'] = "color: black; font-weight: bold;"
                font_tag.string = current_memory_addr # let's paint the address
                div_heapdump.append(font_tag)

                line = line.split(" ")[1:] # remove the address in the line

                # now let's paint our memory dword
                address_of_a_chunk = []
                address_of_next_chunk = []
                chunk_end = False

                last_addr_end,last_identified_chunk,table = self.getMemoryAddrTableRepr(current_memory_addr,line,state,last_addr_end,last_identified_chunk)

                # now let's follow the indication inside table in order
                # to print the dwords
                prev_color = ""
                dwords = ""
                for t in table:
                    curr_color = t[2] # take the color from the tuple
                    if curr_color != prev_color: # we need to open a new tag
                        if dwords != "":
                            dword_tag.string = dwords
                            div_heapdump.append(dword_tag)
                            dwords = ""
                        r,g,b = curr_color[0],curr_color[1],curr_color[2]
                        dword_tag = self.soup.new_tag('font')
                        dword_tag_style = "font-family: monospace;display:inline; color: rgb(RXXX, GXXX, BXXX);;"
                        dword_tag_style = dword_tag_style.replace("RXXX",r)
                        dword_tag_style = dword_tag_style.replace("GXXX",g)
                        dword_tag_style = dword_tag_style.replace("BXXX",b)
                        dword_tag['style'] = dword_tag_style
                        dwords = dwords + " " + t[1]
                        prev_color = curr_color
                    else:
                        dwords = dwords + " " + t[1]
                        prev_color = curr_color

                if dwords != "":
                    dword_tag.string = dwords
                    div_heapdump.append(dword_tag)

                div_space_tag = self.soup.new_tag('div')
                div_space_tag['style'] = "font-size:0;height:1px;"
                div_heapdump.append(div_space_tag)

            else:
                break


    def paste_libc_dump(self,state,proc_info):
        libc_dump_full_path = self.libc_dump_folder + state.libc_dump_name
        f = open(libc_dump_full_path, "r")
        div_libcdump = self.soup.find(id="libcdump")
        libc_version = self.proc_info.libc_version
        arch = proc_info.architecture

        lines_range = supported_libc.get(libc_version+"-"+arch,"")
        if lines_range != "": # let's extract only the lines in which there is the malloc_state struct
            start_line = int(lines_range.split("-")[0],10)
            end_line = int(lines_range.split("-")[1],10)
        else:
            print "[ERROR] Libc not supported"
            sys.exit(0)

        cont = 1

        for line in f.readlines(): # this optimization in order to avoid pase unuseful stuff in the libc view
            if cont < start_line:
                cont+=1
                continue
            if cont > end_line:
                break

            # first entry of the line is the memory address
            font_tag = self.soup.new_tag('font')
            font_tag['style'] = "color: black; font-weight: bold;"
            font_tag.string = str(line.split(" ")[0]) # let's paint the address
            div_libcdump.append(font_tag)

            line = " ".join(line.split(" ")[1:]) # remove the address in the line

            p_tag = self.soup.new_tag('p')
            p_tag.string = str(line)
            p_tag['style'] = "font-family: monospace;display:inline;"
            div_libcdump.append(p_tag)
            div_space_tag = self.soup.new_tag('div')
            div_space_tag['style'] = "font-size:0;height:1px;"
            div_libcdump.append(div_space_tag)
            cont += 1
