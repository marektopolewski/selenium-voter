
import os
from random import randint
import time

class ServersManager:

    TEMP_DIR = "./.tmp"
    SERVERS_PATH_OLD = os.path.join(TEMP_DIR, "server_list_old")
    SERVERS_PATH_NEW = os.path.join(TEMP_DIR, "server_list")

    def __init__(self, path) -> None:
        self.servers = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        if not os.path.exists(ServersManager.TEMP_DIR):
            os.mkdir(ServersManager.TEMP_DIR)

        if os.path.exists(ServersManager.SERVERS_PATH_OLD):
            os.remove(ServersManager.SERVERS_PATH_OLD)

        if not os.path.exists(ServersManager.SERVERS_PATH_NEW):
            open(ServersManager.SERVERS_PATH_NEW, "a").close()

        os.rename(ServersManager.SERVERS_PATH_NEW, ServersManager.SERVERS_PATH_OLD)
        old_used_servers = open(ServersManager.SERVERS_PATH_OLD, "r")
        self.used_servers = open(ServersManager.SERVERS_PATH_NEW, "a")

        for entry in old_used_servers.read().splitlines():
            server, date = entry.split()
            if int(date) - time.time() < 24 * 60 * 60:
                self.servers.remove(server)
                self._write_server(server, date)
        
    def get_file(self) -> str:
        assert len(self.servers) > 0
        server_idx = randint(0, len(self.servers) - 1)
        server = self.servers[server_idx]
        self.servers.pop(server_idx)
        if self.used_servers.closed:
            self.used_servers = open(ServersManager.SERVERS_PATH_NEW, "a")
        timestamp = str(int(time.time()))
        self._write_server(server, timestamp)
        return server
    
    def _write_server(self, server: str, date: str) -> None:
        self.used_servers.write(" ".join((server, date)) + "\n")
