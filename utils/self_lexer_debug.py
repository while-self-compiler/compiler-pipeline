import sys
from colorama import Fore, Back, Style
from utils.utils import (
    merge_ewhile_files,
)
from utils.self_compiler import generate_ascii
from utils.wasm_runner import run_wasm
from utils.minimal_compiler import compile_to_wasm
from utils import config


def self_lexer_debug(filepath, inputs=None):
    """Run the self-compiler lexer in debug mode to analyze tokens.

    Compiles and runs the self-compiler lexer components with the provided file,
    displaying detailed information about the lexical analysis process and token structure.

    Args:
        filepath (str): Path to the file to be analyzed
        inputs (list, optional): List of input values for the program

    Returns:
        str: Output from the WASM execution
    """
    print(
        f"\n{Back.MAGENTA}{Fore.WHITE}{Style.BRIGHT} COMPILING SELF-COMPILER LEXER {Style.RESET_ALL}"
    )
    filepath_lexer = sys.path[0] + "/self_compiler/lexer.ewhile"
    filepath_lexer_debug = sys.path[0] + "/self_compiler/lexer_debug.ewhile"
    filepath_macros = sys.path[0] + "/self_compiler/macros.ewhile"

    # Combine macros.ewhile, lexer.ewhile and lexer_debug.ewhile files
    merged_lexer_filepath = merge_ewhile_files(
        [filepath_macros, filepath_lexer, filepath_lexer_debug]
    )
    wasm_filepath_compiler = compile_to_wasm(merged_lexer_filepath)

    print(
        f"\n{Back.CYAN}{Fore.BLACK}{Style.BRIGHT} RUNNING SELF-COMPILER LEXER {Style.RESET_ALL}"
    )
    if config.is_self_lexer:
        filepath = "out/self_compiler.while"
        print(
            f"{Fore.BLUE}Using generated file:{Style.RESET_ALL} {Fore.CYAN}{filepath}{Style.RESET_ALL}"
        )

    inputs = generate_ascii(filepath)

    print(
        f"{Fore.BLUE}Running with mode:{Style.RESET_ALL} {Fore.YELLOW}n3=3{Style.RESET_ALL}"
    )
    output = run_wasm(wasm_filepath_compiler, [inputs[0], inputs[1], "n3=3"])
    print(f"{Fore.GREEN}✓{Style.RESET_ALL} Lexical analysis completed successfully")

    # Parse the output which now contains separate printf statements
    parse_debug_output(output)

    return output


def parse_debug_output(output):
    """Parse the debug output which contains separate printf statements for each value.

    The output format is:
    printf: 1
    printf: {amountOfTokens}
    printf: 2
    printf: {tokenStream}
    printf: 3
    printf: {integerStream}
    printf: 4
    printf: {constantPool}

    Args:
        output (str): The output from the WASM execution
    """
    # Split output into lines and extract printf values
    lines = output.strip().split("\n")
    printf_values = []

    for line in lines:
        if line.startswith("printf: "):
            value_str = line[8:]  # Remove 'printf: ' prefix
            try:
                value = int(value_str)
                printf_values.append(value)
            except ValueError:
                # Skip non-numeric values
                continue

    if len(printf_values) < 8:  # We expect 8 values: 4 message numbers + 4 data values
        print(
            f"{Fore.RED}Warning: Expected 8 printf values, got {len(printf_values)}{Style.RESET_ALL}"
        )
        print(f"{Fore.YELLOW}Raw output:{Style.RESET_ALL}")
        print(output)
        return

    # Extract the values based on the expected pattern
    # msg=1, amountOfTokens, msg=2, tokenStream, msg=3, integerStream, msg=4, constantPool
    amount_of_tokens = printf_values[1]
    token_stream = printf_values[3]
    integer_stream = printf_values[5]
    constant_pool = printf_values[7]

    # Display the results
    print(
        f"\n{Back.GREEN}{Fore.BLACK}{Style.BRIGHT} LEXER DEBUG RESULTS {Style.RESET_ALL}"
    )

    print(f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} AMOUNT OF TOKENS {Style.RESET_ALL}")
    print(
        f"{Fore.CYAN}Number of tokens:{Style.RESET_ALL} {Fore.YELLOW}{amount_of_tokens}{Style.RESET_ALL}"
    )

    print(f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} TOKEN STREAM {Style.RESET_ALL}")
    print(
        f"{Fore.CYAN}Token stream value:{Style.RESET_ALL} {Fore.YELLOW}{token_stream}{Style.RESET_ALL}"
    )
    decode_token_stream(token_stream, amount_of_tokens)

    reassemble_number_blocks(integer_stream, "INTEGER STREAM")

    reassemble_number_blocks(constant_pool, "CONSTANT POOL")


