import argparse
import ast
import operator
import sys

from argparse import RawTextHelpFormatter
from functools import reduce
from os.path import join

# Sources
from entropy_sources.fm import fm_source
from entropy_sources.osrandom import osrandom_source
from entropy_sources.randomorg import randomorg_source
from entropy_sources.vlf import vlf_source

# Operations
from operations.filter import (
    filter_spectrum_average,
    filter_spectrum_gaussian,
    filter_spectrum_median,
    filter_spectrum_notch,
)
from operations.miscellaneous import (
    autocorrelate_signal,
    autocorrelate_spectrum,
    expand_band,
)
from operations.operation import operation
from operations.outlier import winsorize_spectrum, winsorize_signal
from operations.uniformize import (
    uniformize_signal,
    uniformize_spectrum_mean,
    uniformize_spectrum_median,
    uniformize_spectrum_maximum,
)

from strings import BANNER, SOURCE_FORMAT, OPERATIONS_FORMAT, PLOTS_FORMAT, TESTS_FORMAT

# Plots and tests
from plots import plot_type
from tests import test_type

DEFAULT_DURATION = 5
DEFAULT_SAMPLE_RATE = 32000

DEFAULT_AUDIO_DIR = "audio"
DEFAULT_EVAL_DIR = "out"
DEFAULT_SOURCE_DIR = "sources"

supported_sources = {
    "vlf": vlf_source,
    "fm": fm_source,
    "randomorg": randomorg_source,
    "osrandom": osrandom_source,
}

supported_operations = {
    "uniformize_signal": uniformize_signal,
    "uniformize_spectrum_mean": uniformize_spectrum_mean,
    "uniformize_spectrum_median": uniformize_spectrum_median,
    "uniformize_spectrum_maximum": uniformize_spectrum_maximum,
    "filter_spectrum_average": filter_spectrum_average,
    "filter_spectrum_gaussian": filter_spectrum_gaussian,
    "filter_spectrum_median": filter_spectrum_median,
    "filter_spectrum_notch": filter_spectrum_notch,
    "winsorize_spectrum": winsorize_spectrum,
    "winsorize_signal": winsorize_signal,
    "autocorrelate_signal": autocorrelate_signal,
    "autocorrelate_spectrum": autocorrelate_spectrum,
    "expand_band": expand_band,
}


def make_plot_types(args) -> plot_type:
    # Construct Abstract Syntax Tree
    tree = ast.parse(args.plots, mode="eval")

    # Check if it's just one element
    if isinstance(tree.body, ast.Name):
        tree = ast.Expression(
            body=ast.List(
                elts=[tree.body],
                ctx=ast.Load(),
            )
        )

    # At this point the tree should be a list
    if not isinstance(tree.body, ast.List):
        sys.stderr.write(PLOTS_FORMAT)

    # Map the array to plot_types
    plot_types = [getattr(plot_type, p.id.upper()) for p in tree.body.elts]

    # Reduce the array to a single plot_type
    return reduce(operator.or_, plot_types)


def make_test_types(args) -> test_type:
    # Construct Abstract Syntax Tree
    tree = ast.parse(args.tests, mode="eval")

    # Check if it's just one element
    if isinstance(tree.body, ast.Name):
        tree = ast.Expression(
            body=ast.List(
                elts=[tree.body],
                ctx=ast.Load(),
            )
        )

    # At this point the tree should be a list
    if not isinstance(tree.body, ast.List):
        sys.stderr.write(TESTS_FORMAT)

    # Map the array to test_types
    test_types = [getattr(test_type, t.id.upper()) for t in tree.body.elts]

    # Reduce the array to a single test_type
    return reduce(operator.or_, test_types)


