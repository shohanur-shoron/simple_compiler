# test_cases.py

test_suite = [
    # 1. Basic Assignments
    ("Assignment: Simple", "int x; x = 10;"),
    ("Assignment: Simple Expression", "int y; y = 5 + 3;"),
    ("Assignment: Negative Value", "int z; z = -100;"),

    # 2. Operator Tests
    ("Operators: Precedence 1", "int a; a = 10 + 5 * 2;"), # Expected: 20
    ("Operators: Precedence 2 (Parens)", "int b; b = (10 + 5) * 2;"), # Expected: 30
    ("Operators: Subtraction Order", "int c; c = 20 - 10 - 5;"), # Expected: 5
    ("Operators: Division", "int d; d = 20 / 4;"), # Expected: 5
    ("Operators: Modulo", "int e; e = 21 % 4;"), # Expected: 1
    ("Operators: All", "int f; f = (10 + (20 / 2)) * 3 - 5 % 3;"), # Expected: (10+10)*3 - 2 = 58

    # 3. Conditional Logic (if-else)
    ("Conditionals: Simple If (True)", "int g; g = 10; if (g > 5) { g = 1; }"), # Expected: 1
    ("Conditionals: Simple If (False)", "int h; h = 10; if (h < 5) { h = 1; }"), # Expected: 10
    ("Conditionals: If-Else (If path)", "int i; i = 10; if (i == 10) { i = 100; } else { i = 200; }"), # Expected: 100
    ("Conditionals: If-Else (Else path)", "int j; j = 10; if (j != 10) { j = 100; } else { j = 200; }"), # Expected: 200
    ("Conditionals: Negative Condition (True)", "int k; k = -5; if (k < 0) { k = 99; }"), # Expected: 99
    ("Conditionals: Negative Condition (False)", "int l; l = -5; if (l > 0) { l = 99; } else { l = -99; }"), # Expected: -99

    # 4. Loop Logic (for)
    ("Loops: Simple For", """
        int m; 
        m = 0;
        int i;
        for (i = 0; i < 5; i = i + 1) {
            m = m + 2;
        }
    """), # Expected: 10
    ("Loops: Nested For", """
        int n;
        n = 0;
        int i;
        int j;
        for (i = 0; i < 3; i = i + 1) {
            for (j = 0; j < 3; j = j + 1) {
                n = n + 1;
            }
        }
    """), # Expected: 9
    ("Loops: For with If", """
        int o;
        o = 0;
        int i;
        for (i = 1; i <= 4; i = i + 1) {
            if ((i % 2) == 0) {
                o = o + i;
            }
        }
    """), # Expected: 2 + 4 = 6

    # 5. Edge Cases
    ("Edge Case: Loop That Does Not Run", """
        int p;
        p = 100;
        int i;
        for (i = 0; i < 0; i = i + 1) {
            p = 99;
        }
    """), # Expected: 100
    ("Edge Case: Uninitialized Variable Use", """
        int q;
        int r;
        r = q + 5;
    """), # Expected: 5 (since q defaults to 0)
]


error_suite = [
    ("Error: Missing Semicolon", "int a; a = 10"),
    ("Error: Mismatched Parenthesis", "int b; b = (5 + 3;"),
    ("Error: Invalid Operator Placement", "int c; c = 5 + * 3;"),
    ("Error: Invalid Assignment Target", "int d; 5 = d;"),
]
