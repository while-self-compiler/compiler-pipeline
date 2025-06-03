typedef struct Node
{
    unsigned int value;
    struct Node *next;
} Node;

#include <stddef.h>
#include <stdint.h>
#include <limits.h>

#ifdef TEST

#include <stdio.h>
#include <stdlib.h>

Node *allocate()
{
    Node *node = (Node *)malloc(sizeof(Node));
    if (node == NULL)
    {
        fprintf(stderr, "Failed to allocate memory\n");
        exit(1);
    }

    // Initialize to zero
    node->value = 0;
    node->next = NULL;

    return node;
}

#else

#define PAGE_SIZE 65536
extern unsigned char __heap_base;
// Properly declare printjs as a WebAssembly import
extern void printjs(unsigned int) __attribute__((import_module("env"), import_name("printjs")));
Node *head = (Node *)&__heap_base;

unsigned int get_memory_size()
{
    unsigned int size;
    __asm__("memory.size 0\n"
            "local.set %0"
            : "=r"(size)::"memory");
    return size * PAGE_SIZE;
}

unsigned int grow_memory_by_one_page()
{
    unsigned int previous_size;
    __asm__("i32.const 1\n"
            "memory.grow 0\n"
            "local.set %0"
            : "=r"(previous_size)::"memory");
    return previous_size;
}

Node *allocate()
{
    Node *node = head;
    head += sizeof(Node);

    if ((unsigned int)head >= get_memory_size())
        grow_memory_by_one_page();

    // printjs((unsigned int)node);
    return node;
}

#endif

unsigned int get_value(Node *node)
{
    return node->value;
}

void set_value(Node *node, unsigned int value)
{
    node->value = value;
}

Node *get_next(Node *node)
{
    return node->next;
}

void set_next(Node *node, Node *next)
{
    node->next = next;
}

Node *create_chunk(unsigned int value)
{
    Node *node = allocate();
    node->value = value;
    return node;
}

unsigned int is_gt(Node *a, Node *b)
{
    Node *a_current = a;
    Node *b_current = b;
    unsigned int is_gt = 0;
    while (a_current != 0 || b_current != 0)
    {
        unsigned int a_value = (a_current != 0) ? a_current->value : 0;
        unsigned int b_value = (b_current != 0) ? b_current->value : 0;
        if (a_value > b_value)
        {
            is_gt = 1;
        }
        else if (a_value < b_value)
        {
            is_gt = 0;
        }
        a_current = (a_current != 0) ? a_current->next : 0;
        b_current = (b_current != 0) ? b_current->next : 0;
    }
    return is_gt;
}

void set_to_zero(Node *node)
{
    Node *current = node;
    while (current != 0)
    {
        current->value = 0;
        current = current->next;
    }
}

void copy(Node *dest, Node *src)
{
    Node *dest_current = dest;
    Node *src_current = src;

    set_to_zero(dest);

    while (src_current != 0)
    {
        dest_current->value = src_current->value;
        src_current = src_current->next;
        if (src_current != 0)
        {
            if (dest_current->next == 0)
            {
                dest_current->next = allocate();
            }
            dest_current = dest_current->next;
        }
    }
}

unsigned int is_equal(Node *a, Node *b)
{
    Node *a_current = a;
    Node *b_current = b;

    while (a_current != 0 || b_current != 0)
    {
        unsigned int a_value = (a_current != 0) ? a_current->value : 0;
        unsigned int b_value = (b_current != 0) ? b_current->value : 0;

        if (a_value != b_value)
        {
            return 0; // Not equal
        }

        a_current = (a_current != 0) ? a_current->next : 0;
        b_current = (b_current != 0) ? b_current->next : 0;
    }
    return 1; // Equal
}

unsigned int get_length(Node *node)
{
    unsigned int length = 0;
    Node *current = node;

    while (current != 0)
    {
        length++;
        current = current->next;
    }
    return length;
}

// a = b + c
void add(Node *a, Node *b, Node *c)
{
    unsigned int carry = 0;
    Node *b_current = b;
    Node *c_current = c;
    Node *a_current = a;
    unsigned int b_value, c_value, sum;

    if (a != b && a != c)
    {
        set_to_zero(a);
    }

    while (b_current != 0 || c_current != 0 || carry != 0)
    {
        // Get values from b and c, or use 0 if no more blocks
        b_value = (b_current != 0) ? b_current->value : 0;
        c_value = (c_current != 0) ? c_current->value : 0;

        // Calculate the sum with carry
        sum = b_value + c_value + carry;

        // Handle overflow
        if (sum < b_value || (sum == b_value && c_value > 0))
        {
            carry = 1;
        }
        else
        {
            carry = 0;
        }

        // Store the sum in a
        a_current->value = sum;

        // Move to next blocks in b and c
        if (b_current != 0)
        {
            b_current = b_current->next;
        }
        if (c_current != 0)
        {
            c_current = c_current->next;
        }

        // If we need more blocks in a, allocate a new one
        if ((b_current != 0 || c_current != 0 || carry != 0) && a_current->next == 0)
        {
            a_current->next = allocate();
        }

        // Move to the next block in a
        a_current = a_current->next;
    }
}

