#define TEST
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "gmp_lib.c"

int main()
{
    clock_t start = clock();

    mpz_t *x0 = create_bigint_with_value(42);
    mpz_t *shift = create_bigint_with_value(8);
    mpz_t *counter = create_bigint_with_value(50000);

    mpz_t *one = create_bigint_with_value(1);
    mpz_t *zero = create_bigint_with_value(0);

    while (is_gt(counter, zero))
    {
        left_shift(x0, x0, shift);

        sub(counter, counter, one);
    }

    set_to_zero(counter);
    mpz_set_ui(*counter, 49999);

    while (is_gt(counter, zero))
    {
        right_shift(x0, x0, shift);

        sub(counter, counter, one);
    }

    clock_t end = clock();
    double cpu_time_used = ((double)(end - start)) / CLOCKS_PER_SEC;

    print_mpz_value(x0, "Result");
    printf("C implementation execution time: %f seconds\n", cpu_time_used);

    free_bigint(x0);
    free_bigint(shift);
    free_bigint(counter);
    free_bigint(one);
    free_bigint(zero);

    return 0;
}
