from lipnet_dataset import DatasetPD, DatasetPDFeatures, DatasetPDAugmented
from lipnet_tf import train as lptf
from lipnet_tf.model import Model
from lipnet_tf import FLAGS
import lipnet_architecture as la


def train_on_images():
    """
    Train lipnet CNN with some framework. Currently only Tensorflow is supported
    :return:
    """
    problem = 'lamellarity'
    dir = '/home/sergii/Documents/microscopic_data/{}/'
    path_to_json = dir + '{}_{}_set.json'
    path_to_img = dir + 'images/without_padding/'
    batch_size = 500
    FLAGS.batch_size = batch_size
    epochs = 100
    # create train set
    train_set = DatasetPDAugmented(path_to_json.format(problem, problem, 'train'),
                          path_to_img.format(problem),
                          batch_size=batch_size,
                          num_epochs=epochs)

    validation_set = DatasetPD(path_to_json.format(problem, problem, 'validation'),
                          path_to_img.format(problem),
                          batch_size=batch_size,
                          num_epochs=1)

    model = Model(3, la.layer_definitions)
    lptf.train(train_set, model, validation_set)


def main(argv=None):
    #train_on_features()
    train_on_images()

if __name__ == '__main__':
    main()
