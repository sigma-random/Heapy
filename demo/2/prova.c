#include <stdio.h>
#include <stdlib.h>



int main(){

	unsigned int a = malloc(3000);
	unsigned int v = malloc(2000);
	unsigned int x = malloc(12300);
	free(v);
        free(x);
	free(a);
	unsigned int vl = malloc(3242);



}
