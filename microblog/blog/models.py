from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.dispatch import receiver


# Create your models here.
class Tag(models.Model):
    """ タグ """

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Blog(models.Model):
    """ ポスト"""
    content = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='anicolleblog', blank=True, null=True)
    anime_id = models.IntegerField(blank=True, null=True)
    anime = models.CharField(max_length=200, blank=True, null=True)
    posted_date = models.DateTimeField(auto_now_add=True)
    tag = models.ManyToManyField(Tag, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    like_num = models.IntegerField(default=0)

    class Meta:
        ordering = ['-posted_date']

    def __str__(self):
        return self.content


class Comment(models.Model):
    """ コメント """
    content = models.TextField('コメント')
    post = models.ForeignKey(Blog, verbose_name='対象記事', on_delete=models.CASCADE)
    # selfはForrignKey(Comment)を意味する。
    parent = models.ForeignKey('self', verbose_name='親コメント', null=True, blank=True, on_delete=models.CASCADE)
    commented_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content


class Like(models.Model):
    """ いいね """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='like_user')
    post = models.ForeignKey(Blog, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user


class UserProfile(models.Model):
    """ ユーザープロフィール """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='profile')
    picture = models.ImageField(upload_to='profile_pictures', blank=True, null=True,)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


class UserManager(BaseUserManager):
    """ユーザーマネージャー."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """メールアドレスでの登録を必須にする"""
        if not email:
            raise ValueError('メールアドレスを入力してください')
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """is_staff(管理サイトにログインできるか)と、is_superuer(全ての権限)をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """スーパーユーザーは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル."""

    email = models.EmailField(_('email address'), unique=True)
    nick_name = models.CharField(_('nick name'), max_length=50, blank=False, unique=True, db_column="ユーザー名")

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_short_name(self):
        return self.nick_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """ユーザーにメールを送る"""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def username(self):
        """username属性のゲッター

        他アプリケーションが、username属性にアクセスした場合に備えて定義
        メールアドレスを返す
        """
        return self.email


@receiver(post_save, sender=User)
def create_profile(sender, **kwargs):
    """ 新ユーザー作成時に空のprofileも作成する """
    if kwargs['created']:
        user_profile = UserProfile.objects.get_or_create(user=kwargs['instance'])
