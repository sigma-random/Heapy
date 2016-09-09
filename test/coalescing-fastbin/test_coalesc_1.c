#include <stdlib.h>
#include <stdio.h>

/*
 chunk c is not reused
*/
int main(){


	unsigned int c = malloc(4);
	free(c);
  unsigned int d = malloc(100);



}
