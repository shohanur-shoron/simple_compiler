
# Compiler Project Documentation

## 1. Project Overview

This document provides a detailed explanation of a simple compiler built in Python using the `ply` library. The compiler takes code written in a small, C-like language and translates it into x86 assembly code for the Linux environment.

The project demonstrates the classic stages of compilation, including lexical analysis, syntax analysis, intermediate code generation, and final assembly code generation. It also includes a robust error-handling mechanism for syntax errors and a comprehensive test suite.

## 2. Project Structure

The project is organized into several Python files, each responsible for a specific part of the compilation process:

- **`main.py`**: The main entry point for the compiler. It imports the test suites and orchestrates the compilation of each test case.

- **`test_cases.py`**: Contains the test suites for the compiler. It is separated into a `test_suite` for valid code that is expected to pass and an `error_suite` for invalid code that is expected to be caught by the error-handling mechanism.

- **`compiler.py`**: The core driver of the compiler. The `Compiler` class initializes all the necessary components (lexer, parser, etc.) and manages the overall pipeline for a given piece of source code.

- **`lexer.py`**: Implements the Lexical Analyzer. It uses `ply.lex` to break the source code text into a stream of tokens (e.g., keywords, identifiers, operators).

- **`parser.py`**: Implements the Syntax Analyzer and the first stage of code generation. It uses `ply.yacc` to parse the token stream according to the language's grammar. As it parses, it also generates Three-Address Code (TAC).

- **`codegen.py`**: A helper module for the intermediate code generation phase. It manages the creation of new temporary variables and labels for the TAC.

- **`assembly_gen.py`**: Implements the final code generation stage. It takes the Three-Address Code and translates it into x86 assembly language, managing register allocation in the process.

## 3. Supported Language Features

The compiler supports a subset of the C language with the following features:

- **Data Types**: Basic `int` declaration (`int x;`). The parser recognizes other types like `float` and `char`, but they are not fully supported in expressions or code generation.

- **Variables**: 32-bit integer variables.

- **Expressions**:
    - **Arithmetic Operators**: `+`, `-`, `*`, `/`, `%`.
    - **Operator Precedence**: Standard mathematical precedence is respected (e.g., `*` before `+`).
    - **Parentheses**: `()` can be used to override default precedence.
    - **Negative Numbers**: Unary minus is supported for assigning and using negative values (e.g., `x = -100;`).

- **Control Flow**:
    - **`if-else` Statements**: Supports `if` and `if-else` blocks for conditional logic.
    - **Relational Operators**: `==`, `!=`, `<`, `<=`, `>`, `>=`.
    - **`for` Loops**: C-style `for` loops with an initializer, a condition, and an increment step.

- **Code Structure**: Statements must be terminated by a semicolon `;`. Code blocks are enclosed in curly braces `{}`.

## 4. Compiler Architecture (The Pipeline)

The compilation process is divided into four main stages:

### Stage 1: Lexical Analysis (Lexing)
- **File**: `lexer.py`
- **Description**: The lexer is the first stage. It scans the raw source code string and converts it into a sequence of discrete tokens. For example, the code `x = 10;` is converted into `ID(x)`, `ASSIGN(=)`, `CONSTANT(10)`, `SEMICOLON(;)`. This process simplifies the next stage, as the parser can work with a structured sequence of tokens instead of raw text.

### Stage 2: Syntax Analysis (Parsing)
- **File**: `parser.py`
- **Description**: The parser takes the stream of tokens from the lexer and checks if they form a valid sequence according to the language's grammar rules. These rules are defined in the `p_*` functions within the `Parser` class. If the sequence is valid, the parser builds an internal representation of the code (a parse tree). This project uses a `precedence` table to correctly handle operator precedence and resolve ambiguities.

### Stage 3: Intermediate Code Generation (TAC)
- **Files**: `parser.py` (specifically the `generate_*` methods) and `codegen.py`.
- **Description**: As the parser validates the grammar, it simultaneously traverses the parse tree to generate a simpler, machine-independent representation of the code known as **Three-Address Code (TAC)**. TAC breaks down complex expressions into a sequence of simple instructions, each with at most three "addresses" (e.g., `t1 = x + y`). The `CodeGen` class assists this process by providing methods to create new temporary variables (`t1`, `t2`, ...) and unique labels for control flow (`L1`, `L2`, ...).

### Stage 4: Assembly Code Generation
- **File**: `assembly_gen.py`
- **Description**: This is the final stage, where the compiler translates the intermediate TAC into the target machine's assembly language (in this case, x86 for Linux).
    - **Register Allocation**: The `AssemblyGenerator` manages a pool of general-purpose registers (`eax`, `ebx`, etc.). It allocates registers for temporary variables from the TAC.
    - **Spilling**: When all registers are in use, it employs a round-robin strategy to "spill" a register, freeing it up for a new value. This was a critical bug-fix area, as the initial implementation was too simple and led to register value corruption.
    - **Instruction Mapping**: Each TAC instruction is mapped to one or more x86 assembly instructions. For example, `t3 = t1 + t2` is translated into a sequence of `mov` and `add` instructions.

## 5. Error Handling

- **Files**: `parser.py`, `compiler.py`
- **Mechanism**: The compiler features a robust mechanism to handle syntax errors.
    1. When the `ply.yacc` parser encounters a token that violates the language grammar, its `p_error` method is called.
    2. We have modified this method to raise a custom `SyntaxErrorFound` exception, which immediately halts the parsing process.
    3. The main `compile` method in the `Compiler` class wraps the call to the parser in a `try...except` block.
    4. If a `SyntaxErrorFound` exception is caught, it prints a clear "COMPILATION FAILED" message and stops processing that piece of code, preventing crashes or confusing output from later stages of the compiler.

## 6. How to Run

- **File**: `main.py`
- **Execution**: To run the compiler and its test suites, simply execute the main file:
  ```sh
  python main.py
  ```
- **Output**: The script will first run the `test_suite` from `test_cases.py`, which contains a wide variety of valid code snippets. For each, it will print the source code, the tokenization output, the generated TAC, and the final x86 assembly. After that, it will run the `error_suite`, demonstrating that the compiler correctly identifies and flags each piece of invalid code.

## 7. Future Improvements

This compiler provides a solid foundation, but many features could be added to enhance it:

- **Semantic Analysis**: Implement a symbol table to perform checks like:
    - Detecting the use of undeclared variables.
    - Preventing variable re-declaration in the same scope.
    - Type checking for expressions.
- **More Data Types**: Add full support for `float`, `char`, and other data types.
- **Functions**: Implement function declaration, function calls, and stack management.
- **More Control Flow**: Add `while` loops, `do-while` loops, and `switch` statements.
- **Code Optimization**: Introduce an optimization pass on the Three-Address Code, such as:
    - **Constant Folding**: Pre-calculate expressions with constant values at compile time (e.g., `2 + 3` becomes `5`).
    - **Dead Code Elimination**: Remove code that has no effect on the program's output.
- **Improved Register Allocation**: Move from a simple round-robin spilling strategy to a more intelligent algorithm based on liveness analysis.
