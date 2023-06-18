import argparse

import os
from pathlib import Path

from functools import reduce
import operator

# Sources
from entropy_sources.vlf import vlf_source

# Transformations
from transformations.uniformize import UniformizeSignal, UniformizeSpectrum
from transformations.filter import FilterSpectrumAverage, FilterSpectrumMedian, FilterSpectrumWiener

# Plots
from plots import plot_type

DEFAULT_DURATION = 5


def main():
    # Define command line arguments
    parser = argparse.ArgumentParser(description='Radio Noise based TRNG.')

    # Add source argument
    sources = list(map(lambda x: x.__name__.split('_')[0], [
        vlf_source]))
    parser.add_argument('--source', dest='source_name', action='store',
                        type=str, choices=sources, default=sources[0],
                        help='a souce of choice for the data')

    parser.add_argument('--acquire', action='store_true',
                        help='acquire the data from the source')

    parser.add_argument('--duration', action='store', default=DEFAULT_DURATION, type=int,
                        help='the acquisition data aproximate duration in seconds, ' +
                        f'default: {DEFAULT_DURATION}')
    parser.add_argument('--acquisitions_dir', action='store', type=str,
                        help='directory to store the acquisitions')

    # TODO description
    parser.add_argument('--transformations', action='store', type=str)

    parser.add_argument('--name', action='store', type=str, default='',
                        help='the name of your the transformations')

    parser.add_argument('--block_size', action='store', type=int,
                        help='the dimension on which the data is processed, block by block')

    available_plots = list(
        map(lambda x: x.lower(), plot_type.__members__.keys()))
    parser.add_argument('--plot_types', action='store', type=str,
                        default=plot_type.NONE.name.lower(),
                        help='plot intermediate data, available plots: ' +
                        ', '.join(available_plots) + '; can be combined with comma (,)')

    parser.add_argument('--results_dir', action='store', type=str,
                        help='root directory to store the results')

    # Parse command line arguments
    args = parser.parse_args()

    # Create the source
    args.source_name = args.source_name + '_source'
    match args.source_name:
        case vlf_source.__name__:
            source = vlf_source(args.acquisitions_dir, args.results_dir)
        case _:
            pass

    # Split the plot_types string into a list of strings
    # Convert each string to the corresponding plot_type
    # Reduce the array of plot_types to a single plot_type
    plot_types: plot_type = reduce(operator.or_,
                                   [getattr(plot_type, t.upper()) for t in args.plot_types.split(',')])

    # Verify if there is a need to acquire data
    if (args.acquire):
        source.acquire(args.duration, plot_types)

    # Verify if there is a need to apply transformations
    if (args.transformations is None):
        return

    # Let the name of the transformation be the same as the transformations applied
    if args.name == '':
        args.name = args.transformations

    # Set the directories for the transformations
    base_product = os.path.join(Path(source.captures).parent, args.name)
    base_results = os.path.join(Path(source.results).parent, args.name)

    # Set the basic kwargs for the transformations
    kwargs = {
        'audio_dir': source.captures,
        'block_size': args.block_size
    }

    # Create the list transformations
    transformations = []

    # Parse the transformations string
    for i, trans_descr in enumerate(args.transformations.split(',')):
        # Parse the transformation description
        name, *tweaks = trans_descr.split('/')

        # Set the kwargs for this specific transformation
        init_kwargs = {**kwargs,
                       'product_dir': os.path.join(base_product, f'{i}_{name}'),
                       'results_dir': os.path.join(base_results, f'{i}_{name}')
                       }

        # Parse the tweaks, split them in key-value pairs
        for tweak in tweaks:
            for kv in tweak.split('-'):
                key, value = kv.split('=')

                # Convert the value to the correct type
                if value.isnumeric():
                    value = int(value)
                elif value.replace('.', '', 1).isdigit():
                    value = float(value)
                
                # Add the key-value pair to the init_kwargs
                init_kwargs[key] = value

        # Select the constructor for the transformation
        match name:
            case 'uniformize-signal':
                constructor = UniformizeSignal
            case 'uniformize-spectrum':
                constructor = UniformizeSpectrum
            case 'filter-spectrum-average':
                constructor = FilterSpectrumAverage
            case 'filter-spectrum-median':
                constructor = FilterSpectrumMedian
            case 'filter-spectrum-wiener':
                constructor = FilterSpectrumWiener
            case _:
                raise Exception(f'Unknown transformation: {name}')

        # Add the constructed transformation to the list
        transformations.append(constructor(**init_kwargs))

        # Feed the product of each transformation to the next one
        kwargs['audio_dir'] = init_kwargs['product_dir']

    # Iterate over the transformations
    for trans in transformations:
        # Execute the transformation
        trans.execute()

        # Plot the results
        plot_types.execute(trans.product_dir, trans.results_dir)


if __name__ == '__main__':
    main()
