
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

char path[30] = {"/proc/"};
char hippy_tag[30] = {"heapy-d75d6fc7"};

int main(int argc , char* argv[]){

  char string_ppid[6];
  uint16_t ppid = getppid();
  sprintf(string_ppid, "%d",ppid);
  strcat(path,string_ppid);
  strcat(path,"/maps");
  char heap_start_address[30] = {0};
  char heap_end_address[30] = {0};
  char libc_start_address[30] = {0}; // information about the bins ( malloc_state struct ) are in the .bss
  char libc_end_address[30] = {0};
  char libc_version[30] = {0};
  int cont = 0;
  char * line = NULL;
  char * libc_line = NULL;
  size_t len = 0;
  ssize_t read;
  size_t size_arch = sizeof(size_t); // get the size of size_t in order to discover if we are using a 32 or 64 bits binary
                                     // this should reflect the binary traced since we must use a 32 bit tracer to track a 32 bit binary
                                     // and a 64 bit tracer to track a 64 bit binary
  if(size_arch == 4){
    size_arch = 32;
  }else{
    size_arch = 64;
  }

  FILE * f1 = fopen(path,"r");
  int heap_found = 0;
  int libc_found = 0;

  while ((read = getline(&line, &len, f1)) != -1) {

    if (strstr(line, "[heap]") != NULL) { // found the line in the /proc/<pid>/maps with the heap information
       heap_found = 1;
       char *c = line;

       while(*c != '-'){
         heap_start_address[cont] = *c;
         c++;
         cont++;
       }

       c++;
       cont = 0;

       while(*c!=' '){
         heap_end_address[cont] = *c;
         c++;
         cont++;
       }
    }

    cont = 0;
    // searching for the .bss of the libc mapped in memory:
    // 7f6138cee000-7f6138cf0000 rw-p 001c3000 fc:01 13373861 /lib/x86_64-linux-gnu/libc-2.23.so
    if (strstr(line, "libc-") != NULL && strstr(line, "rw-p") != NULL ) { // found the line in the /proc/<pid>/maps with the  bss libc information

       libc_found = 1;
       char *c = line; // with this we extract the address range

       while(*c != '-'){
         libc_start_address[cont] = *c;
         c++;
         cont++;
       }

       c++;
       cont = 0;

       while(*c!=' '){
         libc_end_address[cont] = *c;
         c++;
         cont++;
       }

       // now let's extract the libc version in use by the program with a dirty trick
       libc_line = strstr(line, "libc-");
       char *c1 = libc_line+5; // skip the "libc-"
       cont = 0;

       while(*c1 != 's'){
         libc_version[cont] = *c1;
         c1++;
         cont++;
       }

       libc_version[cont] = 0;
       libc_version[cont-1] = 0;

    }

    if(heap_found == 1 && libc_found == 1){
       break; // found the [heap] line and the libc line address range
     }
  }

  if(heap_found == 0 || libc_found == 0){
     fprintf(stderr,"[ERROR] Couldn't find the address range needed!\n");
  }

  // record the information about the mapped heap
  FILE *f = fopen("./heap_log","w");
  fprintf(f,"%d\n",ppid);
  fprintf(f,"0x%s\n",heap_start_address);
  fprintf(f,"0x%s\n",heap_end_address);
  fprintf(f,"0x%s\n",libc_start_address);
  fprintf(f,"0x%s\n",libc_end_address);
  fclose(f);


  fprintf(stderr,"\n\n<%s>\n{\"type\": \"procinfo\",\"heap_range\": {\"heap_start_address\": \"0x%s\",\"heap_end_address\": \"0x%s\"}, \"libc_version\": \"%s\" , \"libc_range\": \\
                 {\"libc_start_address\": \"0x%s\",\"libc_end_address\": \"0x%s\"}, \"arch\": \"%zd\"}\n</%s>\n\n",
                 hippy_tag,heap_start_address,heap_end_address,libc_version,libc_start_address,libc_end_address,size_arch,hippy_tag);

  /*
  char *ptr;
  size_t heap_start_value = strtoull(heap_start_address, &ptr, 16);
  size_t heap_end_value   = strtoull(heap_end_address, &ptr, 16);

  fprintf(stderr,"HEAP-START-ADDRESS IS 0x%zx\n",heap_start_value);
  fprintf(stderr,"HEAP-END-ADDRESS IS 0x%zx\n",heap_end_value);

  fclose(f1);
  */

  exit(0); // bye bye son
}
