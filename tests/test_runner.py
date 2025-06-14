import os
import sys
from typing import List, Tuple
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import SimpleLangAnalyzer
from errors import ErrorReporter

class TestRunner:
    def __init__(self):
        self.analyzer = SimpleLangAnalyzer()
        self.test_cases_dir = os.path.join(os.path.dirname(__file__), 'test_cases')
        self.passed_tests = 0
        self.failed_tests = 0
    
    def run_test(self, filename: str, expect_success: bool) -> bool:
        """Run a single test case"""
        print(f"\nTesting {filename}...")
        print("=" * 50)
        
        filepath = os.path.join(self.test_cases_dir, filename)
        success = self.analyzer.analyze_file(filepath)
        
        if success == expect_success:
            print(f"✓ Test passed: {'success' if success else 'failure'} as expected")
            self.passed_tests += 1
            return True
        else:
            print(f"✗ Test failed: expected {'success' if expect_success else 'failure'}, "
                  f"got {'success' if success else 'failure'}")
            self.failed_tests += 1
            return False
    
    def run_all_tests(self):
        """Run all test cases"""
        test_cases: List[Tuple[str, bool]] = [
            # (filename, expect_success)
            ('valid_program.sl', True),
            ('invalid_declaration.sl', False),
            ('invalid_assignment.sl', False),
            ('invalid_control.sl', False),
            ('missing_brace.sl', False),
        ]
        
        print("SimpleLang Syntax Analyzer Test Suite")
        print("=" * 50)
        
        for filename, expect_success in test_cases:
            self.run_test(filename, expect_success)
        
        # Print summary
        total = self.passed_tests + self.failed_tests
        print("\nTest Summary")
        print("=" * 50)
        print(f"Total tests: {total}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success rate: {(self.passed_tests / total) * 100:.1f}%")

def main():
    """Main function"""
    runner = TestRunner()
    runner.run_all_tests()

if __name__ == "__main__":
    main()