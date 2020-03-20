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

def _output_fail_info(input_file, base_file, output_file, diff, outfile):
    outfile.write("========= TEST FAILED =========\n")
    outfile.write(f"input:   {input_file}\n")
    outfile.write(f"base:    {base_file}\n\n")
    outfile.write(f"result:  {output_file}\n")
    outfile.write(diff)
    outfile.write("===============================\n\n")

def _output_stats(total, failed, expected_fail, unexpected_pass, skipped, outfile):
    outfile.write("Results:\n")
    num_okay = total - failed - expected_fail - unexpected_pass - skipped
    outfile.write(f"  Ok:                    {num_okay}\n")
    outfile.write(f"  Expected Fail:         {expected_fail}\n")
    outfile.write(f"  Fail:                  {failed}\n")
    outfile.write(f"  Unexpected Pass:       {unexpected_pass}\n")
    outfile.write(f"  Skipped:               {skipped}\n")


class TestOptions(Enum):
    EXPECT_FAIL = 0
    SKIP = 1

def _get_options(opt_dict):
    options = dict()
    options[TestOptions.EXPECT_FAIL] = opt_dict.get(TestOptions.EXPECT_FAIL, False)
    options[TestOptions.SKIP] = opt_dict.get(TestOptions.SKIP, False)
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

def run_tests(test_forms, gen_fn, outdir, outfile):
    _prep_output_dir(outdir)

    failed = []
    expected_failed = []
    unexpected_pass = []
    skipped = []

    for (input_file, compare_file, opts) in test_forms:
        output_file = os.path.join(outdir, _mangle_input_file(input_file))

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
                _output_fail_info(input_file, compare_file, output_file, diff, outfile)
        else:
            if options[TestOptions.EXPECT_FAIL]:
                unexpected_pass.append(input_file)
                # TODO: use different function that explains what happened
                _output_fail_info(input_file, compare_file, output_file, diff, outfile)

    _output_stats(len(test_forms), len(failed), len(expected_failed), len(unexpected_pass),
                  len(skipped), outfile)
    return len(failed) + len(unexpected_pass) == 0
