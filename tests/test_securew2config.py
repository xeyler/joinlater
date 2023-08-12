from joinlater.securew2config import SecureW2Config
import glob
import pytest

CLOUDCONFIGS = [ config for config in glob.glob('**/*.cloudconfig', recursive=True) ]

@pytest.fixture(params=CLOUDCONFIGS)
def cloudconfigs(request):
    return request.param

def test_securew2config(cloudconfigs):
        print(cloudconfigs)
        SecureW2Config.from_file(cloudconfigs)