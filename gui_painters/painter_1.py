# ad hoc painter for libc 2.23 x32 

for i in xrange(0,start_line,1):
    line = f.readline() # skip unuseful lines

# now let's print the information based on the libc in user

if libc_version == "2.23" and arch == "32":
    first_line = line
    first_line = first_line.split(" ")
    malloc_state_info = self.soup.new_tag('font')
    malloc_state_info['style'] = "font-family: monospace;display:inline; color: black;"
    malloc_state_info.string = "mutex: " + first_line[1] + "\nflags: " + first_line[2]

    #div_libcdump.append(malloc_state_info)

    div_space_tag_wide = self.soup.new_tag('div')
    div_space_tag_wide['style'] = "font-size:0;height:20px;"
    #div_libcdump.append(div_space_tag)

    # then we have 10 fastbins
    fastbins_title = self.soup.new_tag('font')
    fastbins_title['style'] = "font-family: monospace;display:inline; color: red; font-weight: bold;"
    fastbins_title.string = "Fastbins"
    #div_libcdump.append(fastbins_title)

    hr_tag = self.soup.new_tag('hr')
    #div_libcdump.append(hr_tag)

    line = " ".join(line.split(" ")[3:]) # remove the address in the line

    fastbins_dump = self.soup.new_tag('font')
    fastbins_dump['style'] = "font-family: monospace;display:inline; color: black;"
    fastbins_dump.string = str(line) # let's paint the address
    #div_libcdump.append(fastbins_dump)

    next_line = f.readline()

    fbins = " ".join(next_line.split(" ")[1:-4])
    fastbins_dump_2 = self.soup.new_tag('font')
    fastbins_dump_2['style'] = "font-family: monospace;display:inline; color: black;"
    fastbins_dump_2.string = str(fbins) # let's paint the address
    #div_libcdump.append(fastbins_dump_2)

    #div_libcdump.append(hr_tag)

    div_space_tag = self.soup.new_tag('div')
    div_space_tag['style'] = "font-size:0;height:20px;"
    #div_libcdump.append(div_space_tag)

    top_chunk = next_line.split(" ")[5]

    malloc_state_info.string += "\ntop_chunk: " + top_chunk

    last_remainder = next_line.split(" ")[6]
    malloc_state_info.string += "\nlast_remainder: " + last_remainder

    div_libcdump.append(malloc_state_info)
    div_libcdump.append(div_space_tag_wide)
    div_libcdump.append(fastbins_title)
    div_libcdump.append(div_space_tag)
    div_libcdump.append(hr_tag)
    div_libcdump.append(div_space_tag)
    div_libcdump.append(fastbins_dump)
    div_libcdump.append(fastbins_dump_2)
    div_libcdump.append(hr_tag)
    div_libcdump.append(div_space_tag)

    div_space_tag = self.soup.new_tag('div')
    div_space_tag['style'] = "font-size:0;height:1px;"
    div_libcdump.append(div_space_tag)

    font_tag = self.soup.new_tag('font')
    font_tag['style'] = "font-family: monospace;display:inline; color: red; font-weight: bold;"
    font_tag.string = "Unsorted bins"

    div_libcdump.append(font_tag)
    hr_tag = self.soup.new_tag('hr')
    div_libcdump.append(hr_tag)

    unsorted_bins = " ".join(next_line.split(" ")[7:]) # remove the address in the line

    font_tag = self.soup.new_tag('font')
    font_tag['style'] = "font-family: monospace;display:inline; color: black;"
    font_tag.string = str(unsorted_bins) # let's paint the address
    div_libcdump.append(font_tag)

    hr_tag = self.soup.new_tag('hr')
    div_libcdump.append(hr_tag)

    div_space_tag = self.soup.new_tag('div')
    div_space_tag['style'] = "font-size:0;height:1px;"
    div_libcdump.append(div_space_tag)

    font_tag = self.soup.new_tag('font')
    font_tag['style'] = "font-family: monospace;display:inline; color: red; font-weight: bold;"
    font_tag.string = "Small bins"

    div_libcdump.append(font_tag)
    hr_tag = self.soup.new_tag('hr')
    div_libcdump.append(hr_tag)


    for i in xrange(0,15,1): # next 15 lines are small bins
        next_line = f.readline()
        next_line = " ".join(next_line.split(" ")[1:]) # remove the first dword
        font_tag = self.soup.new_tag('font')
        font_tag['style'] = "font-family: monospace;display:inline; color: black;"
        font_tag.string = str(next_line) # let's paint the address
        div_libcdump.append(font_tag)

    hr_tag = self.soup.new_tag('hr')
    div_libcdump.append(hr_tag)

    div_space_tag = self.soup.new_tag('div')
    div_space_tag['style'] = "font-size:0;height:1px;"
    div_libcdump.append(div_space_tag)

    font_tag = self.soup.new_tag('font')
    font_tag['style'] = "font-family: monospace;display:inline; color: red; font-weight: bold;"
    font_tag.string = "Large bins"

    div_libcdump.append(font_tag)
    hr_tag = self.soup.new_tag('hr')
    div_libcdump.append(hr_tag)


    for i in xrange(0,16,1): # next 16 lines are small bins
        next_line = f.readline()
        next_line = " ".join(next_line.split(" ")[1:]) # remove the first dword
        font_tag = self.soup.new_tag('font')
        font_tag['style'] = "font-family: monospace;display:inline; color: black;"
        font_tag.string = str(next_line) # let's paint the address
        div_libcdump.append(font_tag)

    hr_tag = self.soup.new_tag('hr')
    div_libcdump.append(hr_tag)
