# written by brian
# but... argument parsing done by chatgpt

# base
from argparse import ArgumentParser
from os import system as run_shell_command

# local - application setup
from flaskr import create_app

def parse_args():
    parser = ArgumentParser(description="VEDB Toolbox application setup.")
    
    # Add a command-line argument for the config type
    parser.add_argument(
        "--config",
        choices = ["devel", "mem", "wsgi-zach"],
        default = "devel",
        help = "Specify the configuration to use: 'devel' (default), 'mem', or 'wsgi-zach'."
    )
    return parser.parse_args()

# Run the Flask app based on the provided configuration type
def run_app(config_type):
    if config_type == "wsgi-zach":
        # WSGI on CSE server port 9090 as a daemon (6 allotted CPU cores = 12 workers (2 per core))
        run_shell_command("gunicorn -w 12 -b 0.0.0.0:9090 'flaskr:create_app(test_config=None)' --daemon")
    else:
        # Default to development configuration. "mem" uses a static secret key and in-memory sqlite database
        if config_type == "mem":
            app = create_app(test_config=True)
        else:
            app = create_app(test_config=None)
        app.run(debug=True)

# Run the app based on the selected configuration parsed from the command line
if __name__ == "__main__":
    run_app(parse_args().config)
