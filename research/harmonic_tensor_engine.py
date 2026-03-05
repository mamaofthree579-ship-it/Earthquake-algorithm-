import numpy as np
from scipy.ndimage import laplace
from sklearn.cluster import KMeans


class HarmonicTensorDiscoveryEngine:

    def __init__(self):

        self.lambda_resonance = 0.4
        self.lambda_entropy = 0.3
        self.lambda_cluster = 0.3

    # -----------------------------------------
    # Entropy Estimation
    # -----------------------------------------

    def field_entropy(self, field):

        hist, _ = np.histogram(field.flatten(), bins=50, density=True)

        hist = hist + 1e-12

        return -np.sum(hist * np.log(hist))

    # -----------------------------------------
    # Spatial Cluster Coherence
    # -----------------------------------------

    def cluster_coherence(self, field, k=4):

        flat = field.flatten().reshape(-1, 1)

        if len(flat) < k:
            return 0.0

        model = KMeans(n_clusters=min(k, len(flat)))

        labels = model.fit_predict(flat)

        return np.var(labels)

    # -----------------------------------------
    # Resonance Proxy Metric
    # -----------------------------------------

    def resonance_metric(self, field):

        grad_x, grad_y = np.gradient(field)

        return np.mean(np.sqrt(grad_x**2 + grad_y**2))

    # -----------------------------------------
    # Discovery Score Computation
    # -----------------------------------------

    def discover(self, field):

        laplacian_energy = np.linalg.norm(laplace(field))

        resonance = self.resonance_metric(field)

        entropy = self.field_entropy(field)

        cluster_score = self.cluster_coherence(field)

        score = (
            laplacian_energy
            + self.lambda_resonance * resonance
            + self.lambda_entropy * entropy
            + self.lambda_cluster * cluster_score
        )

        return float(score)
