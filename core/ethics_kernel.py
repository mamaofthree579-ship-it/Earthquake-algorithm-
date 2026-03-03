class EthicsKernel:

    def __init__(self, risk_threshold=0.7):
        self.risk_threshold = risk_threshold

    def compute_risk_proxy(self, complexity, sensitivity, human_review_score):

        risk = (complexity * sensitivity) / (human_review_score + 1e-8)

        return float(risk)

    def requires_review(self, risk_score):

        return risk_score > self.risk_threshold
