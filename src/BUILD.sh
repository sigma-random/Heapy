gcc -m32 -shared -fPIC -Wl,-z,relro,-z,now -o tracer.so tracer.c -ldl
gcc -m32 -Wl,-z,relro,-z,now -o tracer_child tracer_child.c
gcc -m32 -Wl,-z,relro,-z,now -o readmem readmem.c
mkdir -p ../bin/i386/
mv ./tracer.so ../bin/i386/tracer.so
mv ./tracer_child ../bin/i386/tracer_child
mv ./readmem ../bin/i386/readmem


gcc -shared -fPIC -Wl,-z,relro,-z,now -o tracer.so tracer.c -ldl
gcc -Wl,-z,relro,-z,now -o tracer_child tracer_child.c
gcc -Wl,-z,relro,-z,now -o readmem readmem.c
mkdir -p ../bin/amd64/
mv ./tracer.so ../bin/amd64/tracer.so
mv ./tracer_child ../bin/amd64/tracer_child
mv ./readmem ../bin/amd64/readmem
