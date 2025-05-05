import socket
import datetime
import requests
import argparse
import threading
import time
from ip2geotools.databases.noncommercial import DbIpCity
from geopy.distance import distance


def log_attack(ip_address, port, city, region, country, log_file="attack_log.txt"):
    """Log attack details to a file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as file:
        file.write(f"Timestamp: {timestamp}, Attacker IP: {ip_address}, Port: {port}, Location: {city}, {region}, {country}\n")
    
    # Also print to console for real-time monitoring
    print(f"[{timestamp}] Attack logged from {ip_address}:{port} ({city}, {region}, {country})")


def handle_connection(conn, addr, options):
    """Handle an individual connection to the honeypot."""
    try:
        print(f'Connection received from {addr[0]}:{addr[1]}')
        
        # Get geolocation data
        try:
            res = DbIpCity.get(addr[0], api_key="free")
            city = res.city if res.city else "Unknown"
            region = res.region if res.region else "Unknown"
            country = res.country if res.country else "Unknown"
        except Exception as e:
            print(f"Error getting geolocation: {e}")
            city, region, country = "Unknown", "Unknown", "Unknown"
        
        # Log the connection attempt
        log_attack(addr[0], addr[1], city, region, country, options.log_file)
        
        # Send fake welcome message
        conn.sendall(f"220 Welcome to {options.server_name} FTP server.\r\n".encode())
        
        # Simulate actual FTP server behavior for a more convincing honeypot
        if options.interactive:
            try:
                # Set a timeout for receiving data
                conn.settimeout(60)
                
                while True:
                    data = conn.recv(1024).decode('utf-8', errors='ignore').strip()
                    if not data:
                        break
                    
                    print(f"Received command: {data}")
                    
                    # Log commands separately
                    with open(f"{options.log_file}.commands", "a") as cmd_log:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cmd_log.write(f"[{timestamp}] {addr[0]}:{addr[1]} - {data}\n")
                    
                    # Handle common FTP commands
                    if data.upper().startswith("USER"):
                        conn.sendall(b"331 User name okay, need password.\r\n")
                    elif data.upper().startswith("PASS"):
                        conn.sendall(b"530 Authentication failed.\r\n")
                    elif data.upper() == "QUIT":
                        conn.sendall(b"221 Goodbye.\r\n")
                        break
                    else:
                        conn.sendall(b"500 Command not understood.\r\n")
            
            except socket.timeout:
                print(f"Connection from {addr[0]}:{addr[1]} timed out")
            except Exception as e:
                print(f"Error handling connection: {e}")
    
    finally:
        # Always ensure the connection is closed
        conn.close()


def honeypot(options):
    """Run the FTP honeypot."""
    host = options.host
    port = options.port
    
    print(f"Starting FTP honeypot on {host}:{port}")
    print(f"Logging attacks to {options.log_file}")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Allow port reuse to avoid "address already in use" errors
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s.listen(5)  # Accept up to 5 simultaneous connections
            
            print(f"Honeypot is listening on {host}:{port}")
            
            # Create a shutdown mechanism
            stop_event = threading.Event()
            
            def signal_handler(sig, frame):
                print("\nShutting down honeypot...")
                stop_event.set()
                
            # Register signal handlers
            import signal
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # Accept connections until stopped
            while not stop_event.is_set():
                try:
                    # Use a timeout to check for stop_event periodically
                    s.settimeout(1.0)
                    conn, addr = s.accept()
                    
                    # Handle each connection in a separate thread
                    thread = threading.Thread(
                        target=handle_connection,
                        args=(conn, addr, options)
                    )
                    thread.daemon = True
                    thread.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error accepting connection: {e}")
                    if not stop_event.is_set():
                        time.sleep(1)  # Brief pause before retrying
            
            print("Honeypot shutdown complete")
            
    except PermissionError:
        print(f"Error: Cannot bind to port {port}. You may need root privileges.")
        print("Try: sudo python honeypot.py")
    except Exception as e:
        print(f"Error starting honeypot: {e}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="FTP Honeypot")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=21, help="Port to listen on (default: 21)")
    parser.add_argument("--log-file", default="attack_log.txt", help="Log file (default: attack_log.txt)")
    parser.add_argument("--server-name", default="FTP Server", help="Fake server name to display")
    parser.add_argument("--interactive", action="store_true", help="Enable interactive mode to respond to FTP commands")
    return parser.parse_args()


if __name__ == "__main__":
    options = parse_arguments()
    honeypot(options)