def make_source(args):
    # Set the basic kwargs for the source
    kwargs = {
        "sample_rate": args.acquisition_sample_rate,
        "block_size": args.block_size,
    }

    # Construct Abstract Syntax Tree
    tree = ast.parse(args.source, mode="eval")

    # Check if source has no parameters
    if isinstance(tree.body, ast.Name):
        tree = ast.Expression(body=ast.Call(func=tree.body, args=[], keywords=[]))

    # At this point the starting point should look like a regular call
    if not isinstance(tree.body, ast.Call):
        sys.stderr.write(SOURCE_FORMAT)
        exit(1)

    # Get the constructor for the source
    name = tree.body.func.id
    if name in supported_sources:
        constructor = supported_sources[name]
    else:
        raise Exception(f"Unknown source: {name}")

    # Get tweaks for the source
    kwargs.update({kw.arg: ast.literal_eval(kw.value) for kw in tree.body.keywords})

    # Extract working directories
    if args.audio_dir is None:
        args.audio_dir = join(DEFAULT_AUDIO_DIR, name)
    if args.eval_dir is None:
        args.eval_dir = join(DEFAULT_EVAL_DIR, name)

    kwargs["source_dir"] = join(args.audio_dir, DEFAULT_SOURCE_DIR)
    kwargs["eval_dir"] = join(args.eval_dir, DEFAULT_SOURCE_DIR)

    return constructor(**kwargs)


def make_operations(args, source) -> list[operation]:
    # If no name is given: let the name of the operations be the same as the operations applied
    if args.name == "":
        args.name = args.operations

    # Set the directories for the operations
    base_product = join(args.audio_dir, args.name)
    base_eval = join(args.eval_dir, args.name)

    # Set the basic kwargs for the operations
    kwargs = {
        "audio_dir": source.source_dir,
        "block_size": args.block_size,
        "sample_rate": source.sample_rate,
    }

    # Construct Abstract Syntax Tree
    tree = ast.parse(args.operations, mode="eval")

    # Check is just one operation was passed has no parameters
    if isinstance(tree.body, ast.Name):
        tree = ast.Expression(body=ast.Call(func=tree.body, args=[], keywords=[]))

    # Check is just one operation was passed has parameters
    if isinstance(tree.body, ast.Call):
        tree = ast.Expression(
            body=ast.List(
                elts=[tree.body],
                ctx=ast.Load(),
            )
        )

    # At this point the starting point should look like a regular list
    if not isinstance(tree.body, ast.List):
        sys.stderr.write("Operations must be in one of the following formats:\n")
        sys.stderr.write("    - name\n")
        sys.stderr.write("    - name(option_1=val_1,...,option_n=val_n)\n")
        sys.stderr.write("    - [name_1(...), ..., name_n(...)]\n")
        exit(1)

    # Create the list operations
    operations = []

    # Parse the operations string
    for i, op in enumerate(tree.body.elts):
        # Check if operations has no parameters
        if isinstance(op, ast.Name):
            op = ast.Call(func=op, args=[], keywords=[])

        # Get the constructor for the operation
        name = op.func.id
        if name in supported_operations:
            constructor = supported_operations[name]
        else:
            raise Exception(f"Unknown operation: {name}")

        # Set the kwargs for this specific operation
        op_kwargs = {
            **kwargs,
            "product_dir": join(base_product, f"{i}_{name}"),
            "eval_dir": join(base_eval, f"{i}_{name}"),
        }

        # Get tweaks for the source
        op_kwargs.update({kw.arg: ast.literal_eval(kw.value) for kw in op.keywords})

        # Add the constructed operation to the list
        operations.append(constructor(**op_kwargs))

        # Feed the product of each operation to the next one
        kwargs["audio_dir"] = op_kwargs["product_dir"]

    return operations


def compute(args):
    # Extract what evaluations need to be done
    plot_types = make_plot_types(args)
    test_types = make_test_types(args)

    # Create the entropy source
    source = make_source(args)

    # Verify if there is a need to acquire data
    if args.acquire:
        source.acquire(args.duration)
        plot_types.execute(source.source_dir, source.eval_dir)
        test_types.execute(source.source_dir, source.eval_dir)

    # Verify if all the sources are in the same format
    if (args.source_trim_to_same_length):
        source.source_trim_to_same_length()

    # Verify if there is a need to apply operations
    if args.operations is None:
        return

    # Extract the operations that need to be applied
    operations = make_operations(args, source)

    # Iterate over the operations
    for op in operations:
        # Execute the operation
        op.execute()

        last_op = op

        # Evaluate the results if we should for intermediate stages
        if not args.evaluate_only_last_operation:
            plot_types.execute(op.product_dir, op.eval_dir)
            test_types.execute(op.product_dir, op.eval_dir)

    if args.evaluate_only_last_operation:
        plot_types.execute(last_op.product_dir, last_op.eval_dir)
        test_types.execute(last_op.product_dir, last_op.eval_dir)


