#!/usr/bin/env python3

import json
import logging
import os
import sys
import xdg.BaseDirectory

from argparse import ArgumentParser
from atomicwrite import AtomicWrite
from oauthdialog import OAuthDialog
from PyQt4 import QtCore, QtGui, QtWebKit
from vk import VK
from vkattachmentsaver import VKAttachmentSaver

def vkDumpMessages(vk, user_id=None, chat_id=None):
    assert (user_id is None) != (chat_id is None)
    offset = 0
    count = 200
    while offset < count:
        reply = vk.messages.getHistory(user_id=user_id, chat_id=chat_id, rev=1, offset=offset, count=min(count-offset, 200))
        count = reply['count']
        for msg in reply['items']:
            offset += 1
            yield msg

@QtCore.pyqtSlot(bool)
def webLoadFinished(ok):
    if ok:
        # Fix opening in new window on clicks on user photo
        frame = webView.page().mainFrame()
        frame.findFirstElement('.fl_r a').setAttribute('target', '_blank')
    else:
        # TODO: implement this
        pass

@QtCore.pyqtSlot('QString')
def webAuthFinished(auth_response):
    webView.close()
    vk.auth_response(auth_response)
    save_messages(vk)

def save_messages(vk):
    vk_at = VKAttachmentSaver(vk, 'out')

    os.makedirs('out/messages', exist_ok=True)
    messages = []
    for msg in vkDumpMessages(vk, user_id=options.user_id, chat_id=options.chat_id):
        messages.append(msg)
        vk_at.save_message(msg)

    if options.user_id is not None:
        with AtomicWrite('out/messages/id%d.json' % options.user_id) as f:
            json.dump(messages, f)
    else:
        with AtomicWrite('out/messages/chat%d.json' % options.chat_id) as f:
            json.dump(messages, f)

if __name__ == '__main__':
    args = ArgumentParser()
    args.add_argument('-u', '--user', dest='user_id', help='dump messages of user USER_ID', metavar='USER_ID', type=int)
    args.add_argument('-c', '--chat', dest='chat_id', help='dump messages from chat CHAT_ID', metavar='CHAT_ID', type=int)
    options = args.parse_args()
    if (options.user_id is None) == (options.chat_id is None):
        print('Please specify only one of USER_ID and CHAT_ID')
        sys.exit(2)

    logging.basicConfig(level=logging.DEBUG)
    #log_fmt = logging.Formatter('[%(asctime)s] %(name)s: %(message)s')
    #log_stderr = logging.StreamHandler()
    #log_stderr.setLevel(logging.DEBUG)
    #log_stderr.setFormatter(log_fmt)
    #log = logging.getLogger()
    #log.setLevel(logging.DEBUG)

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('MsgDump')

    QtWebKit.QWebSettings.setIconDatabasePath(xdg.BaseDirectory.save_cache_path(app.applicationName()))

    #vk = VK(4824234, ['messages'])
    vk = VK(4820130, ['messages', 'audio'])
    vk.set_params({ 'https' : 1 })

    webView = OAuthDialog(VK.url_redirect)
    webView.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    webView.loadFinished.connect(webLoadFinished)
    webView.authFinished.connect(webAuthFinished, QtCore.Qt.QueuedConnection)
    webView.load(QtCore.QUrl.fromEncoded(vk.auth_url(), QtCore.QUrl.StrictMode))
    webView.show()

    sys.exit(app.exec_())
