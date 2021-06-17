import socket
import redis
import time
import os
from flask import Flask, request, session
from flask_session import Session

app = Flask(__name__)

app.secret_key = os.getenv('APP_SECRET_KEY')
app.redis_url = os.getenv('REDIS_URL')
app.spacer = '\n\n<br><br><br>\n'

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url(app.redis_url)

server_session = Session(app)


def getAllSessions():
    r = redis.Redis.from_url(app.redis_url)
    return r.keys()

def processCommand(command):    
    if 'started_at' not in session.keys():
        session['started_at'] = str(time.time())
    redis_sessions = getAllSessions()
    session_text =  'Session count: ' + str(len(redis_sessions)) + '.'
    session_text += app.spacer + 'Actual sessions IDs: ' + str(redis_sessions)
    return {
        'WHO': session_text,
        'WHERE': 'HostName: ' + socket.gethostname(),
        'WHY': 'Answer to the Ultimate Question of Life, the Universe, and Everything: 42'
    }.get(command, "Command not found.") + app.spacer + 'Your session started at: ' + session['started_at']


@app.route('/api', methods=['GET', 'POST'])
def api():
    if request.method == 'POST':
        return processCommand(request.form['command'])
    return "Error, you need to specify the command as follow: curl -d 'command=XXXX' URL"

@app.route('/web', methods=['GET', 'POST'])
def web():
    if request.method == 'POST':
        return processCommand(request.form['command'])

    return """
        <form method="post">
            <label for="command">Enter the command:</label>
            <input type="text" id="command" name="command" required />
            <button type="submit">Submit</button
        </form>
        """

if __name__ == '__main__':
    app.run()