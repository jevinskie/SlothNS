#include "pow.h"
#include <stdio.h>

int main(void)
{
    pow_t *p;
    pow_req_t *req;
    pow_res_t *res;

    p = pow_create(24, 20, 0);
    req = pow_create_req(p);
    res = pow_create_res(p, req);
    printf("%d\n", pow_verify_res(p, req, res));
    pow_destroy_res(res);
    pow_destroy_req(req);
    pow_destroy(p);

    return 0;
}

