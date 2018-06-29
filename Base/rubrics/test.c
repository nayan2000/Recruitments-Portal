#include <stdio.h>

int foo(){
	return 1;
}

int main(){
	printf("%p\n", &foo);
	return 0;
}
