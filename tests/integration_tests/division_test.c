#define TEST
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "gmp_lib.c"

int main()
{
    clock_t start = clock();

    mpz_t *x0 = create_bigint_with_value(13);
    mpz_t *operand = create_bigint_with_value(17);
    mpz_t *divCounter = create_bigint_with_value(100000);
    mpz_t *modValue = create_bigint_with_value(1);
    mpz_mul_2exp(*modValue, *modValue, 32); // 2^32
    mpz_t *shift = create_bigint_with_value(500000);

    mpz_t *one = create_bigint_with_value(1);
    mpz_t *zero = create_bigint_with_value(0);

    // Shift x0 left by 500000 bits
    mpz_mul_2exp(*x0, *x0, 500000);

    // Divide by operand 100000 times
    while (is_gt(divCounter, zero))
    {
        big_div(x0, x0, operand);

        sub(divCounter, divCounter, one);
    }

    mod(x0, x0, modValue);

    clock_t end = clock();
    double cpu_time_used = ((double)(end - start)) / CLOCKS_PER_SEC;

    print_mpz_value(x0, "Result");
    printf("C implementation execution time: %f seconds\n", cpu_time_used);

    free_bigint(x0);
    free_bigint(operand);
    free_bigint(divCounter);
    free_bigint(modValue);
    free_bigint(shift);
    free_bigint(one);
    free_bigint(zero);

    return 0;
}
