
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

int main(int argc , char* argv[]){

  char *ptr;
  char *a;
  char start_heap[30];
  char end_heap[30];
  int cont = 0;
  int row = 4;

  fprintf(stderr,"OPENING LOG FILE\n");
  FILE *f = fopen("./heap_log","r");
  fprintf(stderr,"OPENED LOG FILE\n");

  fscanf(f,"%s", start_heap);
  fscanf(f,"%s", end_heap);
  fclose(f);
  size_t heap_start_value = strtoull(start_heap, &ptr, 16);
  size_t heap_end_value   = strtoull(end_heap, &ptr, 16);

  fprintf(stderr,"HEAP-START-ADDRESS CALC IS 0x%zx\n",heap_start_value);
  fprintf(stderr,"HEAP-END-ADDRESS CALC IS 0x%zx\n",heap_end_value);

  f = fopen("./dump_heap", "a");

  for( a=(char *)heap_start_value; a < heap_end_value; a+=4){
      //printf("a is %zx, *a is %02x\n",a,*a);
      if(row == 4){
        fprintf(f,"0x%zx %02x%02x%02x%02x",a,*(unsigned char *)(a+3),*(unsigned char *)(a+2),*(unsigned char *)(a+1),*(unsigned char *)a);
      }else{
        fprintf(f,"%02x%02x%02x%02x",*(unsigned char *)(a+3),*(unsigned char *)(a+2),*(unsigned char *)(a+1),*(unsigned char *)a);
      }

      if(row!=1){
        fprintf(f," ");
        row--;
      }
      else{
        fprintf(f,"\n");
        row=4;
      }
      cont++;
  }

  fclose(f);
  exit(0);
}
