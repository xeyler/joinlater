# Installation

JoinLater may be installed as a pip package:

`pip install https://github.com/Xeyler/joinlater/releases/download/v0.2.0/joinlater-0.2.0.tar.gz`

## Debian-based distros

The following commands will get you started:

```
# Dependencies
sudo apt update
sudo apt install python3-pip python3-venv -y
mkdir ~/.joinlater && cd ~/.joinlater

# Make a virtual environment to avoid conflicting with apt
python3 -m venv joinlater
source joinlater/bin/activate

# Installation
pip install https://github.com/Xeyler/joinlater/releases/download/v0.2.0/joinlater-0.2.0.tar.gz
joinlater
```

Follow the instructions printed to the terminal. After your certs are generated, you'll need to edit your eduroam connection settings. Here's how it's done on Debian running KDE.

![KDE Debian](/img/KDE.png)

Using `ls -a` in your home folder will help you find the `.joinlater` directory and the appropriate paths to the User certificate, CA certificate, and Private key. The private key password doesn't matter, so you can put anything in that box (NetworkManager requires that it's filled for some reason).

Here's how it's done on Linux Mint Cinnamon:

![Cinnamon](/img/Cinnamon.png)

Largely the same as the previous example. You'll also need to add a user key password, but just like with KDE it doesn't matter. You may get an alert that says "Unencrypted private keys are insecure" but you can ignore it.

## Arch-based distros

If you're using Arch, you probably don't need your hand held.

# Usage

Run `joinlater` to generate a user private key, user certificate, and CA certificate in the current directory. These keys and certificates, along with the connection details output by the command, can be used to connect to eduroam from any device which supports WPA2 enterprise. JoinLater does not use any information which uniquely identifies the device which runs the script, so the connection credentials can be moved to another device as the user desires.

To renew a user certificate with the USU SecureW2 certificate authority, run `joinlater --renew *.key:*.crt`, supplying the user private key and user certificate. A new private key and user certificate will be output alongside the CA certificate and connection details. Keys and certificates output by the official SecureW2 JoinNow client may also be renewed by supplying a single `*.p12` file, which contains the user private key and user certificate. The JoinNow client saves this information in `~/.joinnow/`.

# Development/Building

Development depends on Python and Pipenv. After cloning the repo, use `pipenv sync` to install dependencies in a virtual environment, then `pipenv shell` to drop into the virtual environment with all of the project's dependencies available.

The package is built from source using [build](https://pypi.org/project/build/). Run `python -m build` in the same directory as the `pyproject.toml` file to build.
