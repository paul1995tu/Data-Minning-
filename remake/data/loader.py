import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Set, Optional
import os
from omegaconf import OmegaConf
import multiprocessing as mp
from enum import Enum

class PANDAS_STACK_ORIENTATION(Enum):
    """
    Enum class to specify the orientation of the stacked pandas dataframe.
    """

    HORIZONTAL = 1
    VERTICAL = 0


class DataLoader:

    def __init__(self, config_path="/home/h9/elru535b/scratch/elru535b-workspace/Data-Mining/remake/config/data.yaml") -> None:
        """
        The init function of the data loader.

        Parameters:
        -----------
        config_path : str
            The path to the config file.

        Returns:
        --------
        None
        """
        if os.path.exists(config_path):
            self.config = OmegaConf.load(config_path)
        else:
            raise FileNotFoundError("The config file does not exist.")
        if os.path.exists(self.config["workload"]):
            self.done_workload = pd.read_csv(self.config["workload"])
        else:
            raise FileNotFoundError("The done_workload file does not exist.")
        if os.path.exists(self.config["hyperparameter"]):
            self.hyperparameter = OmegaConf.load(self.config["hyperparameter"])
        else:
            raise FileNotFoundError("The hyperparameter config file does not exist!")
        self.data_dir = self.config["data_dir"]
        self.columns = [
            "EXP_RANDOM_SEED",
            "EXP_START_POINT",
            "EXP_NUM_QUERIES",
            "EXP_BATCH_SIZE",
            "EXP_LEARNER_MODEL",
            "EXP_TRAIN_TEST_BUCKET_SIZE",
        ]

    def get_strategies(self) -> List[str]:
        """
        Function to get all strategies described in the config file.

        Parameters:
        -----------
        None

        Returns:
        --------
        strategies : List[str]
            The list of all strategies.
        """
        return self.config["strategies"]

    def get_metrices(self) -> List[str]:
        """
        Function to get all metrices described in the config file.

        Parameters:
        -----------
        None

        Returns:
        --------
        metrices : List[str]
            The list of all metrices.
        """
        return self.config["metrices"]

    def get_datasets(self) -> List[str]:
        """
        Function to get all datasets described in the config file.

        Parameters:
        -----------
        None

        Returns:
        --------
        datasets : List[str]
            The list of all datasets.
        """
        return self.config["datasets"]

    def load_single_df(self, path:str) -> Tuple[str, pd.DataFrame]:
        """
        Function to load a single dataframe.

        Parameters:
        -----------
        path : str
            The path to the frame.

        Returns:
        --------
        name : str
            The strategy name.
        frame : pd.DataFrame
            The data frame.
        """
        return path.split("/")[-3], pd.merge(pd.read_csv(path), self.done_workload)

    def load_data_for_metric_dataset(self, metric:str, dataset:str) -> Tuple[List[str], List[pd.DataFrame]] | Tuple[None, None]:
        """
        Function to load all files for a metric on a data set.
        Parameters:
        -----------
        metric : str
            A metric.
        dataset : str
            A dataset.

        Returns:
        --------
        strategies : List[str]
            The strategies.
        frames : List[pd.DataFrame]
            The corresponding dataframes.
        """
        # read in all the paths for the datasets
        paths = [os.path.join(os.path.join(self.data_dir, strategy), f"{dataset}/{metric}")
                 for strategy in self.get_strategies()]
        if not all([os.path.exists(path) for path in paths]):
            return None, None
        with mp.Pool(mp.cpu_count()) as pool:
            results = pool.map(self.load_single_df, paths)
        pool.close()
        results = sorted(results, key=lambda x: x[0])
        return list(map(lambda x: x[0], results)), list(map(lambda x: x[1], results))

    def get_hyperparameter_for_dataset(self, dataset:str) -> List[Tuple[int, int, int, int, int, int]]:
        """

        Parameters:
        -----------
        dataset : str
            The dataset the hyperparameters are requested for.

        Returns:
        --------
        List[Tuple[int, int, int, int, int, int]]
        """
        return self.hyperparameter[dataset]

    def get_row(self, frame: Tuple[str, pd.DataFrame, List[int]]) -> Tuple[str, np.ndarray]:
        """
        Function to extract a single row from a dataframe.

        Parameters:
        -----------
        frame : Tuple[str, pd.DataFrame, List[int]]
            The frame and additional information.

        Returns:
        --------
        name : str
            The name of the strategy.
        filtered_df : np.ndarray
            The row as numpy array.
        """
        filtered_df = frame[1][(frame[1][self.columns] == frame[2]).all(axis=1)].to_numpy()
        if filtered_df.shape[0] == 1:
            filtered_df = filtered_df.squeeze(axis=0)[:-9]
        else:
            filtered_df = filtered_df[:-9]
        return frame[0], filtered_df
