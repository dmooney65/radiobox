import sys
#from time import sleep
from random import sample
from mpd import MPDClient, MPDError, CommandError



class ClientError(Exception):
    """Fatal error in client."""


class Client():
    def __init__(self, host="localhost", port="6600", password=None):
        self._host = host
        self._port = port
        self._password = password
        self._client = MPDClient()

    def connect(self):
        try:
            self._client.connect(self._host, self._port)
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
                                  "password commmand failed: %s" %
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
        #print(song)
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

    def random(self):
        try:
            self._client.clear()
            songs = sample(self._client.list('file'), 250)
            for song in songs:
                self._client.add(song)
            self._client.play(0)
        except (MPDError, IOError):
            self.disconnect()
            try:
                self.connect()
            except ClientError as err:
                raise ClientError("Reconnecting failed: %s" % err)

            try:
                self._client.clear()
                songs = sample(self._client.list('file'), 250)
                for song in songs:
                    self._client.add(song)
                self._client.play(0)

            except (MPDError, IOError) as err:
                raise ClientError("Couldn't skip previous: %s" % err)


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
