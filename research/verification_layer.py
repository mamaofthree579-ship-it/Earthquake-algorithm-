import hashlib
import numpy as np

class VerificationLayer:

    def hash_array(self, array):

        return hashlib.sha256(
            array.tobytes()
        ).hexdigest()

    def verify_determinism(self, a, b):

        return self.hash_array(a) == self.hash_array(b)
