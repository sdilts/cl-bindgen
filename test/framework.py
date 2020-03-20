import difflib
import filecmp
import os.path
import os
import io
from enum import Enum

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

def _output_fail_info(input_file, output_file, diff, outfile):
    outfile.write("=== TEST FAILED ===\n")
    outfile.write(f"INPUT FILE:  {input_file}\n")
    outfile.write(f"OUTPUT FILE: {output_file}\n")
    outfile.write("diff:\n")
    outfile.write(diff)
    outfile.write("\n\n")

def _output_stats(failed, expected_fail, unexpected_pass, skipped, outfile):
    pass

class TestOptions(Enum):
    EXPECT_FAIL = 0
    SKIP = 1

def _get_options(opt_dict):
    options = dict()
    options[TestOptions.EXPECT_FAIL] = opt_dict.get(TestOptions.EXPECT_FAIL, False)
    options[TestOptions.SKIP] = opt_dict.get(TestOptions.SKIP, False)
    return options

def run_tests(test_forms, gen_fn, indir, outdir, outfile):
    _prep_output_dir(outdir)

    failed = []
    expected_failed = []
    unexpected_pass = []
    skipped = []

    for (input_file, compare_file, opts) in test_forms:
        output_file = os.path.join(outdir, input_file)
        input_file = os.path.join(indir, input_file)

        options = _get_options(opts)

        if options[TestOptions.SKIP]:
            skipped.append(input_file)
            continue
        gen_fn(input_file, output_file)

        is_same, diff = _perform_diff(output_file, compare_file)

        if not is_same:
            if options[TestOptions.EXPECT_FAIL]:
                expected_failed.append(input_file)
            else:
                failed.append(input_file)
                _output_fail_info(input_file, output_file, diff, outfile)
        else:
            if options[TestOptions.EXPECT_FAIL]:
                unexpected_pass.append(input_file)
                # TODO: make use different function
                _output_fail_info(input_file, output_file, diff, outfile)
    outfile.write("\n")
    _output_stats(failed, expected_failed, unexpected_pass, skipped, outfile)
    return len(failed) + len(unexpected_pass) == 0
