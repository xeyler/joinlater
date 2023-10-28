# Installation

JoinLater may be installed as a pip package:

`pip install https://github.com/Xeyler/joinlater/releases/download/v0.2.1/joinlater-0.2.1.tar.gz`

## Debian-based distros

The following commands will get you started:

```
# Install pip and venv
sudo apt update
sudo apt install python3-pip python3-venv -y

# Make a virtual environment to avoid conflicting with apt
mkdir ~/.joinlater
cd ~/.joinlater
python3 -m venv joinlater
source joinlater/bin/activate

# Installation
pip install https://github.com/Xeyler/joinlater/releases/download/v0.2.1/joinlater-0.2.1.tar.gz
joinlater
```

Follow the instructions printed to the terminal. After your certs are generated, your network connection should be configured automaticaly if your distro uses NetworkManager. If not, you'll need to configure your network software manually by providing the identity and domain which are printed to the terminal, as well as the file paths to `ca.crt`,  `ident.crt`, and  `ident.key`.

## Arch-based distros

If you're using Arch, you probably don't need your hand held.

# Usage

Run `joinlater` to generate a user private key, user certificate, and CA certificate in the current directory. These keys and certificates, along with the connection details output by the command, can be used to connect to eduroam from any device which supports WPA2 enterprise. JoinLater does not use any information which uniquely identifies the device which runs the script, so the connection credentials can be moved to another device as the user desires.

To renew a user certificate with the USU SecureW2 certificate authority, run `joinlater --renew *.key:*.crt`, supplying the user private key and user certificate. A new private key and user certificate will be output alongside the CA certificate and connection details. Keys and certificates output by the official SecureW2 JoinNow client may also be renewed by supplying a single `*.p12` file, which contains the user private key and user certificate. The JoinNow client saves this information in `~/.joinnow/`.

# Development/Building

Development depends on Python and Pipenv. After cloning the repo, use `pipenv sync` to install dependencies in a virtual environment, then `pipenv shell` to drop into the virtual environment with all of the project's dependencies available.

The package is built from source using [build](https://pypi.org/project/build/). Run `python -m build` in the same directory as the `pyproject.toml` file to build.
