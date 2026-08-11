#!/usr/bin/env python3
__version__ = "1.0.0"
"""
fit_chain.py -- apply a SEQUENCE of fit_patch.py operations to a file
before a single device write, avoiding a device restart per change.

Design: reuses fit_patch.py's existing, already-validated CLI directly
via subprocess for each step, rather than reimplementing any of its
logic (field-count/layout guards, f9 auto-assignment, etc.) in a new
"batch" code path. Each step's output becomes the next step's input;
only the FINAL file is meant to ever reach the device. CRC-verified
after every single step, not just at the end, so a broken step is
caught immediately rather than silently carried forward.

This directly enables what was previously only possible by hand:
swap two fields, reorder two screens, hide a screen, THEN write once
-- one device restart instead of three.
"""
import sys
import os
import subprocess
import tempfile
import shutil

from fit_crc import fit_crc


class ChainError(Exception):
    pass


def apply_chain(input_path, output_path, steps, verbose=True, fit_patch_path=None):
    """
    Apply a sequence of fit_patch.py operations in order.

    input_path:  starting .fit file
    output_path: final result after all steps
    steps:       list of lists, each a set of fit_patch.py CLI args
                 EXCLUDING input_file/output_file (those are chained
                 automatically). e.g.:
                     [["--slot", "9", "--hide"],
                      ["--swap-order", "1,11"]]
    fit_patch_path: path to fit_patch.py; defaults to the copy
                 sitting next to this file.

    Raises ChainError (with the failing step's index and stderr) on
    the first step that fails, WITHOUT touching output_path -- a
    partial/broken chain never produces a file that looks final.

    Returns output_path on success.
    """
    if not steps:
        raise ChainError("apply_chain() called with an empty steps list -- nothing to do")

    if fit_patch_path is None:
        fit_patch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fit_patch.py")

    work_dir = tempfile.mkdtemp(prefix="fit_chain_")
    try:
        current = input_path
        for i, step_args in enumerate(steps):
            step_out = os.path.join(work_dir, f"step{i}.fit")
            cmd = [sys.executable, fit_patch_path, current, step_out] + list(step_args)

            if verbose:
                print(f"[chain step {i+1}/{len(steps)}] {' '.join(step_args)}", file=sys.stderr)

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise ChainError(
                    f"Step {i+1}/{len(steps)} failed ({' '.join(step_args)}):\n"
                    f"{result.stderr.strip()}"
                )
            if verbose:
                # fit_patch.py's own per-step confirmation/note messages go to
                # stdout in some code paths and stderr in others (an existing
                # inconsistency in that tool, not something to silently drop
                # here) -- surface both so nothing gets lost.
                if result.stdout.strip():
                    print(result.stdout.strip(), file=sys.stderr)
                if result.stderr.strip():
                    print(result.stderr.strip(), file=sys.stderr)

            if not os.path.exists(step_out):
                raise ChainError(
                    f"Step {i+1}/{len(steps)} reported success but produced no output file "
                    f"({' '.join(step_args)})"
                )

            # Verify CRC after EVERY step, not just at the end -- catch a
            # broken intermediate result immediately rather than chaining
            # a corrupt file forward through the remaining steps.
            with open(step_out, "rb") as f:
                data = f.read()
            expected_crc = int.from_bytes(data[-2:], "little")
            computed_crc = fit_crc(data[:-2])
            if expected_crc != computed_crc:
                raise ChainError(
                    f"Step {i+1}/{len(steps)} produced a file with an invalid CRC "
                    f"({' '.join(step_args)}) -- refusing to continue the chain"
                )

            current = step_out

        shutil.copy2(current, output_path)
        if verbose:
            print(f"Chain complete: {len(steps)} step(s) applied -> {output_path}", file=sys.stderr)
        return output_path
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def _cli():
    import argparse
    import shlex

    parser = argparse.ArgumentParser(
        description="Apply multiple fit_patch.py operations before a single write.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  python3 fit_chain.py in.fit out.fit \\\n"
            "      --step '--slot 9 --hide' \\\n"
            "      --step '--swap-order 1,11' \\\n"
            "      --step '--slot 4 --layout 1'\n"
        ),
    )
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("--step", action="append", required=True,
                         help="one fit_patch.py argument string (quoted), repeatable, "
                              "applied in the order given")
    args = parser.parse_args()

    steps = [shlex.split(s) for s in args.step]
    try:
        apply_chain(args.input_file, args.output_file, steps)
    except ChainError as e:
        print(f"CHAIN FAILED: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _cli()