// a = b - c
void sub(Node *a, Node *b, Node *c)
{
    unsigned int borrow = 0;
    Node *b_current = b;
    Node *c_current = c;
    Node *a_current = a;
    unsigned int b_value, c_value, diff;

    if (is_gt(c, b))
    {
        set_to_zero(a);
        return;
    }

    if (a != b && a != c)
    {
        set_to_zero(a);
    }

    while (b_current != 0 || c_current != 0)
    {
        // Get values from b and c, or use 0 if no more blocks
        b_value = (b_current != 0) ? b_current->value : 0;
        c_value = (c_current != 0) ? c_current->value : 0;

        // Adjust for borrow
        if (borrow)
        {
            if (b_value > 0)
            {
                b_value--;
                borrow = 0;
            }
            else
            {
                b_value = 0xFFFFFFFF; // 2^32 - 1
                borrow = 1;
            }
        }

        // Calculate the difference and set borrow if needed
        if (b_value < c_value)
        {
            diff = (0x100000000 + b_value) - c_value; // 2^32 + b_value - c_value
            borrow = 1;
        }
        else
        {
            diff = b_value - c_value;
        }

        // Store the result in a
        a_current->value = diff;

        // Move to next blocks
        if (b_current != 0)
        {
            b_current = b_current->next;
        }
        if (c_current != 0)
        {
            c_current = c_current->next;
        }

        // If we need more blocks in a, allocate a new one
        if ((b_current != 0 || c_current != 0) && a_current->next == 0)
        {
            a_current->next = allocate();
        }

        // Move to the next block in a
        a_current = a_current->next;
    }
}

unsigned int get_highest_bit(Node *node)
{
    Node *current = node;
    unsigned int node_nr = 0;
    unsigned int highest_bit = 0;

    while (current != NULL)
    {
        unsigned int value = current->value;
        unsigned int bit_position = 0;

        while (value > 0)
        {
            if (value & 1)
            {
                highest_bit = node_nr * 32 + bit_position;
            }
            value >>= 1;
            bit_position++;
        }

        current = current->next;
        node_nr++;
    }
    return highest_bit;
}

// Returns the 0-indexed bit position if node represents a power of two,
// otherwise returns UINT_MAX.
unsigned int get_single_set_bit_position(Node *node)
{
    if (node == NULL)
        return UINT_MAX;

    Node *current = node;
    unsigned int overall_bit_pos = UINT_MAX;
    unsigned int current_node_idx = 0;
    int found_set_bit_in_any_node = 0;

    while (current != NULL)
    {
        if (current->value != 0)
        {
            if ((current->value & (current->value - 1)) != 0)
            {
                return UINT_MAX;
            }
            if (found_set_bit_in_any_node)
            {
                return UINT_MAX;
            }

            found_set_bit_in_any_node = 1;
            unsigned int local_bit_pos = 0;
            unsigned int val = current->value;
            while ((val & 1) == 0 && val != 0)
            {
                val >>= 1;
                local_bit_pos++;
            }

            overall_bit_pos = (current_node_idx * 32) + local_bit_pos;
        }
        current = current->next;
        current_node_idx++;
    }

    if (!found_set_bit_in_any_node)
    {
        return UINT_MAX;
    }

    return overall_bit_pos;
}

void right_shift(Node *output, Node *input, Node *shift)
{
    if (get_highest_bit(shift) > 34)
    {
        set_to_zero(output);
        return;
    }

    unsigned int shift_low = shift->value;
    unsigned int shift_high = shift->next ? shift->next->value : 0;
    uint64_t shift_value = ((uint64_t)shift_high << 32) | shift_low;

    if (get_highest_bit(input) < shift_value)
    {
        set_to_zero(output);
        return;
    }

    unsigned int read_bit_nr = shift_value % 32;
    unsigned int read_node_nr = shift_value / 32;
    unsigned int write_bit_nr = 0;

    Node *input_current = input;
    Node *output_current = output;

    for (unsigned int i = 0; i < read_node_nr; i++)
    {
        input_current = input_current->next;
    }

    while (input_current != NULL)
    {
        unsigned int read_value = (input_current->value >> read_bit_nr) & 1;
        output_current->value &= ~(1 << write_bit_nr);
        output_current->value |= (read_value << write_bit_nr);

        read_bit_nr++;
        write_bit_nr++;

        if (read_bit_nr == 32)
        {
            read_bit_nr = 0;
            input_current = input_current->next;
        }

        if (write_bit_nr == 32)
        {
            write_bit_nr = 0;
            if ((output_current->next == NULL) & (input_current != NULL))
            {
                output_current->next = allocate();
            }
            output_current = output_current->next;
        }
    }

    if (output_current != NULL)
    {
        output_current->value &= (1 << write_bit_nr) - 1;
        output_current = output_current->next;
    }
    while (output_current != NULL)
    {
        output_current->value = 0;
        output_current = output_current->next;
    }
}

