from django.contrib.auth.hashers import BCryptPasswordHasher
import bcrypt


class BMSBCryptPasswordHasher(BCryptPasswordHasher):

    algorithm = "bcrypt-2a-10"
    rounds = 10

    def salt(self):
        bcrypt = self._load_library()
        return bcrypt.gensalt(self.rounds, prefix=b"2a")
