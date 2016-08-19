gcc -m32 -shared -fPIC -o tracer.so tracer.c -ldl
gcc -m32 -o tracer_child tracer_child.c
gcc -m32 -o readmem readmem.c
mv ./tracer.so ../bin/i386/tracer.so
mv ./tracer_child ../bin/i386/tracer_child
mv ./readmem ../bin/i386/readmem

gcc -shared -fPIC -o tracer.so tracer.c -ldl
gcc -o tracer_child tracer_child.c
gcc -o readmem readmem.c
mv ./tracer.so ../bin/amd64/tracer.so
mv ./tracer_child ../bin/amd64/tracer_child
mv ./readmem ../bin/amd64/readmem
