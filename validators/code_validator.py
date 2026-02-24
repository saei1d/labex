import docker
import tempfile
import os
from datetime import datetime
from labs.models import TestCase, TestResult


class CodeValidator:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            raise Exception(f"Cannot connect to Docker: {e}")

    def validate_submission(self, submission):
        """Validate a code submission by running test cases."""
        results = []
        total_points = 0
        earned_points = 0

        test_cases = TestCase.objects.filter(
            lab_section=submission.lab_section
        ).order_by('order')

        for test_case in test_cases:
            total_points += test_case.points
            result = self._run_test_case(submission, test_case)
            results.append(result)

            if result.passed:
                earned_points += result.points_earned

        return {
            'submission_id': submission.id,
            'total_points': total_points,
            'earned_points': earned_points,
            'percentage': (
                earned_points / total_points * 100
            ) if total_points > 0 else 0,
            'test_results': results,
            'passed_all': all(r.passed for r in results),
        }

    def _run_test_case(self, submission, test_case):
        """Run a single test case."""
        start_time = datetime.now()

        try:
            # Create temporary files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write user code to file
                user_code_file = os.path.join(temp_dir, 'solution.py')
                with open(user_code_file, 'w') as f:
                    f.write(submission.code)

                # Write test code to file
                test_code_file = os.path.join(temp_dir, 'test_solution.py')
                with open(test_code_file, 'w') as f:
                    f.write(test_case.test_code)

                # Run test in container
                result = self._execute_test_in_container(
                    temp_dir, user_code_file, test_code_file
                )

                execution_time = (datetime.now() - start_time).total_seconds()

                # Parse test results
                passed, actual_output, error_message = self._parse_test_output(
                    result['output'], result['exit_code']
                )

                # Create test result record
                test_result = TestResult.objects.create(
                    submission=submission,
                    test_case=test_case,
                    passed=passed,
                    actual_output=actual_output,
                    error_message=error_message,
                    execution_time=execution_time,
                    points_earned=test_case.points if passed else 0.0
                )

                return test_result

        except Exception as e:
            # Create failed test result
            return TestResult.objects.create(
                submission=submission,
                test_case=test_case,
                passed=False,
                actual_output='',
                error_message=str(e),
                execution_time=(
                    datetime.now() - start_time
                ).total_seconds(),
                points_earned=0.0
            )

    def _execute_test_in_container(
        self, temp_dir, user_code_file, test_code_file
    ):
        """Execute tests in a Python container."""
        try:
            # Mount temp directory and run pytest
            volume_mount = {temp_dir: {'bind': '/app', 'mode': 'rw'}}

            result = self.client.containers.run(
                'python:3.11-slim',
                command=[
                    'python', '-m', 'pytest',
                    '-v', '--tb=short', 'test_solution.py'
                ],
                volumes=volume_mount,
                working_dir='/app',
                remove=True,
                stdout=True,
                stderr=True,
            )

            return {
                'exit_code': 0,
                'output': result.decode('utf-8')
            }

        except docker.errors.ContainerError as e:
            return {
                'exit_code': e.exit_status,
                'output': e.stderr.decode('utf-8') if e.stderr else str(e)
            }
        except Exception as e:
            return {
                'exit_code': -1,
                'output': str(e)
            }

    def _parse_test_output(self, output, exit_code):
        """Parse pytest output to determine if tests passed."""
        if exit_code == 0:
            # Tests passed
            return True, output, None
        else:
            # Tests failed - extract error message
            lines = output.split('\n')
            error_lines = []

            # Look for assertion errors or failures
            for line in lines:
                if 'FAILED' in line or 'ERROR' in line or 'AssertionError' in line:
                    error_lines.append(line.strip())

            error_message = '\n'.join(error_lines[-5:]) if error_lines else output
            return False, output, error_message

    def run_syntax_check(self, code):
        """Check if Python code has valid syntax."""
        try:
            compile(code, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, str(e)

    def run_linting(self, code):
        """Run basic linting on the code."""
        try:
            # This would integrate with flake8 or similar
            # For now, just basic checks
            issues = []

            # Check for common issues
            if 'print(' in code:
                issues.append("Consider removing print statements")

            if len(code.split('\n')) > 100:
                issues.append("Code is quite long, consider breaking into functions")

            return len(issues) == 0, issues

        except Exception as e:
            return False, [f"Linting error: {e}"]
