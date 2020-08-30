from .base import _ZoomAPIBase
from .phone import PhoneMixin
from .users import UserMixin


class ZoomAPIClient(PhoneMixin, UserMixin, _ZoomAPIBase):
    pass