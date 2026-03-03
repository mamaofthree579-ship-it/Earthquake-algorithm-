class EthicsKernel:
    def validate(self, job_payload: dict):
        if "compute" not in job_payload:
            return False, "Missing compute function"

        if not callable(job_payload["compute"]):
            return False, "Compute must be callable"

        return True, "Approved"
