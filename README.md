# Please give me money

I'm destitute.

Especially after all the money I spent on Mountain Dew while I was up until 2AM, reverse engineering SecureW2's JoinNow.

Now if you have the time to worry about all the horrible design decisions of JoinNow, then you're presumably either sitting pretty high atop Maslow's hierarchy of needs and, by extension, a massive mound of money, or you're priorities, like mine, are hopelessly misaligned. Either way, if you like this software and if you have the means, please help me get through college. May I suggest a donation of [$2.59](https://order.maverik.com/menu/604-logan-aggie/products/52433699)?

[Venmo](https://venmo.com/brigham_campbell) | [PayPal](https://paypal.me/brighamcampbell?country.x=US&locale.x=en_US)

Thanks!

# Installation

JoinLater may be installed as a pip package:

`pip install https://github.com/Xeyler/joinlater/releases/download/v0.1.0/joinlater-0.1.0.tar.gz`

# Usage

Run `joinlater` to generate a user private key, user certificate, and CA certificate in the current directory. These keys and certificates, along with the connection details output by the command, can be used to connect to eduroam from any device which supports WPA2 enterprise. JoinLater does not use any information which uniquely identifies the device which runs the script, so the connection credentials can be moved to another device as the user desires.

To renew a user certificate with the USU SecureW2 certificate authority, run `joinlater --renew *.key:*.crt`, supplying the user private key and user certificate. A new private key and user certificate will be output alongside the CA certificate and connection details. Keys and certificates output by the official SecureW2 JoinNow client may also be renewed by supplying a single `*.p12` file, which contains the user private key and user certificate. The JoinNow client saves this information in `~/.joinnow/`.

Run `joinlater --loglevel DEBUG` if you encounter errors or the program otherwise doesn't appear to be working. NOTE: DO NOT SHARE THE VERBOSE OUTPUT OF JOINLATER WITH ANYONE AS IT WILL CONTAIN YOUR PRIVATE KEY AND CERTIFICATE WHICH MAY BE USED TO IMPERSONATE YOU.

# Development/Building

Development depends on Python and Pipenv. After cloning the repo, use `pipenv sync` to install dependencies in a virtual environment, then `pipenv shell` to drop into the virtual environment with all of the project's dependencies available.

 The package is built from source using [build](https://pypi.org/project/build/). Run `python -m build` in the same directory as the `pyproject.toml` file to build.
