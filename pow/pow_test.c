#include <stdio.h>
#include "pow.h"

int main(void)
{
    pow_t *p;
    pow_req_t *req;
    pow_res_t *res;

    printf("creating pow\n");
    fflush(stdout);
    p = pow_create(24, 0);

    printf("creating req\n");
    fflush(stdout);
    req = pow_create_req(p, 20);

    printf("creating res\n");
    fflush(stdout);
    res = pow_create_res(p, req);

    printf("verifying res\n");
    fflush(stdout);
    printf("%d\n", pow_verify_res(p, req, res));
    fflush(stdout);

    printf("destroying res\n");
    fflush(stdout);
    pow_destroy_res(res);

    printf("destroying req\n");
    fflush(stdout);
    pow_destroy_req(req);

    printf("destroying pow\n");
    fflush(stdout);
    pow_destroy(p);

    return 0;
}

