import socket
import datetime
import socket
import requests
from ip2geotools.databases.noncommercial import DbIpCity
from geopy.distance import distance


def log_attack(ip_address, port, city, region, country):
   timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   with open("attack_log.txt", "a") as log_file:
       log_file.write(f"Timestamp: {timestamp}, Attacker IP: {ip_address}, Port: {port}, Location: {city}, {region}, {country} \n")


def honeypot():


   def locate(ip):
       res = DbIpCity.get(ip, api_key="free")
       log_attack(addr[0], addr[1], res.city, res.region, res.country)


   host = '0.0.0.0'
   port = 21  # FTP port number


   with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
       s.bind((host, port))
       s.listen()


       print(f'Honeypot is listening on {host}:{port}')


       while True:
           conn, addr = s.accept()
           print(f'Connection from {addr[0]}:{addr[1]}')


           locate(addr[0])
           # Logs the attack in text file


           # Sends a fake welcome message
           fake_response = b"220 Welcome to the daepa's server.\r\n"
           conn.sendall(fake_response)


           # Close connection
           conn.close()


if __name__ == "__main__":
   honeypot()
