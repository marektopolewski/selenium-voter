import subprocess
import time

def get_global_ip():
    temp = subprocess.run(args=["curl", "ifconfig.me", "/dev/null"], capture_output=True)
    return temp.stdout

class VpnConnector:

    MAX_RETRIES = 5
    MAX_SECONDS_DELAY_TO_CONNECT = 5

    def __init__(self, config) -> None:
        self.config = config
        self.process = None
    
    def __del__(self) -> None:
        subprocess.run(args=["sudo", "killall", "openvpn"], stdout=subprocess.PIPE)
    
    def active(self):
        return self.process.poll() == None if self.process else False
    
    def open(self) -> None:
        attempt = 0
        while attempt < VpnConnector.MAX_RETRIES:
            ret = self._open()
            if ret:
                VpnConnector._print("opened: {}".format(self.config))
                return
            attempt += 1
            time.sleep(2 ** attempt)
    
    def close(self) -> None:
        self.process.terminate()
        while self.process.poll() == None:
            pass
        subprocess.run(args=["sudo", "killall", "openvpn"], stdout=subprocess.PIPE)
        VpnConnector._print("closed: {}".format(self.config))
    
    def _open(self) -> None:
        config = "/usr/local/etc/openvpn/ovpn_udp/" + self.config
        cmd = ["sudo", "openvpn", "--config", config, "--auth-user-pass", "auth.txt"]
        self.process = subprocess.Popen(args=cmd, stdout=subprocess.PIPE)
        start_time = time.time()
        while time.time() - start_time < VpnConnector.MAX_SECONDS_DELAY_TO_CONNECT:
            line = str(self.process.stdout.readline())
            if self.process.poll() is not None:
                VpnConnector._print("failed to open, process exited")
                return False
            if "process exiting" in line:
                VpnConnector._print("failed to open, VPN connection refused")
                return False
            if "Initialization Sequence Completed" in line:
                return True
        return False
    
    def _print(msg) -> None:
        print("[VpnConnector] {}".format(msg))