def decode_token_stream(token_stream, num_tokens):
    """Decode the token stream to show individual tokens.

    Args:
        token_stream (int): The encoded token stream
        num_tokens (int): Number of tokens in the stream
    """
    # Token type mapping with syntax colors
    token_mapping = {
        0b00: f"{Fore.CYAN}WHILE{Style.RESET_ALL}",
        0b01: f"{Fore.CYAN}END{Style.RESET_ALL}",
        0b10: f"{Fore.YELLOW}+{Style.RESET_ALL}",
        0b11: f"{Fore.YELLOW}-{Style.RESET_ALL}",
    }

    tokens = []
    current_stream = token_stream

    # Extract tokens (each token is 2 bits)
    for i in range(num_tokens):
        token_bits = current_stream & 0b11  # Get last 2 bits
        current_stream = current_stream >> 2  # Shift right by 2 bits
        tokens.append(token_bits)

    # Reverse tokens since we extracted them backwards
    tokens.reverse()

    # Display tokens in a table
    print(
        f"\n{Fore.MAGENTA}{'INDEX':<8} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.MAGENTA}{'BINARY':<8} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.MAGENTA}{'TOKEN':<15}{Style.RESET_ALL}"
    )
    print(
        f"{Fore.MAGENTA}{'-' * 8} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.MAGENTA}{'-' * 8} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.MAGENTA}{'-' * 15}{Style.RESET_ALL}"
    )

    for i, token in enumerate(tokens):
        binary_str = f"{Fore.BLUE}{token:02b}{Style.RESET_ALL}"
        token_name = token_mapping.get(token, f"{Fore.RED}UNKNOWN{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}{i:<8}{Style.RESET_ALL} {Fore.MAGENTA}|{Style.RESET_ALL} {binary_str:<8}       {Fore.MAGENTA}|{Style.RESET_ALL} {token_name:<15}"
        )


def reassemble_number_blocks(encoded_number, label):
    """Decode and display encoded numerical values from 4-bit blocks.

    Takes an encoded number consisting of 4-bit blocks and reconstructs the original
    values, displaying them in a formatted table. Each block contains 3 bits of value
    and 1 bit indicating if it's the last block of a number.

    Args:
        encoded_number (int): The encoded number to decode
        label (str): Label to display in the section header

    Returns:
        list: List of reassembled values extracted from the encoded number
    """
    # Add colorful header for the section
    print(f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} {label} {Style.RESET_ALL}")
    print(
        f"{Fore.BLUE}Encoded value:{Style.RESET_ALL} {Fore.YELLOW}{encoded_number}{Style.RESET_ALL}"
    )

    reassembled_values = []
    all_blocks_info = []  # To store info about all blocks for summarized display
    blocks = []
    value_count = 0

    # Collect all blocks and reassembled values first
    while encoded_number != 0:
        block = encoded_number & 0b1111
        encoded_number = encoded_number >> 4
        blocks.append(block)

        # Store block info for later display
        bin_value = bin(block)[2:].zfill(4)  # Get binary and pad to 4 bits
        is_last_block = block & 0b1 == 0
        value_bits = (block >> 1) & 0b111  # Extract the 3 value bits

        # Add block info to collection
        all_blocks_info.append(
            {
                "block": block,
                "binary": bin_value,
                "is_last": is_last_block,
                "value_bits": value_bits,
                "value_index": value_count,
            }
        )

        if is_last_block:
            # Process the blocks in reverse order (from highest to lowest)
            current_value = 0
            shift = 0
            # Reverse the blocks list to process from highest to lowest
            blocks.reverse()
            for b in blocks:
                value_bits = (b >> 1) & 0b111  # Extract the 3 value bits
                current_value |= value_bits << shift
                shift += 3

            reassembled_values.append(current_value)
            blocks = []  # Reset for next number
            value_count += 1

    # Display consolidated table of reassembled values
    if reassembled_values:
        print(
            f"\n{Fore.MAGENTA}{'INDEX':<8} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.MAGENTA}{'VALUE':<15}{Style.RESET_ALL}"
        )
        print(
            f"{Fore.MAGENTA}{'-' * 8} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.MAGENTA}{'-' * 15}{Style.RESET_ALL}"
        )
        for i, value in enumerate(reassembled_values):
            print(
                f"{Fore.CYAN}{i:<8}{Style.RESET_ALL} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.GREEN}{value:<15}{Style.RESET_ALL}"
            )

    # Only show block details if requested (disabled by default to keep output clean)
    show_blocks = False
    if show_blocks and all_blocks_info:
        print(
            f"\n{Fore.BLUE}{Style.BRIGHT}Detailed block information:{Style.RESET_ALL}"
        )
        print(
            f"\n{Fore.MAGENTA}{'VALUE#':<8} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.MAGENTA}{'BLOCK#':<8} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.MAGENTA}{'BINARY':<12} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.MAGENTA}{'IS_LAST':<10} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.MAGENTA}{'VALUE':<10}{Style.RESET_ALL}"
        )
        print(
            f"{Fore.MAGENTA}{'-' * 8} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.MAGENTA}{'-' * 8} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.MAGENTA}{'-' * 12} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.MAGENTA}{'-' * 10} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.MAGENTA}{'-' * 10}{Style.RESET_ALL}"
        )

        for i, block_info in enumerate(all_blocks_info):
            bin_prefix = block_info["binary"][0:3]
            bin_suffix = block_info["binary"][3]
            is_last_text = (
                f"{Fore.GREEN}Yes{Style.RESET_ALL}"
                if block_info["is_last"]
                else f"{Fore.RED}No{Style.RESET_ALL}"
            )
            print(
                f"{Fore.YELLOW}{block_info['value_index']:<8}{Style.RESET_ALL} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.CYAN}{i:<8}{Style.RESET_ALL} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.YELLOW}{bin_prefix}{Style.RESET_ALL}{Fore.RED}{bin_suffix}{Style.RESET_ALL}{' ' * 7} {Fore.MAGENTA}|{Style.RESET_ALL} {is_last_text:<10} {Fore.MAGENTA}|{Style.RESET_ALL} {Fore.GREEN}{block_info['value_bits']:<10}{Style.RESET_ALL}"
            )

    return reassembled_values
