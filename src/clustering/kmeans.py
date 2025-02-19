from typing import List
from sklearn.cluster import KMeans
import numpy as np
from clustering.base_cluster import BaseClustering
from clustering.similarity_matrix import SimilarityMatrix


class KMeansClustering(BaseClustering):
    """
    Class for setup a KMeans clustering.
    """

    num_clusters: List[int]

    def __init__(
        self, cluster_name: str, labels: List[str], num_clusters: List[int]
    ) -> None:
        """
        Initializes the class object.

        Parameters:
        ----------
        cluster_name : str
            the name for the cluster object
        labels : List[str]
            the labels for data vectors that are passed into the clustering

        Returns:
        --------
        None
        """
        super().__init__(labels, cluster_name)
        self.num_clusters = num_clusters
        self.similarity_matrix = [
            SimilarityMatrix(labels, cluster_name) for _ in range(len(num_clusters))
        ]

    def cluster(self, data_vecs: List[np.ndarray]) -> None:
        """
        Implementation of abstract method from BaseClustering class.

        Parameters:
        ----------
        data_vecs : np.ndarray
            the data vectors for the clustering algorithm
        cluster_size : int
            the number of different clusters in the algorithm

        Returns:
        --------
        None
        """
        # create sklearn KMeans object
        for index, num in enumerate(self.num_clusters):
            kmeans: KMeans = KMeans(n_clusters=num, n_init=10).fit(data_vecs)
            # update the similarity matrix with retrieved labels
            self.similarity_matrix[index].update(self.labels, kmeans.labels_)

    def write_cluster_results(self) -> None:
        """
        Function to write cluster results in .csv file.

        Parameters:
        -----------
        cluster_size : int
            the chosen cluster size for experiment

        Returns:
        --------
        None
        """
        for index, _ in enumerate(self.similarity_matrix):
            self.similarity_matrix[index].write_to_csv(
                str(self.num_clusters[index]) + "_centers"
            )
