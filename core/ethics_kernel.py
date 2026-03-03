class EthicsKernel:

    def __init__(self, threshold=0.7):
        self.threshold = threshold

    def compute_risk(self, complexity, sensitivity, review_score):

        risk = (complexity*sensitivity)/(review_score+1e-8)

        return float(risk)

    def requires_review(self, risk_score):
        return risk_score > self.threshold
