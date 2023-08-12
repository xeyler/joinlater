import requests
import re

from asn1crypto.cms import ContentInfo
from xml.etree import ElementTree

XPATH_ORGANIZATION_TITLE = 'organization/name'
XPATH_ORGANIZATION_UID = 'organization/UID'
XPATH_ORGANIZATION_PROFILE_UUID = \
    'configurations/deviceConfiguration/profileUUID'
XPATH_ORGANIZATION_NAME = 'configurations/deviceConfiguration/name'

# SecureW2 instances that don't use WPA2-Enterprise likely won't have these:
XPATH_PKI_ENDPOINT_URL = \
    'configurations/deviceConfiguration/actions/action/credentials/' \
    'TLSEnrollment/URL'
XPATH_CA_CERTIFICATE = \
    'configurations/deviceConfiguration/actions/action/certificate/data'
XPATH_EAP_SERVER = \
    'configurations/deviceConfiguration/actions/action/WLANProfile/EAP/' \
    'serverNames'

# SecureW2 instances that don't use SSO will not have this:
XPATH_SSO_URL = \
    'configurations/deviceConfiguration/actions/action/credentials/' \
    'TLSEnrollment/webSSOUrl'


class SecureW2Config():
    @classmethod
    def from_URL(cls, config_url):
        # TODO: Break out HTTP GET into more generic securew2 function
        signed_cloudconfig_file = requests.get(config_url).content

        return cls(signed_cloudconfig_file)

    @classmethod
    def from_file(cls, config_file):
        with open(config_file, mode='rb') as file:
            return cls(file.read())

    def __init__(self, signed_cloudconfig):
        # SecureW2 needs help. There's no reason to be signing these files.
        # It's a huge hassle. Otherwise, there would be no need for asn1crypto.
        # Anyways, we're just loading the signed config into a cms data
        # structure which then allows us to extract the PKCS7 message content.
        # This is the most straightforward way I could find to do it and yet
        # it's arguably the most hideous code in this project... *sigh* At
        # least I didn't have to resort to calling openssl via os.exec like
        # SecureW2 does. Ridiculous.
        cms = ContentInfo.load(signed_cloudconfig)
        xml_bytes = cms['content']['encap_content_info']['content'].native

        xml = xml_bytes.decode('utf-8')

        # Okay look, I'm not proud of this. Editing config files with regex
        # isn't the sort of thing that should be happening client-side in
        # production. But SecureW2 does this in their own client too. It makes
        # me wonder why they use XML at all. Why not JSON??
        no_namespace_xml = re.sub('xmlns="(.*?)"', '', xml)

        xml = ElementTree.fromstring(no_namespace_xml)

        # Parse XML into variables
        self.organization_title = xml.find(XPATH_ORGANIZATION_TITLE).text
        self.organization_uid = xml.find(XPATH_ORGANIZATION_UID).text
        self.organization_profile_uuid = \
            xml.find(XPATH_ORGANIZATION_PROFILE_UUID).text
        self.organization_name = xml.find(XPATH_ORGANIZATION_NAME).text

        self.pki_endpoint_url = xml.find(XPATH_PKI_ENDPOINT_URL).text
        self.ca_certificate = xml.find(XPATH_CA_CERTIFICATE).text
        self.eap_server = xml.find(XPATH_EAP_SERVER).text

        self.sso_url = xml.find(XPATH_SSO_URL).text
