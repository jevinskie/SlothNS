#include "pow.h"
#include <stdio.h>

int main(void)
{
    pow_t *p;
    pow_req_t *r;

    p = pow_create(24, 20, 0);
    r = pow_create_req(p);
    pow_destroy_req(r);
    pow_destroy(p);

    return 0;
}

