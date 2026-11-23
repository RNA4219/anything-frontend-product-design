"""Only test reporting classification. No browser is launched by these tests."""
import unittest
from browser_contracts import exception_status


class ReportingTests(unittest.TestCase):
    def test_unavailable_setup_is_blocked(self):
        self.assertEqual(exception_status('setup'), 'BLOCKED')

    def test_fixture_and_runtime_errors_do_not_claim_environment_block(self):
        for phase in ('navigation', 'interaction'):
            self.assertEqual(exception_status(phase), 'ERROR_TEST_EXECUTION')


if __name__ == '__main__':
    unittest.main()
