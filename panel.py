from flask import Flask, render_template, request, redirect
import json

app = Flask(__name__)
CONFIG_FILE = 'config.json'

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/update', methods=['POST'])
def update():
    config = load_config()
    config['log_channel'] = int(request.form['log_channel'])
    config['whitelist'] = list(map(int, request.form.getlist('whitelist')))
    config['specific_user_logs'] = list(map(int, request.form.getlist('specific_user_logs')))
    save_config(config)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
