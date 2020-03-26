# Jumpbox
Jumpbox is a simple, command line based, menu style interface that allows
centralized SSH device connectivity from a Linux server. It is primarily
designed to be populated via Netbox using GET requests through the API.

### Installation

Clone the Repository:
```bash
  # mkdir -p /opt/jumpbox/ && cd /opt/jumpbox
  # git clone -b master https://github.com/bsakdol/jumpbox.git
```

Modify `jumpbox/netbox_url.py`:
  - replace `<netbox_url>` on line 20 with the URL or IP to your Netbox installation.

Install Requirements:
```bash
  # cd /opt/jumpbox
  # pip install -r requirements.txt
```

Create a Jumpbox user account:
```bash
  # useradd -m -s /opt/jumpbox/jumpbox/main.py jumpbox
  # passwd jumpbox
```
__NOTE: Change the password for the jumpbox user account__

### Run the Jumpbox
SSH to the server with the Jumpbox installed, logging in with the `jumpbox` user.
