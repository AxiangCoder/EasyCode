
import argparse
import os

from .converter import SketchConverter
from . import config

def main():
    """
    Main function to run the Sketch to DSL converter from the command line.
    """
    parser = argparse.ArgumentParser(
        description="Convert Sketch JSON to a design-specific DSL.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-i", "--input",
        dest="input_file",
        default=config.DEFAULT_SKETCH_INPUT,
        help="Path to the input Sketch JSON file."
    )
    parser.add_argument(
        "-t", "--tokens",
        dest="tokens_file",
        default=config.DEFAULT_TOKENS_INPUT,
        help="Path to the design tokens JSON file."
    )
    parser.add_argument(
        "-d", "--dsl-output",
        dest="dsl_output_file",
        default=config.DEFAULT_DSL_OUTPUT,
        help="Path for the output DSL JSON file."
    )
    parser.add_argument(
        "-r", "--report-output",
        dest="report_output_file",
        default=config.DEFAULT_REPORT_OUTPUT,
        help="Path for the output token report JSON file."
    )

    args = parser.parse_args()

    # Ensure the output directories exist
    os.makedirs(os.path.dirname(args.dsl_output_file), exist_ok=True)
    os.makedirs(os.path.dirname(args.report_output_file), exist_ok=True)

    try:
        converter = SketchConverter(
            input_file=args.input_file,
            tokens_file=args.tokens_file,
            dsl_output_file=args.dsl_output_file,
            report_output_file=args.report_output_file
        )
        converter.run()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
