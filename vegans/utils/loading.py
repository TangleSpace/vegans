import pickle
import torchvision

import numpy as np

from vegans.utils.layers import LayerReshape
from vegans.utils.architectures.mnist import (
    preprocess_mnist, load_mnist_generator, load_mnist_adversariat,
    load_mnist_encoder, load_mnist_decoder, load_mnist_autoencoder
)
from vegans.utils.architectures.example import (
    load_example_generator, load_example_adversariat, load_example_encoder,
    load_example_decoder, load_example_autoencoder
)

def load_data(root, which=None, **kwargs):
    """ Wrapper around torchvision.datasets with certain preprocessing steps

    Parameters
    ----------
    root : str
        Path to root directory. Is created if `download=True` and the folder does not exists yet.
    which : str, optional
        One of the torchvision.datasets.
    **kwargs
        Keyword arguments to torchvision.datasets (`https://pytorch.org/vision/0.8/datasets.html`).

    Returns
    -------
    np.array
        Numpy array or torch dataset with train and test data.
    """
    if which is None:
        raise ValueError("`which` must be not None. See: https://pytorch.org/vision/0.8/datasets.html for available dataset names.")
    capitalize = ["cifar", "emnist", "kmnist", "lsun", "mnist"]
    if which.lower() in capitalize:
        which = which.upper()
    loader = eval("torchvision.datasets." + which)
    torch_data = loader(root=root, **kwargs)

    if which.lower() == "mnist":
        torch_data_train = loader(root=root, train=True, **kwargs)
        torch_data_test = loader(root=root, train=False, **kwargs)
        X_train, y_train = preprocess_mnist(torch_data_train, normalize=True, pad=2)
        X_test, y_test = preprocess_mnist(torch_data_test, normalize=True, pad=2)
        return X_train, y_train, X_test, y_test
    elif which.lower() == "fashionmnist":
        torch_data_train = loader(root=root, train=True, **kwargs)
        torch_data_test = loader(root=root, train=False, **kwargs)
        X_train, y_train = preprocess_mnist(torch_data_train, normalize=True, pad=2)
        X_test, y_test = preprocess_mnist(torch_data_test, normalize=True, pad=2)
        return X_train, y_train, X_test, y_test
    return torch_data

def load_generator(x_dim, z_dim, y_dim=None, which="example"):
    available = ["example", "mnist"]
    if which == "example":
        return load_example_generator(x_dim, z_dim, y_dim=y_dim)
    elif which == "mnist":
        return load_mnist_generator(x_dim, z_dim, y_dim=y_dim)
    else:
        raise ValueError("`which` must be one of {}. Given: {}.".format(available, which))

def load_adversariat(x_dim, z_dim, y_dim=None, adv_type="Critic", which="example"):
    available = ["example", "mnist"]
    if which == "example":
        return load_example_adversariat(x_dim, z_dim, y_dim=y_dim, adv_type=adv_type)
    elif which == "mnist":
        return load_mnist_adversariat(x_dim, z_dim, y_dim=y_dim, adv_type=adv_type)
    else:
        raise ValueError("`which` must be one of {}. Given: {}.".format(available, which))

def load_encoder(x_dim, z_dim, y_dim=None, which="example"):
    available = ["example", "mnist"]
    if which == "example":
        return load_example_encoder(x_dim, z_dim, y_dim=y_dim)
    elif which == "mnist":
        return load_mnist_encoder(x_dim, z_dim, y_dim=y_dim)
    else:
        raise ValueError("`which` must be one of {}. Given: {}.".format(available, which))

def load_decoder(x_dim, z_dim, y_dim=None, which="example"):
    available = ["example", "mnist"]
    if which == "example":
        return load_example_decoder(x_dim, z_dim, y_dim=y_dim)
    elif which == "mnist":
        return load_mnist_decoder(x_dim, z_dim, y_dim=y_dim)
    else:
        raise ValueError("`which` must be one of {}. Given: {}.".format(available, which))

def load_autoencoder(x_dim, z_dim, y_dim=None, which="example"):
    available = ["example", "mnist"]
    if which == "example":
        return load_example_autoencoder(x_dim, z_dim, y_dim=y_dim)
    elif which == "mnist":
        return load_mnist_autoencoder(x_dim, z_dim, y_dim=y_dim)
    else:
        raise ValueError("`which` must be one of {}. Given: {}.".format(available, which))

