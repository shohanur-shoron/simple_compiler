from compiler import Compiler
from test_cases import test_suite, error_suite

def run_tests():
    compiler = Compiler()
    
    # print("\n" + "=" * 20 + " RUNNING PASSING TESTS " + "=" * 20)
    # tests = test_suite
    # for name, code in tests:
    #     print("\n" + "#" * 50)
    #     print(f"TEST: {name}")
    #     print(f"CODE:\n{code.strip()}\n")
    #     print("#" * 50 + "\n")
    #     compiler.compile(code)
        
    # print("\n" + "=" * 20 + " RUNNING ERROR-HANDLING TESTS " + "=" * 15)
    # error_tests = error_suite
    # for name, code in error_tests:
    #     print("\n" + "#" * 50)
    #     print(f"TEST: {name}")
    #     print(f"CODE:\n{code.strip()}\n")
    #     print("#" * 50 + "\n")
    #     compiler.compile(code)

    code = """
    // nested if else and nested for loop
        int n;
        n = 5;
        int num = 45;
        int var = 0;

        if(n > num){
            var = var + 10;
        }
        else{
            if(var == 0){
                var = 20;
            }
            else{
                int i = 0;
                int j;
                for(i = 0; i < n; i++){
                    for(j = 0; j<n; j++){
                        var = var + j;
                    }
                }
            }
        }

    """
    print(code)
    compiler.compile(code)


if __name__ == "__main__":
    run_tests()