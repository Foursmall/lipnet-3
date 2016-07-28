from abc import ABCMeta, abstractmethod
import pandas as pd
from random import shuffle
import os
from skimage import io, img_as_float
from skimage.transform import resize
import numpy as np


class Batch:
    def __init__(self, images, labels, ids):
        """

        :param images:
        :param labels:
        :param ids:
        """
        assert images.shape[0] == labels.shape[0], "Number of images and corresponding labels must be the same"
        assert images.shape[0] == ids.shape[0], "Number of images and corresponding ids must be the same"
        self.images = images
        self.labels = labels
        self.ids = ids

    @property
    def size(self):
        return self.ids.shape[0]

class DatasetAbstract(object):
    """
    This is an abstract class that describes a dataset object.
    Any implementation of lipnet dataset must follow contract described here
    and implement all stated below methods.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_num_classes(self):
        """

        :return: integer, number of classes
        """
        pass

    @abstractmethod
    def get_image_names(self):
        """

        :return: numpy 1D array of strings, corresponding to image names
        """
        pass

    @abstractmethod
    def get_labels(self):
        """

        :return: numpy 2D array, one-hot encoded labels
        """
        pass

    @abstractmethod
    def get_count(self):
        """

        :return: integer, total number of examples in the dataset
        """


class DatasetPD(DatasetAbstract):
    """
    This is an implementation of lipnet dataset based on pandas dataframe and JSON
    """
    __df = pd.DataFrame()
    __shape = None
    __class_columns = None
    __chunks = None
    __num_epochs = None
    __epoch_count = 0
    __batch_size = 100
    __path_to_img = None
    __image_width = 28
    __image_height = 28

    def __init__(self, path_to_json, path_to_img, batch_size=100, num_epochs=None, image_width=28, image_height=28):
        """

        :param path_to_json: full path to JSON file to be read into pandas dataframe
        :param path_to_img: full path to folder with images
        :param batch_size: integer, size of batch
        :param num_epochs: integer, number of times whole dataset can be processed, leave NOne for unlimited
        """
        super(DatasetPD, self).__init__()
        self.__df = pd.read_json(path_to_json)
        self.__shape = self.__df.shape
        self.__class_columns = [col for col in list(self.__df) if col.startswith('Label')]
        self.__num_epochs = num_epochs
        self.__image_height = image_height
        self.__image_width = image_width
        self.__path_to_img = path_to_img
        self.__batch_size = batch_size
        self.__create_chunks()

    def chunks(self, items, chunk_size):
        """
        Creates a generator
        :param items: iterable, list of items to be transformed into chunks
        :param chunk_size: integer, number of items in a chunk. This is a maximum number of items, chunk can be smaller if
                    total length of l is not divisible by n
        :return: generator
        """
        for i in xrange(0, len(items), chunk_size):
            yield items[i:i + chunk_size]

    def next_batch(self):
        """
        Yields a batch of data
        :return: batch
        """
        try:
            ids = self.__chunks.next()
        except StopIteration:
            if self.__reset():
                return self.next_batch()
            else:
                return None
        return self.__get_batch(ids)

    def __get_batch(self, ids):
        """
        Creates a batch from example ids
        :param ids: list of int, ids of examples
        :return: tuple
        """
        img_names = self.__df['Image'][self.__df['Id'].isin(ids)]
        images = np.empty([len(img_names), self.__image_width, self.__image_height], dtype=float)
        i = 0
        for f in img_names:
            filename = os.path.join(self.__path_to_img, f)
            img = io.imread(filename)
            img = img_as_float(img)
            img = resize(img, (self.__image_width, self.__image_height))
            images[i] = img
            i += 1
        labels = self.__df[self.__class_columns][self.__df['Id'].isin(ids)].values
        return Batch(images, labels, np.array(ids))

    def __reset(self):
        """
        Resets chunks if epochs limit is not reached
        :return: boolean
        """
        if self.__num_epochs is not None:
            if self.__epoch_count >= (self.__num_epochs - 1):
                return False

        self.__epoch_count += 1
        self.__create_chunks()
        return True

    def print_stats(self):
        """
        Prints som dataframe statistics to console
        :return: nothing
        """
        print '{} columns and {} rows'.format(self.__shape[1], self.__shape[0])
        print self.__df['Class'].value_counts()

    def __create_chunks(self):
        """
        Creates chunks
        :return: nothing, result is written to self.__chunks
        """
        list_of_ids = self.__df['Id'].tolist()
        shuffle(list_of_ids)
        self.__chunks = self.chunks(list_of_ids, self.__batch_size)

    # DatasetAbstract methods

    def get_count(self):
        """
        See description in DatasetAbstract
        :return:
        """
        return self.__shape[0]

    def get_num_classes(self):
        """
        See description in DatasetAbstract
        :return:
        """
        return len(self.__class_columns)

    def get_image_names(self):
        """
        See description in DatasetAbstract
        :return:
        """
        return self.__df['Image'].values

    def get_labels(self):
        """
        See description in DatasetAbstract
        :return:
        """
        return self.__df[self.__class_columns].values
