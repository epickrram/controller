import dbus
import threading
import time
import Queue

class PlayQueue(object):
    def __init__(self):
        self.tag_queue = []
        self.lock = threading.Lock()

    def enqueue(self, tag, entry_list):
        self.lock.acquire()
        self.tag_queue.append(QueueEntry(tag, entry_list))
        self.lock.release()
        print self.tag_queue

    def peek(self):
        val = None
        self.lock.acquire()
        val = self.tag_queue[0]
        self.lock.release()
        return val

    def pop(self):
        val = None
        self.lock.acquire()
        val = self.tag_queue.pop()
        self.lock.release()
        return val

    def is_empty(self):
        empty = False
        self.lock.acquire()
        empty = len(self.tag_queue) is 0
        self.lock.release()
        return empty

    def get(self):
        val = None
        self.lock.acquire()
        val = frozenset(self.tag_queue)
        self.lock.release()
        return val


class QueueEntry(object):
    def __init__(self, tag, entry_list):
        self.tag = tag
        self.entry_list = entry_list

class Poller(threading.Thread):
    def __init__(self, player):
        self.player = player
        self.running = True
        super(Poller, self).__init__()
        self.daemon = True

    def run(self):
        while(self.running):
            self.player.ping()
            time.sleep(1)

class MusicPlayer(object):
    def __init__(self, play_queue):
        self.state = 'IDLE'
        self.dbus = dbus.Dbus()
        self.play_queue = play_queue
        self.currently_playing = None
        Poller(self).start()

    def get_player_state(self):
        return self.state

    def ping(self):
        if self.state in ['IDLE'] and not self.play_queue.is_empty():
            queue_entry = self.play_queue.peek()
            if len(queue_entry.entry_list) is not 0:
                entry = queue_entry.entry_list.pop()
                self.play(entry.full_path)
                if len(queue_entry.entry_list) is 0:
                    self.play_queue.pop()
        elif self.state == 'PLAYING':
            if(self.get_play_state() != 3):
                self.state = 'IDLE'
                self.currently_playing = None
                
    def get_play_state(self):
        cmd = 'dbus-send --print-reply --type=method_call --dest=com.gnome.mplayer / com.gnome.mplayer.GetPlayState'.split(' ')
        std_out = self.dbus.send_and_get_response(cmd)
        response = self.dbus.get_first_response_value(std_out)
        player_state = int(response)
        return player_state
        

    def get_percent_complete(self):
        cmd = 'dbus-send --print-reply --type=method_call --dest=com.gnome.mplayer / com.gnome.mplayer.GetPercent'.split(' ')
        std_out = self.dbus.send_and_get_response(cmd)
        return 15

    def play(self, media_file):
        cmd = 'dbus-send / com.gnome.mplayer.Open'.split(' ')        
        cmd.append('string:{0}'.format(media_file))
        self.dbus.send(cmd)
        self.currently_playing = media_file.split('/')[-1:][0]
        self.state = 'PLAYING'

    def get_time_remaining(self):
        return 0
