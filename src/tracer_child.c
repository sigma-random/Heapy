
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

int main(int argc , char* argv[]){

  char string_ppid[6];
  char path[30] = {"/proc/"};
  uint16_t ppid = getppid();
  sprintf(string_ppid, "%d",ppid);
  strcat(path,string_ppid);
  strcat(path,"/maps");
  char *hippy_tag = {"hippy-d75d6fc7"};
  char heap_start_address[30] = {0};
  char heap_end_address[30] = {0};
  int cont = 0;
  char * line = NULL;
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

  while ((read = getline(&line, &len, f1)) != -1) {
    if (strstr(line, "[heap]") != NULL) { // found the line in the /proc/<pid>/maps with the heap information
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

       break; // found the [heap] line
    }
  }

  // record the information about the mapped heap
  FILE *f = fopen("./heap_log","w");
  fprintf(f,"%d\n",ppid);
  fprintf(f,"0x%s\n",heap_start_address);
  fprintf(f,"0x%s\n",heap_end_address);
  fclose(f);

  fprintf(stderr,"\n\n<%s>\n{\"type\": \"procinfo\",\"heap_range\": {\"heap_start_address\": \"0x%zx\",\"heap_end_address\": \"0x%zx\"}, \"arch\": \"%zd\"}\n</%s>\n\n",hippy_tag,heap_start_address,heap_end_address,size_arch,hippy_tag);

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
