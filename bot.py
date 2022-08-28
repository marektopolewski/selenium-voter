from servers_manager import ServersManager 
from vpn_connector import VpnConnector, get_global_ip
from voter import Voter

from webdriver_manager.chrome import ChromeDriverManager
import time

def cast_vote(voter: Voter, page: str, stars: int) -> float:
    page_loaded = voter.open(page)
    if not page_loaded:
        print("Could not open target website <{}>".format(page))
        return 0.0
    print("Restaurant page opened <{}>".format(page))
    rating = voter.vote(stars)
    print("New rating is {}".format(rating))
    return rating

chrome_driver_path = ChromeDriverManager().install()
servers = ServersManager("/usr/local/etc/openvpn/ovpn_udp")
it_counter = 0

while True:
    it_counter += 1
    print("\n{} Iteration {}/100 {}".format("-" * 30, it_counter, "-" * 30))

    # Connect to VPN
    server = servers.get_file()
    vpn = VpnConnector(server)
    ip_no_proxy = get_global_ip()
    vpn.open()
    if not vpn.active():
        print("Error, VPN not active, skipping..")
        continue
    while ip_no_proxy == get_global_ip():
        time.sleep(1)
    print("New IP received: {}".format(get_global_ip()))

    # Open main website
    voter = Voter(chrome_driver_path)
    voter.open(dismiss_cookies=True)

    mlyn_rating = cast_vote(voter, "modry-mlyn", 5)
    # ryba_rating = cast_vote(voter, "bar-pod-ryba", 1)
    # if mlyn_rating != 0.0 and ryba_rating != 0.0 and ryba_rating < mlyn_rating:
    #     print("{}".format("-" * 80))
    #     print("{} SUCESS, modry mlyn is back on the top {}".format("-" * 20, "-" * 21))
    #     print("{}".format("-" * 80))
    #     break

    # Close VPN connection
    vpn.close()
    if vpn.active():
        print("Error, VPN not disconnected")
    while ip_no_proxy != get_global_ip():
        time.sleep(1)
    print("Old IP returned: {}".format(ip_no_proxy))
