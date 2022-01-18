import sys
import re

#from time import sleep
from random import sample
from mpd import MPDClient, MPDError, CommandError



class ClientError(Exception):
    """Fatal error in client."""


class Client():
    def __init__(self, host='/var/run/mpd/socket', port='6600', password=None):
        self._host = host
        self._port = port
        self._password = password
        self._client = MPDClient()

    def connect(self):
        try:
            self._client.connect(self._host)
        # Catch socket errors
        except IOError as err:
            #err_num, strerror = err.strerror
            raise ClientError("Could not connect to '%s': %s" %
                              (self._host, err.strerror))

        # Catch all other possible errors
        # ConnectionError and ProtocolError are always fatal.  Others may not
        # be, but we don't know how to handle them here, so treat them as if
        # they are instead of ignoring them.
        except MPDError as err:
            raise ClientError("Could not connect to '%s': %s" %
                              (self._host, err))

        if self._password:
            try:
                self._client.password(self._password)

            # Catch errors with the password command (e.g., wrong password)
            except CommandError as err:
                raise ClientError("Could not connect to '%s': "
                                  "password command failed: %s" %
                                  (self._host, err))

            # Catch all other possible errors
            except (MPDError, IOError) as err:
                raise ClientError("Could not connect to '%s': "
                                  "error with password command: %s" %
                                  (self._host, err))

    def disconnect(self):
        # Try to tell MPD we're closing the connection first
        try:
            self._client.close()

        # If that fails, don't worry, just ignore it and disconnect
        except (MPDError, IOError):
            pass

        try:
            self._client.disconnect()

        # Disconnecting failed, so use a new client object instead
        # This should never happen.  If it does, something is seriously broken,
        # and the client object shouldn't be trusted to be re-used.
        except (MPDError, IOError):
            self._client = MPDClient()

    def title_from_file(self, file):
        f_name = 'No Filename'
        if not file == None:
            f_split = re.split('\/',file)
            f_name = f_split[len(f_split) -1]
        return f_name

    def poll(self):
        try:
            song = self._client.currentsong()

        # Couldn't get the current song, so try reconnecting and retrying
        except (MPDError, IOError):
            # No error handling required here
            # Our disconnect function catches all exceptions, and therefore
            # should never raise any.
            self.disconnect()

            try:
                self.connect()

            # Reconnecting failed
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)
            try:
                song = self._client.currentsong()

            # Failed again, just give up
            except (MPDError, IOError) as err:
                raise ClientError("Couldn't retrieve current song: %s" % err)

        # Hurray!  We got the current song without any errors!
        if song.get('title') == None:
            song['title'] = self.title_from_file(song.get('file'))
        return song

    def status(self):
        try:
            status = self._client.status()

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                status = self._client.status()

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't retrieve status: %s" % err)

        return status

    def stop(self):
        try:
            self._client.stop()

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                self._client.stop()

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't retrieve status: %s" % err)
    
    def next(self):
        try:
            self._client.next()

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                self._client.next()

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't skip next: %s" % err)

    def previous(self):
        try:
            self._client.previous()

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                self._client.previous()

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't skip previous: %s" % err)

    def seek(self, song, pos):
        try:
            self._client.seek(song, pos)

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                self._client.seek(song, pos)

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't skip next: %s" % err)
    def replayGain(self, val):
        try:
            self._client.replay_gain_mode(val)

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                self._client.replay_gain_mode('auto')

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't skip next: %s" % err)
    def playPause(self):
        try:
            state = self._client.status().get('state')
            if state == 'play':
                self._client.pause()
            else:
                self._client.play()

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                state = self._client.status().get('state')
                if state == 'play':
                    self._client.pause()
                else:
                    self._client.play()

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't skip previous: %s" % err)

    def pause(self):
        try:
            state = self._client.status().get('state')
            if state == 'play':
                self._client.pause()

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                state = self._client.status().get('state')
                if state == 'play':
                    self._client.pause()

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't skip previous: %s" % err)

    def random_playlist(self, num):
        def add_songs(songs):
            for song in songs:
                info = self._client.lsinfo(song.get('file'))
                duration = int(info[0].get('time'))
                if duration > 120:
                    self._client.add(song.get('file'))
            self._client.play(0)
        try:
            self._client.clear()
            songs = sample(self._client.list('file'), num)
            add_songs(songs)
            
        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)
            try:
                self._client.clear()
                songs = sample(self._client.list('file'), num)
                add_songs(songs)
            except (MPDError, IOError) as err:
                raise ClientError("Couldn't clear list: %s" % err)
    
    def find(self, *args):
        try:
            find_list = self._client.find(*args)#[, filtertype, filterwhat, ..., "group", grouptype, ...])

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                find_list = self._client.list(*args)

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't perform find: %s" % err)
        
        return find_list
    
    def get_list(self, *args):

        try:
            type_list = self._client.list(*args)
        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                type_list = self._client.list(*args)

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't get list: %s" % err)
        
        return type_list

    def get_playlistinfo(self, start_end):#[SONGPOS] | [START:END]):
        try:
            type_list = self._client.playlistinfo(start_end) #[SONGPOS] | [START:END]):

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                type_list = self._client.list(type)

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't get playlist info: %s" % err)
        
        return type_list

    def search(self, *args):#[SONGPOS] | [START:END]):
        try:
            type_list = self._client.search(*args)#cmd) #[SONGPOS] | [START:END]):

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                type_list = self._client.search(*args)#cmd)

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't search: %s" % err)
        
        return type_list
    
    def playlistinfo(self):#[SONGPOS] | [START:END]):
        try:
            playlist = self._client.playlistinfo()#cmd) #[SONGPOS] | [START:END]):

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                playlist = self._client.playlistinfo()#cmd)

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't get playlist: %s" % err)
        
        return playlist

    def add_id(self, *args):
        try:
            song_id = self._client.addid(*args)

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                song_id = self._client.addid(*args)

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't add id: %s" % err)
        return song_id

    def listfiles(self, path):
        try:
            f_list = self._client.listfiles(path)

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                f_list = self._client.listfiles(path)

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't list files: %s" % err)
        return f_list

    def lsinfo(self, path):
        try:
            f_list = self._client.lsinfo(path)

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                f_list = self._client.lsinfo(path)

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't list files: %s" % err)
        return f_list

    def listallinfo(self, path):
        try:
            f_list = self._client.listallinfo(path)

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                f_list = self._client.listallinfo(path)

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't list files: %s" % err)
        return f_list

    def deleteid(self, song_id):
        try:
            self._client.deleteid(song_id)

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                self._client.deleteid(song_id)

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't get artisis: %s" % err)

    
    def prio_id(self, song_id):
        try:
            self._client.prioid(1, song_id)

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                self._client.prioid(1, song_id)#cmd)

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't get artisis: %s" % err)

    def shuffle(self):
        try:
            self._client.shuffle()

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                self._client.shuffle()

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't shuffle playlist: %s" % err)

    def random(self, value):
        try:
            self._client.random(value)

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                self._client.random(value)

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't shuffle playlist: %s" % err)

    def clear(self):
        try:
            self._client.clear()

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                self._client.clear()

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't clear playlist: %s" % err)

    def list_playlists(self):
        try:
            playlists  = self._client.listplaylists()
        
        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                playlists = self._client.listplaylists()

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't list playlists: %s" % err)
        return playlists

    def load_playlist(self, p_list):
        try:
            self._client.load(p_list)

        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                self._client.load(p_list)

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't load playlist: %s" % err)


def main():
    client = Client()
    client.connect()

    #while True:
    #    client.poll()
    #    sleep(3)


if __name__ == "__main__":

    try:
        main()

    # Catch fatal client errors
    except ClientError as err:
        print("Fatal client error: %s" % err, file=sys.stderr)
        sys.exit(1)

    # Catch all other non-exit errors
    except Exception as err:
        print("Unexpected exception: %s" % err, file=sys.stderr)
        sys.exit(1)

    # Catch the remaining exit errors
    except:
        sys.exit(0)
