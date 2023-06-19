import argparse

from os.path import join
from pathlib import Path

from functools import reduce
import operator

# Sources
from entropy_sources.vlf import vlf_source
from entropy_sources.fm import fm_source

# Operations
from operations.operation import operation
from operations.uniformize import uniformize_signal
from operations.uniformize import uniformize_spectrum
from operations.filter import filter_spectrum_average
from operations.filter import filter_spectrum_median
from operations.filter import filter_spectrum_gaussian

# Plots
from plots import plot_type

DEFAULT_DURATION = 5
DEFAULT_AUDIO_DIR = 'audio'
DEFAULT_EVAL_DIR = 'out'
DEFAULT_SOURCE_DIR = 'sources'


def make_plot_types(args) -> plot_type:
    # Split the plot_types string into a list of strings
    # Convert each string to the corresponding plot_type
    # Reduce the array of plot_types to a single plot_type
    plot_types = [getattr(plot_type, t.upper())
                  for t in args.plot_types.split('+')]
    return reduce(operator.or_, plot_types)


def get_value(value: str):
    # Convert the value to the correct type
    if value == 'None':
        return None
    elif value.isnumeric():
        return int(value)
    elif value.replace('.', '', 1).isdigit():
        return float(value)
    elif value == 'False' or value == 'True':
        return value == 'True'
    elif value.startswith('\'') and value.endswith('\'') or \
            value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    elif value.startswith('[') and value.endswith(']'):
        values = value[1:-1].split(',')
        return list(map(get_value, values))
    elif value.startswith('(') and value.endswith(')'):
        return tuple(map(get_value, values))
    elif value.startswith('{') and value.endswith('}'):
        raise NotImplementedError


def make_source(args):
    # Set the basic kwargs for the source
    kwargs = {}

    # Parse the source description
    name, *tweaks = args.source.split('/')

    # Parse the tweaks, split them in key-value pairs
    for tweak in tweaks:
        key, value = tweak.split('=')

        # Add the key-value pair to the kwargs
        kwargs[key] = get_value(value)

    match name + '_source':
        case vlf_source.__name__:
            constructor = vlf_source
        case fm_source.__name__:
            constructor = fm_source
            pass
        case _:
            raise Exception(f'Unknown source: {name}')

    # Extract working directories
    if args.audio_dir is None:
        args.audio_dir = join(DEFAULT_AUDIO_DIR, name)
    if args.eval_dir is None:
        args.eval_dir = join(DEFAULT_EVAL_DIR, name)

    kwargs['source_dir'] = join(args.audio_dir, DEFAULT_SOURCE_DIR)
    kwargs['eval_dir'] = join(args.eval_dir, DEFAULT_SOURCE_DIR)

    return constructor(**kwargs)


def make_operations(args, source) -> list[operation]:
    # Let the name of the operations be the same as the operations applied if no name is given
    if args.name == '':
        args.name = args.operations

    # Set the directories for the operations
    base_product = join(args.audio_dir, args.name)
    base_eval = join(args.eval_dir, args.name)

    # Set the basic kwargs for the operations
    kwargs = {
        'audio_dir': source.source_dir,
        'block_size': args.block_size
    }

    # Create the list operations
    operations = []

    # Parse the operations string
    for i, op_description in enumerate(args.operations.split('+')):
        # Parse the operation description
        name, *tweaks = op_description.split('/')

        # Set the kwargs for this specific operation
        op_kwargs = {
            **kwargs,
            'product_dir': join(base_product, f'{i}_{name}'),
            'eval_dir': join(base_eval, f'{i}_{name}')
        }

        # Parse the tweaks, split them in key-value pairs
        for tweak in tweaks:
            key, value = tweak.split('=')

            # Add the key-value pair to the current kwargs
            op_kwargs[key] = get_value(value)

        # Select the constructor for the operation
        match name:
            case 'uniformize_signal':
                constructor = uniformize_signal
            case 'uniformize_spectrum':
                constructor = uniformize_spectrum
            case 'filter_spectrum_average':
                constructor = filter_spectrum_average
            case 'filter_spectrum_median':
                constructor = filter_spectrum_median
            case 'filter_spectrum_gaussian':
                constructor = filter_spectrum_gaussian
            case _:
                raise Exception(f'Unknown operation: {name}')

        # Add the constructed operation to the list
        operations.append(constructor(**op_kwargs))

        # Feed the product of each operation to the next one
        kwargs['audio_dir'] = op_kwargs['product_dir']

    return operations


def compute(args):
    # Extract what plots need to be shown
    plot_types = make_plot_types(args)

    # Create the entropy source
    source = make_source(args)

    # Verify if there is a need to acquire data
    if (args.acquire):
        source.acquire(args.duration)
        plot_types.execute(source.source_dir, source.eval_dir)

    # Verify if there is a need to apply operations
    if (args.operations is None):
        return

    # Extract the operations that need to be applied
    operations = make_operations(args, source)

    # Iterate over the operations
    for op in operations:
        # Execute the operation
        op.execute()

        # Plot the results
        plot_types.execute(op.product_dir, op.eval_dir)


def add_arguments(parser: argparse.ArgumentParser):
    parser.add_argument('--source', action='store',
                        type=str, default=vlf_source.__name__.split('_')[0],
                        help='a souce of choice for the data')

    parser.add_argument('--acquire', action='store_true',
                        help='acquire the data from the source')

    parser.add_argument('--duration', action='store', default=DEFAULT_DURATION, type=int,
                        help='the acquisition data aproximate duration in seconds, ' +
                        f'default: {DEFAULT_DURATION}')

    parser.add_argument('--audio_dir', action='store', type=str,
                        help='directory to store the audio files')

    # TODO description
    parser.add_argument('--operations', action='store', type=str)

    parser.add_argument('--name', action='store', type=str, default='',
                        help='the name of your the method described by the operations')

    parser.add_argument('--block_size', action='store', type=int,
                        help='the dimension on which the data is processed, block by block')

    available_plots = list(
        map(lambda x: x.lower(), plot_type.__members__.keys()))
    parser.add_argument('--plot_types', action='store', type=str,
                        default=plot_type.NONE.name.lower(),
                        help='plot intermediate data, available plots: ' +
                        ', '.join(available_plots) + '; can be combined with plus (+)')

    parser.add_argument('--evaluation_dir', dest='eval_dir', action='store', type=str,
                        help='root directory to store the plots and tests')


def main():
    # Define command line arguments
    parser = argparse.ArgumentParser(description='Radio Noise based TRNG.')

    add_arguments(parser)

    # Parse command line arguments
    args = parser.parse_args()

    compute(args)


if __name__ == '__main__':
    main()
