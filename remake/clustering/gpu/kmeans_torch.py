import torch
from torch import Tensor
from typing import Tuple
import time


class KMeansTorch:
    """
    This class contains the functionality for KMeans on large matrices running completly on gpu-accelerated.
    """

    def __init__(self, num_cluster: int, error: float, device:str) -> None:
        """
        Init function.

        Paramters:
        ----------
        num_clusters : int
            the number of allowed cluster centers
        error : float
            the error in distortion change

        Returns:
        --------
        None
        """
        self.num_clusters = num_cluster
        self.device = device
        self.error = torch.tensor(error).to(self.device)

    def fit(self, data: Tensor) -> Tuple[Tensor, Tensor]:
        """
        Performs the kmeans clustering on 3 dimensional tensor.

        Paramters:
        ----------
        data : Tensor
            the tensor containing the data for clustering

        Returns:
        --------
        centroids, assignments : Tuple[Tensor, Tensor]
            centroids - the centers of the single clusters
            assignments - the assigned label to each input matrix
        """
        starting_time = time.time()
        # if the are more requested cluster_centers than entries in the tensor update the count of centers
        if data.size()[0] < self.num_clusters:
            self.num_clusters = data.size()[0]

        # converts collection of tensors into a single 3 dimensional Tensor
        input: Tensor = torch.Tensor(data).to(self.device)

        # initialize ceentroids with the first matrices
        centroids: Tensor = input[: self.num_clusters, :].clone().to(self.device)

        # initialize the distorsion
        distorsion: Tensor = torch.tensor([0.0]).to(self.device)

        # set a counter for needed iterations:
        counter: int = 0
        # run kmeans iterations
        while True:
            # update the counter in every step
            counter += 1
            # save the old distorsion value
            distorsion_old: Tensor = torch.clone(distorsion)
            # reset distorsion
            distorsion = torch.zeros_like(distorsion)
            # calculates the distance between all matrices in the 2nd and 3rd dimension
            # attention: to match the dimensions we extend the input to a dummy 4th dimension
            distances: Tensor = torch.norm(
                input[:, None] - centroids, p="fro", dim=(2, 3)
            )

            # assign the matrix to the centroid with the shortest distance
            assignment: Tensor = torch.argmin(distances, dim=1)
            # update cluster centroids:
            for i in range(self.num_clusters):
                # extraxt matrices that are assigned to the i'th cluster
                cluster_matrices = input[assignment == i]
                # recalculate the centroids
                centroids[i] = torch.mean(cluster_matrices, dim=0)
                # calculate distortion: distorsion = sum(||x-centroid||_F^2)
                distorsion += torch.sum(
                    torch.square(
                        torch.norm(cluster_matrices - centroids[i], p="fro", dim=(1, 2))
                    )
                )

            # if the distortion change is less than our formal formal requirement stop
            if torch.lt(
                abs(distorsion - distorsion_old),
                self.error,
            ):
                # TODO: write message into logger instead in print out
                print(
                    f"Used {counter} iterations in {time.time()-starting_time} seconds on {self.device}."
                )
                break

        return centroids, assignment

    def adjust_error(self, error: float) -> None:
        """
        Function to adjust the error to runtime.

        Paramters:
        ----------
        error : float
            the new distortion error

        Returns:
        --------
        None
        """
        self.error = error

    def adjust_num_clusters(self, num_clusters: int) -> None:
        """
        Function to adjust the number of clusters to runtime.

        Parameters:
        -----------
        num_cluster : int
            the new number of clusters

        Returns:
        --------
        """
        self.num_clusters = num_clusters

    @property
    def get_device(self) -> str:
        """
        Function that returns the device for accelaration.

        Parameters:
        -----------
        None

        Returns:
        --------
        device : str
            the device as string
        """
        return self.device

    @property
    def get_error(self) -> torch.Tensor:
        """
        Function that returns the error.

        Parameters:
        -----------
        None

        Returns:
        --------
        error : torch.Tensor
            The error as torch.Tensor.
        """
        return self.error