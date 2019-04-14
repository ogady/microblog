from django.db import models


class BaseManager(models.Manager):
    def get_or_none(self, **kwargs):
        """
        検索にヒットすればそのモデルを、しなければNoneを返す。
        """
        try:
            return self.get_queryset().get(**kwargs)
        except self.model.DoesNotExist:
            return None