void left_shift_u64(Node *output, Node *input, uint64_t shift)
{
    // Static temporary node for calculation
    static Node *temp = NULL;

    // Initialize temp node if needed
    if (temp == NULL)
    {
        temp = allocate();
    }

    // Clear the temporary result node
    set_to_zero(temp);

    uint64_t shift_value = shift;

    // Calculate write position
    unsigned int write_bit_nr = shift_value % 32;
    unsigned int write_node_nr = shift_value / 32;

    // Navigate to the correct output node
    Node *output_current = temp;
    for (unsigned int i = 0; i < write_node_nr; i++)
    {
        if (output_current->next == NULL)
        {
            output_current->next = allocate();
        }
        output_current = output_current->next;
    }

    // Process input node by node, bit by bit
    Node *input_current = input;
    unsigned int read_bit_nr = 0;

    while (input_current != NULL)
    {
        unsigned int read_value = (input_current->value >> read_bit_nr) & 1;

        // Write the bit to output
        output_current->value |= (read_value << write_bit_nr);

        read_bit_nr++;
        write_bit_nr++;

        if (read_bit_nr == 32)
        {
            read_bit_nr = 0;
            input_current = input_current->next;
        }

        if (write_bit_nr == 32)
        {
            write_bit_nr = 0;
            if (output_current->next == NULL)
            {
                output_current->next = allocate();
            }
            output_current = output_current->next;
        }
    }

    // Copy the result from temp to output
    copy(output, temp);
}

void left_shift(Node *output, Node *input, Node *shift)
{
    unsigned int shift_low = shift->value;
    unsigned int shift_high = shift->next ? shift->next->value : 0;
    uint64_t shift_value = ((uint64_t)shift_high << 32) | shift_low;

    left_shift_u64(output, input, shift_value);
}

void set_length(Node *node, unsigned int length)
{
    Node *current = node;
    unsigned int count = 1;

    while (count < length)
    {
        if (current->next == NULL)
        {
            current->next = allocate();
        }
        current = current->next;
        count++;
    }
}

unsigned int get_bit(Node *node, uint64_t bit)
{
    unsigned int node_nr = bit / 32;
    unsigned int bit_nr = bit % 32;
    Node *current = node;

    for (unsigned int i = 0; i < node_nr; i++)
    {
        if (current == NULL)
        {
            return 0;
        }
        current = current->next;
    }

    if (current == NULL)
    {
        return 0;
    }

    return (current->value >> bit_nr) & 1;
}

void mul(Node *output, Node *a, Node *b)
{
    static Node *output_buffer = NULL;
    static Node *temp = NULL;

    // Optimization: if one of the operands is a power of two, use left_shift_u64
    unsigned int a_bit_pos = get_single_set_bit_position(a);
    unsigned int b_bit_pos = get_single_set_bit_position(b);

    if (a_bit_pos != UINT_MAX)
    {
        if (a_bit_pos == 0)
        {
            copy(output, b);
            return;
        }

        left_shift_u64(output, b, a_bit_pos);
        return;
    }

    if (b_bit_pos != UINT_MAX)
    {
        if (b_bit_pos == 0)
        {
            copy(output, a);
            return;
        }
        left_shift_u64(output, a, b_bit_pos);
        return;
    }

    if (output_buffer == NULL)
    {
        output_buffer = allocate();
    }
    if (temp == NULL)
    {
        temp = allocate();
    }

    set_to_zero(output_buffer);
    set_to_zero(temp);
    unsigned int a_length = get_length(a);
    unsigned int b_length = get_length(b);
    unsigned int output_length = a_length + b_length;
    set_length(output_buffer, output_length);
    set_length(temp, output_length);

    if (a_length < b_length)
    {
        Node *temp_node = a;
        a = b;
        b = temp_node;
    }

    for (uint64_t i = 0; i <= get_highest_bit(b); i++)
    {
        unsigned int bit = get_bit(b, i);
        if (bit == 1)
        {
            copy(temp, a);
            left_shift_u64(temp, temp, i);
            add(output_buffer, output_buffer, temp);
        }
    }
    copy(output, output_buffer);
}

