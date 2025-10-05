from compiler import Compiler
from test_cases import test_suite, error_suite

def run_tests():
    compiler = Compiler()
    
    print("\n" + "=" * 20 + " RUNNING PASSING TESTS " + "=" * 20)
    tests = test_suite
    for name, code in tests:
        print("\n" + "#" * 50)
        print(f"TEST: {name}")
        print(f"CODE:\n{code.strip()}\n")
        print("#" * 50 + "\n")
        compiler.compile(code)
        
    print("\n" + "=" * 20 + " RUNNING ERROR-HANDLING TESTS " + "=" * 15)
    error_tests = error_suite
    for name, code in error_tests:
        print("\n" + "#" * 50)
        print(f"TEST: {name}")
        print(f"CODE:\n{code.strip()}\n")
        print("#" * 50 + "\n")
        compiler.compile(code)


if __name__ == "__main__":
    run_tests()