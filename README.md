# FTP Honeypot

An FTP Honeypot designed to simulate an FTP server and log unauthorized access attempts. This project provides a way to monitor and collect data on potential attackers, including geolocation and command interactions.

## Features

Simulates an FTP server to attract unauthorized access.
Logs attack details such as IP address, port, geolocation (city, region, country), and commands.
Sends fake FTP server responses to simulate real behavior.
Interactive mode for detailed logging of commands.
Multi-threaded to handle multiple connections simultaneously.
Graceful shutdown using signal handling.

## Requirements
Python 3.x
Required Python libraries can be installed via:
```
pip install -r requirements.txt
```

## Clone the repository:

```
git clone https://github.com/irhdab/FTP-honeypot.git
cd FTP-honeypot
```

## Run the honeypot server:
```
python main.py --host 0.0.0.0 --port 21 --log-file attack_log.txt --server-name "FTP Server" --interactive
--host: The host to bind the server (default: 0.0.0.0).
--port: The port to listen on (default: 21).
--log-file: The file to log attack details (default: attack_log.txt).
--server-name: Fake server name to display to attackers.
--interactive: Enable interactive mode to log FTP commands.
```
### Running the honeypot on port 21 may require root privileges. Use a different port (e.g., 2121) if not running as root:

```
python main.py --port 2121
Ensure your system complies with local laws and regulations before deploying this honeypot.
```

## Contribution

Contributions are welcome! Feel free to open issues or submit pull requests to improve the project.

### License

This project is licensed under the MIT License.
this repo is forked from [Daepa](https://github.com/suspiciousdaepa/simple-FTP-honeypot)
