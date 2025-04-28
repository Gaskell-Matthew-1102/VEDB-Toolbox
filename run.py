# written by brian
# but... argument parsing done by chatgpt

# base
from argparse import ArgumentParser
from os import cpu_count

# pip
from waitress import serve

# local - application setup
from flaskr import create_app

def parse_args():
    parser = ArgumentParser(description="VEDB Toolbox application setup.")
    
    # Add a command-line argument for the config type
    parser.add_argument(
        "--config",
        choices = ["devel", "mem", "wsgi"],
        default = "devel",
        help = "Specify the configuration to use: 'devel' (default), 'mem', or 'wsgi'."
    )
    return parser.parse_args()

# Run the Flask app based on the provided configuration type
def run_app(config_type):
    # Create the app with the appropriate configuration
    app = create_app(test_config=None if config_type != "mem" else True)

    # Conditional logic to handle different configurations
    if config_type == "devel" or config_type == "mem":
        app.run(debug=True)
    elif config_type == "wsgi":
        serve(app, listen='*:5000', threads=cpu_count(), max_request_body_size=4294967296)
        

# Run the app based on the selected configuration parsed from the command line
if __name__ == "__main__":
    run_app(parse_args().config)
