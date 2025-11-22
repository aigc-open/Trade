from urllib.parse import quote, unquote, urlencode
import logging
import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class HarborClient(object):
    def __init__(self, host, user, password, protocol="http", verify_ssl_cert=False):
        self.host = host
        self.user = user
        self.password = password
        self.protocol = protocol
        self.headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
        self.auth = HTTPBasicAuth(user, password)
        self.based_url = '{}://{}'.format(self.protocol, self.host)
        self.verify_ssl_cert = verify_ssl_cert
        if self.verify_ssl_cert:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def copy_image(self, project_name, repository_name, from_):
        path = f"{self.protocol}://{self.host}/api/v2.0/projects/{project_name}/repositories/{quote(quote(repository_name, 'utf8'), 'utf8')}/artifacts?from={from_}"
        response = requests.post(path, headers=self.headers, auth=self.auth, verify=self.verify_ssl_cert)
        return response


def test():
    client = HarborClient("harbor.uat.xxxx.cc", user="labcloud", password="Labcloud123!")

    res = client.copy_image(
        project_name="f9671ac0-c158-4763-8a97-e1cdc69517af",
        repository_name="dfb63a11-f0ff-4ac2-b536-e9dee8cbc652/ljc-test2",
        from_="f9671ac0-c158-4763-8a97-e1cdc69517af/dfb63a11-f0ff-4ac2-b536-e9dee8cbc652/image803@sha256:a5a5b9748fe53d3356c1c70171e804e6f4931fd3ec81f0befbefb406fda95d81"
    )
    print(res.text)


if __name__ == '__main__':
    test()
