#include <stdint.h>
#include <stdlib.h>
#include <assert.h>

typedef struct {
    uint32_t *perm_table;
    uint32_t rand[4];
    uint32_t seed;
    uint32_t size;
    uint32_t n;
} pow_t;

typedef struct {
    uint32_t x0;
    uint32_t check;
    uint32_t l;
    uint32_t *v, *w;
} pow_req_t;

typedef struct {
    uint32_t path;
} pow_res_t;

pow_t *pow_create(uint32_t n, uint32_t seed);
void pow_destroy(pow_t *p);
pow_req_t *pow_create_req(pow_t *p, uint32_t l);
void pow_destroy_req(pow_req_t *r);
int pow_verify_res(pow_t *p, pow_req_t *req, pow_res_t *res);
pow_res_t *pow_create_res(pow_t *p, pow_req_t *req);
void pow_destroy_res(pow_res_t *r);

