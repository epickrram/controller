import BaseHTTPServer
import SimpleHTTPServer
import SocketServer
import sys
import index_builder
import player
import json

class ServerWrapper(BaseHTTPServer.HTTPServer):
    def set_app(self, app):
        self.app = app


class MediaIndexHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        dataLength = int(self.headers['Content-Length'])
        reqData = self.rfile.read(dataLength)
        responseData = {}
        if self.path == '/search':
            searchTerm = json.loads(reqData)
            matching_tags = self.server.app.find(searchTerm['query'])
            copy_list = []
            for tag in matching_tags:
                copy_list.append({'tag': tag, 'size': len(self.server.app.get_entries(tag))})
            responseData = {'matches' : copy_list}
        elif self.path == '/selection':
            tag = json.loads(reqData)['query']
            entries = self.server.app.get_entries(tag)
            self.server.app.enqueue(tag, entries)
        elif self.path == '/status':
            responseData = {'text': self.server.app.music_player.state}

            if self.server.app.music_player.state in ['IDLE', 'PLAYING']:
                play_queue = self.server.app.get_queue()
                renderable = []
                for queue_element in play_queue:
                    elem = {'tag': queue_element.tag, 'fileList': []}
                    for entry in queue_element.entry_list:
                        elem['fileList'].append(entry.label)
                    renderable.append(elem)

                responseData['playQueue'] = renderable
                responseData['currentlyPlaying'] = str(self.server.app.music_player.currently_playing)


        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        responseData = json.dumps(responseData)
        self.wfile.write(responseData);

class App(object):
    def __init__(self, media_index, play_queue, music_player):
        self.media_index = media_index
        self.play_queue = play_queue
        self.music_player = music_player

    def find(self, tag):
        return self.media_index.find(tag)

    def get_entries(self, tag):
        return self.media_index.get_entries(tag)

    def enqueue(self, tag, entries):
        self.play_queue.enqueue(tag, entries)

    def get_queue(self):
        return self.play_queue.get()
    
    def start(self):
        server_address = ('', 8080)
        server = ServerWrapper(server_address, MediaIndexHandler)
        server.set_app(self)
        server.serve_forever()

if __name__ == '__main__':
    media_index = index_builder.MediaIndex(sys.argv[1])
    media_index.build()
    play_queue = player.PlayQueue()
    app = App(media_index, play_queue, player.MusicPlayer(play_queue))
    app.start()
