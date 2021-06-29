# Activate the env
. venv/bin/activate

# Run the logger server in 1 terminal
python prototype_lightning/logger_server.py

# Run the main server in another terminal
python prototype_lightning/lightning_server.py

# Run the client in another terminal
python prototype_lightning/lightning_client.py