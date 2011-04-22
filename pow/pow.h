#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>

typedef struct {
    uint32_t *perm_table;
    uint16_t rand[3];
    uint16_t seed[3];
    uint32_t size;
    uint32_t n;
    uint32_t m;
    uint32_t l;
} pow_t;

typedef struct {
    uint32_t seed[3];
    uint32_t x0;
    uint32_t check;
    uint32_t n;
    uint32_t l;
    uint32_t *v, *w;
} pow_req_t;

pow_t *pow_create(size_t n, size_t l, uint64_t seed);
void pow_destroy(pow_t *p);
pow_req_t *pow_create_req(pow_t *p);
void pow_destroy_req(pow_req_t *r);

