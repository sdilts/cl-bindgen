import difflib
import filecmp
import os.path
import os
import io
import traceback
from enum import Enum
from dataclasses import dataclass, field

def _perform_diff(result, original):
    """  Compares the files `result` and `original`

    Returns a tuple:
      The first value is True if the files are the same
      The second arg is the text representation of the diff
    """

    are_same = filecmp.cmp(result, original)
    if not are_same:
        with open(result) as f:
            result_txt = f.readlines()
        with open(original) as f:
            original_txt = f.readlines()

        with io.StringIO() as output_stream:
            for line in  difflib.unified_diff(result_txt, original_txt):
                output_stream.write(line)
            return (False, output_stream.getvalue())
    else:
        return (True, "")

def _clean_dir(outdir):
    for f in os.listdir(outdir):
        os.remove(os.path.join(outdir, f))

def _prep_output_dir(outdir):
    if os.path.exists(outdir):
        if not os.path.isdir(outdir):
            raise Exception(f'output directory {outdir} is a file')
        else:
            _clean_dir(outdir)
    else:
        os.mkdir(outdir)

_divider_len = 40

def _output_err_title(message, outfile):
    equal_sign_amount = _divider_len - len(message) - 2
    start_banner = '=' * (equal_sign_amount // 2)
    end_banner = '=' * (equal_sign_amount - len(start_banner))
    print(start_banner, message, end_banner, file=outfile)

def _output_err_bar(outfile):
    print(('=' * _divider_len), file=outfile)

def _output_diff_error(input_file, base_file, output_file, diff, outfile):
    _output_err_title("TEST FAILED", outfile)
    outfile.write(f"input:   {input_file}\n")
    outfile.write(f"base:    {base_file}\n\n")
    outfile.write(f"result:  {output_file}\n")
    outfile.write(diff)
    _output_err_bar(outfile)

def _output_error(input_file, message, reason, outfile):
    _output_err_title(message, outfile)
    outfile.write(f"input: {input_file}\n\n")
    print(reason, '\n', sep='',file=outfile)
    _output_err_bar(outfile)

class TestOptions(Enum):
    EXPECT_FAIL = 0
    SKIP = 1
    THROWS_EXCEPTION = 2

def _get_options(opt_dict):
    options = dict()
    options[TestOptions.EXPECT_FAIL] = opt_dict.get(TestOptions.EXPECT_FAIL, False)
    options[TestOptions.SKIP] = opt_dict.get(TestOptions.SKIP, False)
    options[TestOptions.THROWS_EXCEPTION] = opt_dict.get(TestOptions.THROWS_EXCEPTION, False)
    return options

def _make_path_list(path):
    lst = []
    rest, part = os.path.split(path)
    last = rest
    lst.append(part)
    # TODO: This doesn't work with full paths, but it works in our case
    while not (rest == ''):
        rest, part = os.path.split(rest)
        # When at the root dir, rest may just repeat over and over:
        if rest == last:
            break;
        last = rest
        lst.append(part)
    lst.reverse()
    return lst

def _mangle_input_file(filename):
    dir_list = _make_path_list(os.path.dirname(filename))
    base_name = os.path.basename(filename)
    mangled_name = io.StringIO()
    for item in dir_list:
        mangled_name.write(f'{item}_')
    mangled_name.write(base_name)
    return mangled_name.getvalue()

@dataclass
class TestStats:
    failed: list = field(default_factory=lambda: [])
    expected_fail: list = field(default_factory=lambda: [])
    unexpected_pass: list = field(default_factory=lambda: [])
    skipped: list = field(default_factory=lambda: [])

    @staticmethod
    def print_stats(total, stat_object, outfile):
        failed = len(stat_object.failed)
        expected_fail = len(stat_object.expected_fail)
        unexpected_pass = len(stat_object.unexpected_pass)
        skipped = len(stat_object.skipped)
        outfile.write("Results:\n")
        num_okay = total - failed - expected_fail - unexpected_pass - skipped
        outfile.write(f"  Ok:                    {num_okay}\n")
        outfile.write(f"  Expected Fail:         {expected_fail}\n")
        outfile.write(f"  Fail:                  {failed}\n")
        outfile.write(f"  Unexpected Pass:       {unexpected_pass}\n")
        outfile.write(f"  Skipped:               {skipped}\n")

    @staticmethod
    def was_succes(stat_object):
        return len(stat_object.failed) == 0 and len(stat_object.unexpected_pass) == 0


def _perform_test(form, gen_fn, stat_object, outdir, outfile):
    input_file, compare_file, opts = form

    output_file = os.path.join(outdir, _mangle_input_file(input_file))

    options = _get_options(opts)

    if options[TestOptions.SKIP]:
        stat_object.skipped.append(input_file)
        return
    should_continue = True
    try:
        gen_fn(input_file, output_file)
    except Exception as err:
        if options[TestOptions.EXPECT_FAIL]:
            stat_object.expected_fail.append(input_file)
        elif not options[TestOptions.THROWS_EXCEPTION]:
            stat_object.failed.append(input_file)
            stream = io.StringIO()
            stream.write("Exception thrown during file generation:\n")
            traceback.print_exc(file=stream)
            _output_error(input_file, "TEST FAILED",
                          stream.getvalue().rstrip(),
                          outfile)
        should_continue = False
    if not should_continue:
        return

    is_same, diff = _perform_diff(output_file, compare_file)

    if not is_same:
        if options[TestOptions.EXPECT_FAIL]:
            stat_object.expected_fail.append(input_file)
        else:
            stat_object.failed.append(input_file)
            _output_diff_error(input_file, compare_file, output_file, diff, outfile)
    else:
        if options[TestOptions.EXPECT_FAIL]:
            stat_object.unexpected_pass.append(input_file)
            _output_error(input_file, "UNEXPECTED PASS",
                          "The test unexpectedly passed", outfile)


def run_tests(test_forms, gen_fn, outdir, outfile):
    _prep_output_dir(outdir)

    stats = TestStats()

    for form in test_forms:
        _perform_test(form, gen_fn, stats, outdir, outfile)

    TestStats.print_stats(len(test_forms), stats, outfile)

    return TestStats.was_succes(stats)
