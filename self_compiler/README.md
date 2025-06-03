# WHILE Self-Compiler

This is a self-compiler for the WHILE language that generates WebAssembly (WASM) binary code.

## Overview

The compiler consists of the following components:

- **lexer.ewhile**: Tokenizes the source code and produces token streams
- **generator.ewhile**: Parses tokens and generates WASM binary code
- **macros.ewhile**: Contains shared macros used by both lexer and generator

## Tokenization

Tokenclasses:
1. while | 00 | 1 Lookup
2. end   | 01 | 0 Lookup
3. +     | 10 | 3 Lookup
4. -     | 11 | 3 Lookup

## Example Programs

### Example 1:
```
while x4 > 0 do
    x3 = x3 + 1;
    x4 = x4 - 1
end;
x0 = x3 + 0
```

Tokenised: 
while + - end +

Integerised:
start(000 1 (Magic Number)) 4 3 3 1 4 4 1 0 3 0

Tokenstream Reversed: n1 = 632 (10 01 11 10 00)
Integerstream Reversed: n2 = 1125323908712 (1 000 0 011 0 000 0 001 0 100 0 100 0 001 0 011 0 011 0 100 0) 
Amount of tokens: n3 = 5
Highest i for x_i: 4 (x4)
Constantpool Reversed: 288 (1 001 0 000 0)

### Example 2:
```
x0 = x3 + 0
```

n1 = 2 (10)
n2 = 4192 (1 000 0 011 0 000 0)
n3 = 1
n4 = 16 (1 000 0)

## Optimisations

The compiler includes a two-variable code optimizer that replaces patterns like:

```
while x1 > 0 do
    x2 = x2 op 1;
    x1 = x1 - 1
end
```

or

```
while x1 > 0 do
    x1 = x1 - 1;
    x2 = x2 op 1
end
```

with op = + or -

with the following optimized code:
```
x2 = x2 + x1;
x1 = x1 - x1; (x1 = 0)
```
