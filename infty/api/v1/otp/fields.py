from rest_framework import fields

from captcha.helpers import captcha_image_url


class CaptchaImageField(fields.CharField):
    def to_representation(self, value):
        result = super().to_representation(value)
        return captcha_image_url(result)
