
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
  char *hippy_tag_line = {"HIPPY"};
  char *hippy_tag_start = {"HIPPY-START"};
  char *hippy_tag_end = {"HIPPY-END"};

  char heap_start_address[30] = {0};
  char heap_end_address[30] = {0};
  int cont = 0;
  char * line = NULL;
  size_t len = 0;
  ssize_t read;
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

  fprintf(stderr,"[%s]\n",hippy_tag_start);
  fprintf(stderr,"[%s]HEAP ADDRESS RANGE: 0x%s - 0x%s\n[%s]\n",hippy_tag_line,heap_start_address,heap_end_address,hippy_tag_end);

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
