#!/usr/bin/env python3

import cgi
import datetime
import json
import os
import sys

from argparse import ArgumentParser
from atomicwrite import AtomicWrite

if __name__ == '__main__':
    args = ArgumentParser()
    args.add_argument('-u', '--user', dest='user_id', help='dump messages of user USER_ID', metavar='USER_ID', type=int)
    args.add_argument('-c', '--chat', dest='chat_id', help='dump messages from chat CHAT_ID', metavar='CHAT_ID', type=int)
    options = args.parse_args()
    if (options.user_id is None) == (options.chat_id is None):
        print('Please specify only one of USER_ID and CHAT_ID')
        sys.exit(2)

    if options.user_id is not None:
        with open('out/messages/id%d.json' % options.user_id) as f:
            j = json.load(f)
    else:
        with open('out/messages/chat%d.json' % options.chat_id) as f:
            j = json.load(f)

    os.makedirs('out/html', exist_ok=True)
    with AtomicWrite('out/html/messages.css') as f:
        f.write('''\
.messages {
    width: 720px;
    position: relative;
    left: calc((100% - 720px) / 2);
}

.message {
    border: 1px solid black;
    margin-bottom: 1px;
}

.direction {
    padding: 2px;
    width: 20px;
    text-align: center;
    float: left;
}

.body {
    padding: 2px;
    width: 586px;
    float: left;
}

.date {
    padding: 2px;
    width: 100px;
    float: left;
}

.cf {
    clear: both;
}
''')

    if options.user_id is not None:
        filename = 'out/messages/id%d.html' % options.user_id
    else:
        filename = 'out/messages/chat%d.html' % options.chat_id
    with AtomicWrite(filename) as h:
        h.write('''\
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>id%d</title>
    <link rel="stylesheet" href="messages.css">
  </head>
  <body>
    <div class="messages">
''' % (options.user_id or options.chat_id))

        for message in j:
            h.write('<div class="message">\n')
            h.write('<div class="direction">%s</div><div class="body">' % ('&lt;' if message['out'] == 1 else '&gt;'))
            h.write(cgi.escape(message['body']))
            h.write('</div><div class="date">%s</div><div class="cf"></div>\n' % datetime.datetime.strftime(datetime.datetime.fromtimestamp(message['date']), '%Y-%m-%d<br>%H:%M'))
            h.write('</div>\n')

        h.write('''\
    </div>
  </body>
</html>''')
