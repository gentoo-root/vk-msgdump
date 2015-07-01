import os, os.path
import requests

from atomicwrite import AtomicWrite

def fsescape(path):
    return path.replace('/', '\u2215')

class VKUnsupportedAttachmentError(Exception):
    pass

class VKAttachmentSaver(object):
    def __init__(self, vk, path):
        self._handlers = {
            'photo': self.save_photo,
            'video': self.save_video,
            'audio': self.save_audio,
            'doc': self.save_doc,
            'wall': self.save_wall,
            'wall_reply': self.save_wall_reply,
            'sticker': self.save_sticker,
            'gift': self.save_gift,
            'link': self.save_link,
            }

        self._vk = vk
        
        self._path = path
        os.makedirs(self._path, exist_ok=True)

        self._session = requests.Session()

    def save(self, attachment):
        at_type = attachment['type']
        if at_type not in self._handlers:
            raise VKUnsupportedAttachmentError('Attachment type %s is not supported' % attachment['type'])
        self._handlers[at_type](attachment[at_type])

    def save_message(self, message):
        if 'attachments' in message:
            for attachment in message['attachments']:
                self.save(attachment)
        if 'fwd_messages' in message:
            for fwd_message in message['fwd_messages']:
                self.save_message(fwd_message)

    def _download(self, url, filename):
        if not os.path.exists(filename):
            if url:
                reply = self._session.get(url)
                reply.raise_for_status()
                with AtomicWrite(filename, binary=True) as f:
                    f.write(reply.content)
            else:
                open(filename, 'wb').close()

    def save_photo(self, photo):
        path = self._path + '/photo/{owner_id:d}/{photo_id:d}'.format(owner_id=photo['owner_id'], photo_id=photo['id'])
        os.makedirs(path, exist_ok=True)
        for size in 75, 130, 604, 807, 1280, 2560:
            name = 'photo_{size:d}'.format(size=size)
            if name in photo:
                url = photo[name]
                self._download(url, path + '/{name:s}.jpg'.format(name=name))

    def save_video(self, video):
        path = self._path + '/video/{owner_id:d}/{video_id:d}'.format(owner_id=video['owner_id'], video_id=video['id'])
        os.makedirs(path, exist_ok=True)
        with AtomicWrite(path + '/{title:s}.txt'.format(title=fsescape(video['title']))) as f:
            f.write(video['description'])
        if 'files' in video:
            for name in video['files']:
                url = video['files'][name]
                self._download(url, path + '/{name:s}'.format(name=name))

    def save_audio(self, audio):
        path = self._path + '/audio/{owner_id:d}/{audio_id:d}'.format(owner_id=audio['owner_id'], audio_id=audio['id'])
        os.makedirs(path, exist_ok=True)
        self._download(audio['url'], path + '/{artist:s} - {title:s}.mp3'.format(artist=fsescape(audio['artist']), title=fsescape(audio['title'])))
        if 'lyrics_id' in audio:
            lyrics = self._vk.audio.getLyrics(lyrics_id=audio['lyrics_id'])['text']
            with AtomicWrite(path + '/lyrics.txt') as f:
                f.write(lyrics)

    def save_doc(self, doc):
        path = self._path + '/doc/{owner_id:d}/{doc_id:d}'.format(owner_id=doc['owner_id'], doc_id=doc['id'])
        # TODO: exist_ok should be False for {doc_id} dir
        os.makedirs(path, exist_ok=True)
        self._download(doc['url'], path + '/{title:s}'.format(title=doc['title']))

    def save_wall(self, wall):
        pass

    def save_wall_reply(self, wall_reply):
        pass

    def save_sticker(self, sticker):
        pass

    def save_gift(self, gift):
        pass

    def save_link(self, link):
        pass
