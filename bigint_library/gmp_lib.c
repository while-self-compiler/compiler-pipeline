#include <gmp.h>
#include <stddef.h>
#include <stdint.h>
#include <limits.h>
#include <stdlib.h>

#ifdef TEST
#define EMSCRIPTEN_KEEPALIVE
#include <stdio.h>
#else
#include <emscripten.h>
#endif

// Global variables for bigint construction from u32 blocks
static mpz_t *current_bigint = NULL;
static unsigned int shift = 0;

// Helper function to print mpz_t value (for TEST mode only)
#ifdef TEST
void print_mpz_value(mpz_t *bigint, const char *label)
{
    char *str = mpz_get_str(NULL, 10, *bigint);
    printf("%s: %s\n", label, str);
    free(str);
}
#endif

// Create a new bigint, save it globally, and reset shift to 0
EMSCRIPTEN_KEEPALIVE
mpz_t *create_bigint()
{
    // Allocate new bigint
    current_bigint = malloc(sizeof(mpz_t));
    if (current_bigint == NULL)
        return NULL;

    mpz_init(*current_bigint);
    mpz_set_ui(*current_bigint, 0);
    shift = 0;

    return current_bigint;
}

// Push a u32 value into the current bigint at the current shift position
EMSCRIPTEN_KEEPALIVE
void push_u32_to_bigint(uint32_t value)
{
    if (current_bigint == NULL)
        return;

    // Create a temporary mpz_t for the value
    mpz_t temp_value, shifted_value;
    mpz_init(temp_value);
    mpz_init(shifted_value);

    // Set the temp value to the u32 input
    mpz_set_ui(temp_value, value);

    // Shift the value left by the current shift amount
    mpz_mul_2exp(shifted_value, temp_value, shift);

    // Add the shifted value to the current bigint
    mpz_add(*current_bigint, *current_bigint, shifted_value);

    // Increase shift by 32 for next u32 block
    shift += 32;

    // Clean up temporary variables
    mpz_clear(temp_value);
    mpz_clear(shifted_value);
}

// Helper function to create a bigint and initialize it with a value
EMSCRIPTEN_KEEPALIVE
mpz_t *create_bigint_with_value(uint32_t value)
{
    mpz_t *bigint = create_bigint();
    if (bigint != NULL)
    {
        push_u32_to_bigint(value);
    }
    return bigint;
}

// Comparison function: returns 1 if a > b, 0 otherwise
EMSCRIPTEN_KEEPALIVE
unsigned int is_gt(mpz_t *a, mpz_t *b)
{
    return mpz_cmp(*a, *b) > 0 ? 1 : 0;
}

// Set number to zero
EMSCRIPTEN_KEEPALIVE
void set_to_zero(mpz_t *num)
{
    mpz_set_ui(*num, 0);
}

// Copy src to dest
EMSCRIPTEN_KEEPALIVE
void copy(mpz_t *dest, mpz_t *src)
{
    mpz_set(*dest, *src);
}

// Equality check: returns 1 if a == b, 0 otherwise
EMSCRIPTEN_KEEPALIVE
unsigned int is_equal(mpz_t *a, mpz_t *b)
{
    return mpz_cmp(*a, *b) == 0 ? 1 : 0;
}

// Addition: a = b + c
EMSCRIPTEN_KEEPALIVE
void add(mpz_t *a, mpz_t *b, mpz_t *c)
{
    mpz_add(*a, *b, *c);
}

// Subtraction: a = b - c
EMSCRIPTEN_KEEPALIVE
void sub(mpz_t *a, mpz_t *b, mpz_t *c)
{
    if (mpz_cmp(*b, *c) < 0)
    {
        mpz_set_ui(*a, 0);
        return;
    }
    mpz_sub(*a, *b, *c);

    // Ensure result is not negative
    if (mpz_cmp_ui(*a, 0) < 0)
    {
        mpz_set_ui(*a, 0);
    }
}

// Right shift: output = input >> shift
EMSCRIPTEN_KEEPALIVE
void right_shift(mpz_t *output, mpz_t *input, mpz_t *shift)
{
    if (mpz_cmp_ui(*shift, ULONG_MAX) > 0)
    {
        mpz_set_ui(*output, 0);
        return;
    }

    unsigned long shift_amount = mpz_get_ui(*shift);
    mpz_fdiv_q_2exp(*output, *input, shift_amount);
}

// Left shift: output = input << shift
EMSCRIPTEN_KEEPALIVE
void left_shift(mpz_t *output, mpz_t *input, mpz_t *shift)
{
    if (mpz_cmp_ui(*shift, ULONG_MAX) > 0)
    {
        // For very large shifts, result would be huge, set to zero for safety
        mpz_set_ui(*output, 0);
        return;
    }

    unsigned long shift_amount = mpz_get_ui(*shift);
    mpz_mul_2exp(*output, *input, shift_amount);
}

// Multiplication: output = a * b
EMSCRIPTEN_KEEPALIVE
void mul(mpz_t *output, mpz_t *a, mpz_t *b)
{
    mpz_mul(*output, *a, *b);
}

// Division: output = a / b
EMSCRIPTEN_KEEPALIVE
void big_div(mpz_t *output, mpz_t *a, mpz_t *b)
{
    if (mpz_cmp_ui(*b, 0) == 0)
    {
        mpz_set_ui(*output, 0);
        return;
    }
    mpz_fdiv_q(*output, *a, *b);
}

// Modulo: output = a % b
EMSCRIPTEN_KEEPALIVE
void mod(mpz_t *output, mpz_t *a, mpz_t *b)
{
    if (mpz_cmp_ui(*b, 0) == 0)
    {
        mpz_set_ui(*output, 0);
        return;
    }
    mpz_mod(*output, *a, *b);
}

// Convert a bigint to string representation
// Returns a newly allocated string that must be freed by the caller
EMSCRIPTEN_KEEPALIVE
uint32_t read_bigint(mpz_t *bigint)
{
    current_bigint = bigint;
    uint32_t length = mpz_sizeinbase(*bigint, 2);
    length = (length + 31) / 32;
    shift = 0;
    return length;
}

// Get the next u32 block from the current bigint at the current shift position
// Does not modify the bigint, only reads from it and advances the shift
EMSCRIPTEN_KEEPALIVE
uint32_t get_next_u32()
{
    if (current_bigint == NULL)
        return 0;

    // Create temporary variables for extraction
    mpz_t temp_shifted, mask;
    mpz_init(temp_shifted);
    mpz_init(mask);

    // Right shift the bigint by the current shift amount to get the desired block at position 0
    mpz_fdiv_q_2exp(temp_shifted, *current_bigint, shift);

    // Create a mask for the lower 32 bits (0xFFFFFFFF)
    mpz_set_ui(mask, 0xFFFFFFFF);

    // Extract only the lower 32 bits
    mpz_and(temp_shifted, temp_shifted, mask);

    // Convert to uint32_t
    uint32_t result = 0;
    if (mpz_fits_ulong_p(temp_shifted))
    {
        result = (uint32_t)mpz_get_ui(temp_shifted);
    }

    // Advance shift by 32 for next block
    shift += 32;

    // Clean up temporary variables
    mpz_clear(temp_shifted);
    mpz_clear(mask);

    return result;
}

// Free a previously allocated mpz_t bigint
EMSCRIPTEN_KEEPALIVE
void free_bigint(mpz_t *num)
{
    if (num != NULL)
    {
        mpz_clear(*num);
        free(num);
    }
}
