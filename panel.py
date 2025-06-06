from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)
CONFIG_FILE = 'config.json'

# Default config in case the file doesn't exist
default_config = {
    "USER_LOG_CHANNELS": {
        "6018548705": -1002570801078,
        "6672038435": -1002500000000
    },
    "TOGGLES": {
        "bot_enabled": true,
        "forward_metadata": true,
        "enabled_commands": ["/help", "/dox", "/count", "/mutualgroups"]
    },
    "log_channel": -1001234567890,
    "specific_user_logs": [],
    "whitelist": [
        7989761934,
        6018548705,
        6672038435,
        5972356225,
        6568673568,
        7721086392
    ]
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=4)
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    config = load_config()

    config['whitelist_str'] = ','.join(map(str, config.get('whitelist', [])))
    config['specific_user_logs_str'] = ','.join(map(str, config.get('specific_user_logs', [])))
    config['user_log_channels_str'] = "\n".join([f"{uid}:{gid}" for uid, gid in config.get("USER_LOG_CHANNELS", {}).items()])
    config['enabled_commands_str'] = ','.join(config.get("TOGGLES", {}).get("enabled_commands", []))
    config['bot_enabled'] = config.get("TOGGLES", {}).get("bot_enabled", True)
    config['forward_metadata'] = config.get("TOGGLES", {}).get("forward_metadata", True)

    return render_template('index.html', config=config)

@app.route('/update', methods=['POST'])
def update():
    config = load_config()

    # Parse and handle the log_channel
    config['log_channel'] = int(request.form['log_channel']) if request.form['log_channel'] else 0

    # Parse whitelist and specific_user_logs
    config['whitelist'] = list(map(int, request.form['whitelist'].split(','))) if request.form['whitelist'] else []
    config['specific_user_logs'] = list(map(int, request.form['specific_user_logs'].split(','))) if request.form['specific_user_logs'] else []

    # Parse and handle the user_log_channels
    raw_map = request.form['user_log_channels'].strip().split('\n')
    config['USER_LOG_CHANNELS'] = {}

    for line in raw_map:
        if ':' in line:
            try:
                uid, gid = line.split(':')
                # Only add valid pairs to the dictionary
                if uid.strip() and gid.strip():
                    config['USER_LOG_CHANNELS'][int(uid.strip())] = int(gid.strip())
            except ValueError:
                # If there's an error in conversion, log it or skip the line
                print(f"Skipping invalid entry: {line}")

    # Update TOGGLES values
    config['TOGGLES'] = {
        'bot_enabled': 'bot_enabled' in request.form,
        'forward_metadata': 'forward_metadata' in request.form,
        'enabled_commands': [cmd.strip() for cmd in request.form['enabled_commands'].split(',') if cmd.strip()]
    }

    # Save the updated config
    save_config(config)

    # Redirect to the main page
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
