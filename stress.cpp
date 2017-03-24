#include <omp.h>
#include <cmath>
#include <ctime>
#include <cstdlib>
#include <iostream>
#include <unistd.h>
#include <signal.h>
using namespace std;

void sig_handler(int) {
	exit(EXIT_SUCCESS);
}

int main(int argc, char * const argv[]) {
	if (argc != 2) return 0;
	signal(SIGALRM, sig_handler);
	alarm(atoi(argv[1]));
	srand(time(NULL));
	int nproc = sysconf(_SC_NPROCESSORS_ONLN);
	unsigned int seed[nproc];
	for (int i = 0; i < nproc; ++i)
		seed[i] = rand();
	#pragma omp parallel for
	for (int i = 0; i < nproc; ++i) {
		while (true)
			cbrt(rand_r(&seed[omp_get_thread_num()]));
	}
	return 0;
}