void big_div(Node *output, Node *a, Node *b)
{
    static Node *remainder = NULL;
    static Node *divisor = NULL;
    static Node *temp = NULL;
    static Node *quotient = NULL;

    // Allocate static nodes if needed
    if (remainder == NULL)
        remainder = allocate();
    if (divisor == NULL)
        divisor = allocate();
    if (temp == NULL)
        temp = allocate();
    if (quotient == NULL)
        quotient = allocate();

    // Clear all nodes
    set_to_zero(remainder);
    set_to_zero(divisor);
    set_to_zero(temp);
    set_to_zero(quotient);

    // Check for division by zero
    if (b->value == 0 && b->next == NULL)
    {
        // Handle division by zero - set output to zero
        set_to_zero(output);
        return;
    }

    // Optimization: if b is a power of two, division is a right shift
    unsigned int b_bit_pos = get_single_set_bit_position(b);
    if (b_bit_pos != UINT_MAX)
    {
        if (b_bit_pos == 0)
        {
            copy(output, a);
            return;
        }

        static Node *static_shift_amount_node = NULL;
        if (static_shift_amount_node == NULL)
        {
            static_shift_amount_node = allocate();
        }
        static_shift_amount_node->value = b_bit_pos;

        right_shift(output, a, static_shift_amount_node);
        return;
    }

    // If a < b, result is 0
    if (is_gt(b, a))
    {
        set_to_zero(output);
        return;
    }

    // If a == b, result is 1
    if (is_equal(a, b))
    {
        set_to_zero(output);
        output->value = 1;
        return;
    }

    // Make sure remainder can hold a
    unsigned int a_length = get_length(a);
    set_length(remainder, a_length);

    // Make sure quotient can hold potential result (at most same length as a)
    set_length(quotient, a_length);

    // Copy a to remainder
    copy(remainder, a);

    // Get the highest bits
    unsigned int a_highest_bit = get_highest_bit(a);
    unsigned int b_highest_bit = get_highest_bit(b);

    // Main division loop
    // We'll shift b left and then do subtractions
    int shift_amount = a_highest_bit - b_highest_bit;

    while (shift_amount >= 0)
    {
        // Shift b left by shift_amount
        copy(divisor, b);
        left_shift_u64(divisor, divisor, shift_amount);

        // If remainder >= divisor, subtract and set bit in quotient
        if (!is_gt(divisor, remainder))
        {
            sub(remainder, remainder, divisor);

            // Set the corresponding bit in the quotient
            set_to_zero(temp);
            temp->value = 1;
            left_shift_u64(temp, temp, shift_amount);
            add(quotient, quotient, temp);
        }

        shift_amount--;
    }

    // Copy the result to output
    copy(output, quotient);
}

void mod(Node *output, Node *a, Node *b)
{
    static Node *quotient = NULL;
    static Node *product = NULL;
    static Node *remainder = NULL;

    if (quotient == NULL)
        quotient = allocate();
    if (product == NULL)
        product = allocate();
    if (remainder == NULL)
        remainder = allocate();

    set_to_zero(quotient);
    set_to_zero(product);
    set_to_zero(remainder);

    // Optimization: if b is a power of two, a % b is a bitwise AND with (b-1)
    unsigned int b_bit_pos = get_single_set_bit_position(b);
    if (b_bit_pos != UINT_MAX)
    {
        if (b_bit_pos == 0)
        {
            set_to_zero(output);
            return;
        }

        copy(output, a);

        unsigned int cutoff_node_idx = b_bit_pos / 32;
        unsigned int cutoff_bit_in_node = b_bit_pos % 32;

        Node *current_out = output;
        unsigned int current_node_num = 0;
        while (current_out != NULL)
        {
            if (current_node_num > cutoff_node_idx)
            {
                current_out->value = 0;
            }
            else if (current_node_num == cutoff_node_idx)
            {
                if (cutoff_bit_in_node == 0)
                {
                    current_out->value = 0;
                }
                else
                {
                    unsigned int mask = (1U << cutoff_bit_in_node) - 1;
                    current_out->value &= mask;
                }
            }
            current_out = current_out->next;
            current_node_num++;
        }
        return;
    }

    // a % b = a - (a / b) * b
    big_div(quotient, a, b);
    mul(product, quotient, b);
    sub(remainder, a, product);

    copy(output, remainder);
}
