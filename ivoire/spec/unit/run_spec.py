from ivoire import describe

from ivoire import run
from ivoire.spec.util import mock, patch, patchObject


with describe(run.should_color) as it:
    @it.before
    def before(test):
        test.stderr = patchObject(test, run.sys, "stderr")

    with it("colors whenever stderr is a tty") as test:
        test.stderr.isatty.return_value = True
        test.assertTrue(run.should_color("auto"))

    with it("doesn't color otherwise") as test:
        test.stderr.isatty.return_value = False
        test.assertFalse(run.should_color("auto"))


with describe(run.run) as it:
    @it.before
    def before(test):
        test.config = mock.Mock(specs=[])
        test.load_by_name = patchObject(test, run, "load_by_name")
        test.result = patch(test, "ivoire.current_result")
        test.setup = patchObject(test, run, "setup")
        test.exit = patchObject(test, run.sys, "exit")

    with it("succeeds with status code 0") as test:
        test.result.wasSuccessful.return_value = True
        run.run(test.config)
        test.exit.assert_called_once_with(0)

    with it("fails with status code 1") as test:
        test.result.wasSuccessful.return_value = False
        run.run(test.config)
        test.exit.assert_called_once_with(1)

    with it("logs an error to the result if an import fails") as test:
        test.config.specs = ["does.not.exist"]
        test.load_by_name.side_effect = IndexError

        run.run(test.config)

        (example, traceback), _ = test.result.addError.call_args
        test.assertEqual(str(example), "<not in example>")
        test.assertEqual(traceback[0], IndexError)
