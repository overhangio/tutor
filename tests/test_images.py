import unittest
from tutor import images
from tutor.types import Config


class ImagesTests(unittest.TestCase):
    def test_get_tag(self) -> None:
        config: Config = {
            "DOCKER_IMAGE_OPENEDX": "registry/openedx",
            "DOCKER_IMAGE_OPENEDX_DEV": "registry/openedxdev",
        }
        self.assertEqual("registry/openedx", images.get_tag(config, "openedx"))
        self.assertEqual("registry/openedxdev", images.get_tag(config, "openedx-dev"))