def add_arguments(parser: argparse.ArgumentParser):
    available_sources = map(lambda k: f"- {k}", supported_sources.keys())
    available_sources = "\n    ".join(available_sources)
    parser.add_argument(
        "--source",
        action="store",
        required=True,
        type=str,
        default=available_sources[0],
        help="an entropy source of choice, available sources:\n    "
        + available_sources
        + f"\n\n{SOURCE_FORMAT}\n",
    )

    parser.add_argument(
        "--acquire",
        action="store_true",
        help="whether or not to acquire data from the source",
    )

    parser.add_argument(
        "--acquisition_sample_rate",
        action="store",
        default=DEFAULT_SAMPLE_RATE,
        type=int,
        help="the sampling rate at which to save the acquired data, "
        + f"default: {DEFAULT_SAMPLE_RATE}Hz",
    )

    parser.add_argument(
        "--duration",
        action="store",
        default=DEFAULT_DURATION,
        type=int,
        help="(approximate) length (in seconds) for the WAV file to store data, "
        + f"default: {DEFAULT_DURATION}",
    )

    parser.add_argument(
        "--audio_dir",
        action="store",
        type=str,
        help="directory to store the audio files",
    )

    available_operations = map(lambda k: f"- {k}", supported_operations.keys())
    available_operations = "\n    ".join(available_operations)
    parser.add_argument(
        "--operations",
        action="store",
        type=str,
        help="operations to be applied"
        + "available:\n    "
        + available_operations
        + f"\n\n{OPERATIONS_FORMAT}",
    )

    parser.add_argument(
        "--name",
        action="store",
        type=str,
        default="",
        help="the name of the method described by the sequence of operations\nit is just a label",
    )

    parser.add_argument(
        "--block_size",
        action="store",
        type=int,
        help="the dimension on which the data is processed, block by block",
    )

    available_plots = map(lambda x: "- " + x.lower(), plot_type.__members__.keys())
    available_plots = "\n    ".join(available_plots)
    parser.add_argument(
        "--plots",
        action="store",
        type=str,
        default=f"[{plot_type.NONE.name.lower()}]",
        help="whether or not to plot data, "
        + "available plots:\n    "
        + available_plots
        + f"\n\n{PLOTS_FORMAT}",
    )

    available_tests = map(lambda x: "- " + x.lower(), test_type.__members__.keys())
    available_tests = "\n    ".join(available_tests)
    parser.add_argument(
        "--tests",
        action="store",
        type=str,
        default=f"[{test_type.NONE.name.lower()}]",
        help="whether or not run to test, "
        + "available tests:\n    "
        + available_tests
        + f"\n\n{TESTS_FORMAT}",
    )

    parser.add_argument(
        "--evaluation_dir",
        dest="eval_dir",
        action="store",
        type=str,
        help="root directory to store the plots and tests",
    )

    parser.add_argument(
        "--evaluate_only_last_operation",
        dest="evaluate_only_last_operation",
        action="store_true",
        help="set this if you don't want intermediate evaluations for operations",
    )

    parser.add_argument(
        "--source_trim_to_same_length",
        dest="source_trim_to_same_length",
        action="store_true",
        help="set this if you have a source that outputs multiple WAV files, and you want them to have the same length",
    )


def main():
    # Define command line arguments
    parser = argparse.ArgumentParser(BANNER, formatter_class=RawTextHelpFormatter)

    # Do not bloat this function with all arguments
    add_arguments(parser)

    # Parse command line arguments
    args = parser.parse_args()

    compute(args)


if __name__ == "__main__":
    main()
