import argparse
from _data_generation import DataGenerator
from milp import ConstructModel
import matplotlib.pyplot as plt
from _utils import read_parameters_from_json
import sys


def parse_arguments(args_dict, arguments, message):
    parser = argparse.ArgumentParser(
        description="Solve the capacitated vehicle routing problem with"
                    "time windows (CVRVTW) by specifying arguments or"
                    "using defaults from the JSON file."
    )
    for key, description in message.items():
        default_value = args_dict[key]
        param_type = type(default_value)
        if isinstance(description, dict) and "choices" in description:
            parser.add_argument(
                f"--{key}",
                type=param_type,
                default=default_value,
                choices=description["choices"],
                help=f"{description['description']} (default: {default_value})"
            )
        else:
            parser.add_argument(
                f"--{key}",
                type=param_type,
                default=default_value,
                help=f"{description if isinstance(description, str) else description.get('description', '')} (default: {default_value})"
            )
    parsed_args = vars(parser.parse_args(arguments))
    for key, value in parsed_args.items():
        if value is not None:
            args_dict[key] = value

    return args_dict

if __name__ == '__main__':
    # Read parameters and descriptions from the JSON file
    args, descriptions = read_parameters_from_json('arguments.json')
    # Dynamically parse command-line arguments
    args = parse_arguments(args, sys.argv[1:], descriptions)
    # Initialize the data generator with the updated args
    data = DataGenerator(args)
    print(
        'Constructing model for the network with,'
        '\nnum of vehicles = {} \nnum of customers = {}'.format(
            data.args['V'], data.args['I']
        )
    )
    # Solve the optimization problem
    model = ConstructModel(data)
    model.solve()
    # Plot the solution routes
    data._plot_routes(model._routes)