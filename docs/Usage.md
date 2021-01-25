<p align="center">fHDHR    <img src="images/logo.ico" alt="Logo"/></p>

---
[Main](README.md)  |  [Setup and Usage](Usage.md)  |  [template](Origin.md)  |  [Credits/Related Projects](Related-Projects.md)
---
**f**un
**H**ome
**D**istribution
**H**iatus
**R**ecreation

---

[Basic Configuration](Config.md)  | [Advanced Configuration](ADV_Config.md) |  [WebUI](WebUI.md)

---

# Author Notes

* All Testing is currently done in Proxmox LXC, Ubuntu 20.04, Python 3.8


# Prerequisites

* A Linux or Mac "Server". Windows currently does not work. A "Server" is a computer that is typically always online.
* Python 3.7 or later.
* Consult [This Page](Origin.md) for additional setup specific to this variant of fHDHR.


# Optional Prerequisites
* If you intend to use Docker, [This Guide](https://docs.docker.com/get-started/) should help you get started. The author of fHDHR is not a docker user, but will still try to help.

fHDHR uses direct connections with video sources by default. Alternatively, you can install and update the [config](Config.md) accordingly. You will need to make these available to your systems PATH, or manually set their path via the config file.

* ffmpeg
* vlc


# Installation

## Linux

* Download the zip, or git clone
* Navigate into your script directory and run `pip3 install -r requirements.txt`
* Copy the included `config.example.ini` file to a known location. The script will not run without this. There is no default configuration file location. [Modify the configuration file to suit your needs.](Config.md)

* Run with `python3 main.py -c=` and the path to the config file.


## Docker
This portion of the guide assumes you are using a Linux system with both docker and docker-compose installed. This (or some variation thereof) may work on Mac or Windows, but has not been tested.

* this guide assumes we wish to use the `~/fhdhr` directory for our install (you can use whatever directory you like, just make the appropriate changes elsewhere in this guide) and that we are installing for template support
* run the following commands to clone the repo into `~/fhdhr/fHDHR_TEMPLATE`
```
cd ~/fhdhr
git clone https://github.com/fHDHR/fHDHR_TEMPLATE.git
```
* create your config.ini file (as described earlier in this guide) in the `~/fhdhr/fHDHR_TEMPLATE` directory
* while still in the `~/fhdhr` directory, create the following `docker-compose.yml` file
```
version: '3'

services:
  template:
    build: ./fHDHR_TEMPLATE
    container_name: template
    network_mode: host
    volumes:
      - ./fHDHR_TEMPLATE/config.ini:/app/config/config.ini
```
* run the following command to build and launch the container
```
docker-compose up --build -d template
```

After a short period of time (during which docker will build your new fHDHR container), you should now have a working build of fHDHR running inside a docker container.

As the code changes and new versions / bug fixes are released, at any point you can pull the latest version of the code and rebuild your container with the following commands:
```
cd ~/fhdhr/fHDHR_TEMPLATE
git checkout master
git pull
cd ~/fhdhr
docker-compose up --build -d template
```
<hr />

You can also run multiple instances of fHDHR to support additional sources by cloning the appropriate repo into your `~/fhdhr` directory and adding the necessary services to the docker-compose file we created above.

* for example, if we also wanted template support, you would clone the template repository:
```
cd ~/fhdhr
git clone https://github.com/fHDHR/fHDHR_TEMPLATE.git
```
* **NOTE**: if you are running multiple services on the same machine, you must change the port in your config.ini file for each one. For example, if template was using the default port of 5004, template cannot also use that port. You must change the port in your template config.ini file to something else (5005, for example).
* add template as a service in your `docker-compose.yml` file
```
version: '3'

services:
  template:
    build: ./fHDHR_TEMPLATE
    container_name: template
    network_mode: host
    volumes:
      - ./fHDHR_TEMPLATE/config.ini:/app/config/config.ini

  template:
    build: ./fHDHR_TEMPLATE
    container_name: template
    network_mode: host
    volumes:
      - ./fHDHR_TEMPLATE/config.ini:/app/config/config.ini
```
* run the following command to build and launch the container
```
docker-compose up --build -d template
```

You can repeat these instructions for as many fHDHR containers as your system resources will allow.

# Setup

Now that you have fHDHR running, You can navigate (in a web browser) to the IP:Port from the configuration step above.

If you did not setup a `discovery_address` in your config, SSDP will be disabled. This is not a problem as clients like Plex can have the IP:Port entered manually!

You can copy the xmltv link from the webUI and use that in your client software to provide Channel Guide information.
