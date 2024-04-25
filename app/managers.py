from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username=None, phone=None, password=None, **extra_fields):
        if not username:
            if  not phone:
                raise ValueError('The given phone must be set')
        if phone:
            if not username:
                username = phone

            user = self.model(
                phone=phone,
                **extra_fields
            )
        if extra_fields.get('is_superuser'):
            user = self.model(
                phone=phone,
                **extra_fields
            )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone=phone, password=password, **extra_fields)

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(
            phone=phone,
            password=password,
            **extra_fields
        )