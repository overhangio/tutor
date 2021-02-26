# Silence overly verbose warnings
import logging
import warnings
# Ignore if these warning types exist.
try:
    from django.utils.deprecation import RemovedInDjango30Warning, RemovedInDjango31Warning
    warnings.simplefilter('ignore', RemovedInDjango30Warning)
    warnings.simplefilter('ignore', RemovedInDjango31Warning)
except ImportError:
    pass

try:
    from rest_framework import RemovedInDRF310Warning, RemovedInDRF311Warning
    warnings.simplefilter('ignore', RemovedInDRF310Warning)
    warnings.simplefilter('ignore', RemovedInDRF311Warning)
except ImportError:
    pass

warnings.simplefilter('ignore', DeprecationWarning)
