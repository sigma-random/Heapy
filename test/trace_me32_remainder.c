#include <stdlib.h>
#include <stdio.h>

int main(){


unsigned int a = malloc(1000);
unsigned int b = malloc(1000);
unsigned int c = malloc(1000);

free(b);

unsigned int d = malloc(300);
unsigned int e = malloc(300);
unsigned int f = malloc(300);

free(e);

unsigned int i = malloc(100);
unsigned int j = malloc(100);
unsigned int k = malloc(100);
}