#ifndef __workfct_h_
#define __workfct_h_

#include <stdlib.h>
#include <stdio.h>

// Constant Definitions

/* Return/Error Codes */
#define OK               (  0 )  // No errors, everything as should be
#define ERROR            ( -1 ) // Generic error

#define POW2(n) (1<<(n))

// structures

struct req_data;

typedef struct req_data {
	int size;
	int depth;
	int seed;
	int init_cond;
	int *v;
	int *w;
	int c;
} myReq;
  
/* Function Prototypes */
void gen_permTable(int *T, int size, int seed);
myReq gen_req(int size, int depth, int *T, int seed, int *v, int *w);
int solve_req(myReq r, int chk_sum, int x, int level, int *T);
int verify_req(myReq r, int path, int *T);

#endif  // __workfct_h_

