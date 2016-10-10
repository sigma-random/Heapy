
# supported_libc contains the the lines to take in order to retrieve the malloc_state
# from the libc data segment
# f.i. 2.23-32 is the libc 2.23 on 32 bit, 61-95 means that from line 61 to 95 of the hexdump we have the info about bins

class HeapyLibcFormatter:
    def __init__(self,libc_dump_full_path,proc_info,soup):
        self.supported_libc = {"2.19-64": "60-128", "2.23-64": "90-158"}
        self.formatter_dictionary = {"2.19-64": self.formatter_1 , "2.23-64": self.formatter_1 }
        self.libc_dump_full_path = libc_dump_full_path
        self.proc_info = proc_info
        self.soup = soup


    def format(self):
        libc_version = self.proc_info.libc_version
        arch = self.proc_info.architecture
        lines_range = self.supported_libc.get(libc_version+"-"+arch,"")

        if lines_range != "": # let's extract only the lines in which there is the _state struct
            start_line = int(lines_range.split("-")[0],10)
            end_line = int(lines_range.split("-")[1],10)
        else:
            print "[ERROR] Libc not supported - heapy will paste the raw dump"

        formatter = self.formatter_dictionary.get(libc_version+"-"+arch,"") #extract the right formatter for this libc

        formatter(start_line,end_line)

    # generic formatter, this will paste the raw dump in the section libc of the final report
    def formatter_0(self,start_line,end_line):

        f = open(self.libc_dump_full_path, "r")
        div_libcdump = self.soup.find(id="libcdump")

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

    # this formatter print out the information about the bins discovered in the libc dump
    def formatter_1(self,start_line,end_line):

        f = open(self.libc_dump_full_path, "r")
        div_libcdump = self.soup.find(id="libcdump")

        for i in xrange(0,start_line,1):
            line = f.readline().rstrip() # skip unuseful lines

        line = line.split(" ")
        line = line[1:] # remove the memory address

        #space
        div_space = self.soup.new_tag('div')
        div_space['style'] = "font-size:0;height:5px;"

        # flags qwords
        flags_div = self.soup.new_tag('div')
        flags_div['style'] = "font-family: monospace;display:inline;"
        flags_div.string = "flags: " + line[1] + line[0]

        line = line[2:] # discard the first processed elements

        # fastbins
        for i in xrange(0,10,1):
            if line == []:
                line = f.readline().rstrip().split(" ")
                line = line[1:]

            fastbin_div = self.soup.new_tag('div')
            fastbin_div['style'] = "font-family: monospace;display:inline;"
            fastbin_div.string = "fastbin["+str(i)+"]-> 0x" + line[1] + line[0]
            div_libcdump.append(fastbin_div)
            div_space = self.soup.new_tag('div')
            div_space['style'] = "font-size:0;height:5px;"
            div_libcdump.append(div_space)
            line = line[2:]

        #top chunk
        top_chunk_div = self.soup.new_tag('div')
        top_chunk_div['style'] = "font-family: monospace;display:inline;"
        top_chunk_div.string = "topchunk: 0x" + line[1] + line[0]
        div_libcdump.append(top_chunk_div)
        div_space = self.soup.new_tag('div')
        div_space['style'] = "font-size:0;height:5px;"
        div_libcdump.append(div_space)

        line = f.readline().rstrip().split(" ")
        line = line[1:]

        #last remains
        last_remain_div = self.soup.new_tag('div')
        last_remain_div['style'] = "font-family: monospace;display:inline;"
        last_remain_div.string = "last remainder: 0x" + line[1] + line[0]
        div_libcdump.append(last_remain_div)
        div_space = self.soup.new_tag('div')
        div_space['style'] = "font-size:0;height:5px;"
        div_libcdump.append(div_space)

        line = line[2:]

        #unsorted bin
        unsorted_bin_fd = self.soup.new_tag('div')
        unsorted_bin_fd['style'] = "font-family: monospace;display:inline;"
        unsorted_bin_fd.string = "unsorted bin{fd} -> 0x" + line[1] + line[0]
        div_libcdump.append(unsorted_bin_fd)

        div_space = self.soup.new_tag('div')
        div_space['style'] = "font-size:0;height:5px;"
        div_libcdump.append(div_space)

        line = line[2:]

        unsorted_bin_fd = self.soup.new_tag('div')
        unsorted_bin_fd['style'] = "font-family: monospace;display:inline;"
        unsorted_bin_fd.string = "unsorted bin{bk} -> 0x" + line[1] + line[0]
        div_libcdump.append(unsorted_bin_fd)

        line = line[2:]

        div_space = self.soup.new_tag('div')
        div_space['style'] = "font-size:0;height:5px;"
        div_libcdump.append(div_space)

        #small bins
        for i in xrange(0,62,1):
            if len(line) == 2:
                nextline = f.readline().rstrip().split(" ")
                nextline = nextline[1:]
                small_bin_fd = self.soup.new_tag('div')
                small_bin_fd['style'] = "font-family: monospace;display:inline;"
                small_bin_fd.string = "smallbin["+str(i)+"]{fd}-> 0x" + line[1] + line[0]
                div_libcdump.append(small_bin_fd)
                div_space = self.soup.new_tag('div')
                div_space['style'] = "font-size:0;height:5px;"
                div_libcdump.append(div_space)
                small_bin_bk = self.soup.new_tag('div')
                small_bin_bk['style'] = "font-family: monospace;display:inline;"
                small_bin_bk.string = "smallbin["+str(i)+"]{bk}-> 0x" + nextline[1] + nextline[0]
                div_libcdump.append(small_bin_bk)
                div_space = self.soup.new_tag('div')
                div_space['style'] = "font-size:0;height:5px;"
                div_libcdump.append(div_space)
                line = nextline
                line = line[2:]
            else:
                small_bin_fd = self.soup.new_tag('div')
                small_bin_fd['style'] = "font-family: monospace;display:inline;"
                small_bin_fd.string = "smallbin["+str(i)+"]{fd}-> 0x" + line[1] + line[0]
                div_libcdump.append(small_bin_fd)
                div_space = self.soup.new_tag('div')
                div_space['style'] = "font-size:0;height:5px;"
                div_libcdump.append(div_space)
                line = line[2:]
                small_bin_bk = self.soup.new_tag('div')
                small_bin_bk['style'] = "font-family: monospace;display:inline;"
                small_bin_bk.string = "smallbin["+str(i)+"]{bk}-> 0x" + line[1] + line[0]
                div_libcdump.append(small_bin_bk)
                div_space = self.soup.new_tag('div')
                div_space['style'] = "font-size:0;height:5px;"
                div_libcdump.append(div_space)
                line = line[2:]


        #large bins
        for i in xrange(0,63,1):
            if len(line) == 2:
                nextline = f.readline().rstrip().split(" ")
                nextline = nextline[1:]
                large_bin_fd = self.soup.new_tag('div')
                large_bin_fd['style'] = "font-family: monospace;display:inline;"
                large_bin_fd.string = "largebin["+str(i)+"]{fd}-> 0x" + line[1] + line[0]
                div_libcdump.append(large_bin_fd)
                div_space = self.soup.new_tag('div')
                div_space['style'] = "font-size:0;height:5px;"
                div_libcdump.append(div_space)
                large_bin_bk = self.soup.new_tag('div')
                large_bin_bk['style'] = "font-family: monospace;display:inline;"
                large_bin_bk.string = "largebin["+str(i)+"]{bk}-> 0x" + nextline[1] + nextline[0]
                div_libcdump.append(large_bin_bk)
                div_space = self.soup.new_tag('div')
                div_space['style'] = "font-size:0;height:5px;"
                div_libcdump.append(div_space)
                line = nextline
                line = line[2:]
            else:
                large_bin_fd = self.soup.new_tag('div')
                large_bin_fd['style'] = "font-family: monospace;display:inline;"
                large_bin_fd.string = "largebin["+str(i)+"]{fd}-> 0x" + line[1] + line[0]
                div_libcdump.append(large_bin_fd)
                div_space = self.soup.new_tag('div')
                div_space['style'] = "font-size:0;height:5px;"
                div_libcdump.append(div_space)
                line = line[2:]
                large_bin_bk = self.soup.new_tag('div')
                large_bin_bk['style'] = "font-family: monospace;display:inline;"
                large_bin_bk.string = "largebin["+str(i)+"]{bk}-> 0x" + line[1] + line[0]
                div_libcdump.append(large_bin_bk)
                div_space = self.soup.new_tag('div')
                div_space['style'] = "font-size:0;height:5px;"
                div_libcdump.append(div_space)
                line = line[2:]
