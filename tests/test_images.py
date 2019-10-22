import unittest
from tutor import images


class ImagesTests(unittest.TestCase):
    def test_get_tag(self):
        config = {
            "DOCKER_IMAGE_OPENEDX": "openedx",
            "DOCKER_IMAGE_OPENEDX_DEV": "openedxdev",
            "DOCKER_REGISTRY": "registry/",
        }
        self.assertEqual("registry/openedx", images.get_tag(config, "openedx"))
        self.assertEqual("registry/openedxdev", images.get_tag(config, "openedx-dev"))
