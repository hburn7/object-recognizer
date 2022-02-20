import kwargs as kwargs
import tensorflow as tf
from keras.layers import Dense, Flatten, Conv2D
from keras import Model

"""access the datasets here"""

# TODO have the model pull our images.

#path to directory
directory = 0
#from keras.io/api/data_loading/image site has info on each parameter for that method
#kwargs package needed to install to run this method.
(x_train, y_train), (x_test, y_test) = tf.keras.utils.image_dataset_from_directory(
    directory,
    labels="inferred",
    label_mode="int",
    class_names=None,
    color_mode="rgb",
    batch_size=32,
    image_size=(256,256),
    shuffle=True,
    seed=None,
    validation_split=None,
    subset=None,
    interpolation="bilinear",
    follow_links=False,
    crop_to_aspect_ratio=False,
    **kwargs
)
"""it looks like the image_dataset_from_directory method call covers
the next four lines of code. I'm going to keep them here
commented out in case I end up needing them."""
#(x_train, y_train), (x_test, y_test) = mnist.load_data()
#x_train, x_test = x_train/255.0, x_test/255.0

#channels dimension
#x_train = x_train[..., tf.newaxis].astype("float32")
#x_test = x_test[..., tf.newaxis].astype("float32")

train_ds = tf.data.Dataset.from_tensor_slices((x_train, y_train)).shuffle(10000).batch(32)

test_ds = tf.data.Dataset.from_tensor_slices((x_test, y_test)).batch(32)

# building keras model


class KerasModel(Model):

    def __init__(self):
        super(KerasModel, self).__init__()
        # relu = rectified linear unit
        self.conv1 = Conv2D(32, 3, activation='relu')
        self.flatten = Flatten()
        self.d1 = Dense(128, activation='relu')
        self.d2 = Dense(10)

    def call(self, x):
        x = self.conv1(x)
        x = self.flatten(x)
        x = self.d1(x)
        x = self.d2(x)


model = KerasModel()

# choosing optimizer and loss for training

loss_object = tf.keras.losses.SparseCategoricalCrossEntropy(from_logits=True)
optimizer = tf.keras.optimizers.Adam()

# metrics to measure loss and accuracy of the model. these metrics accululate the values over epochs and then print the overall result

train_loss = tf.keras.metrics.Mean(name='train_loss')
train_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name='train_accuracy')

test_loss = tf.keras.metrics.Mean(name='test_loss')
test_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name='test_accuracy')

#tf.GradientTape will train the model

@tf.function
def train_step(images, labels):
    with tf.GradientTape() as tape:
        #training=True is only needed if there are layers with different behavior during training vs inference (e.g. dropout)
        predictions = model(images, training=True)
        loss = loss_object(labels, predictions)
    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))

    train_loss(loss)
    train_accuracy(labels, predictions)

# testing the model

@tf.function
def test_step(images, labels):
    #training=False is only needed if there are layers with different behavior during training vs inference (e.g. dropout)
    predictions = model(images, training=False)
    t_loss = loss_object(labels, predictions)

    test_loss(t_loss)
    test_accuracy(labels, predictions)


EPOCHS = 10

for epoch in range(EPOCHS):
    #reset at each epoch
    train_loss.reset_states()
    train_accuracy.reset_states()
    test_loss.reset_states()
    test_accuracy.reset_states()

    for images, labels in train_ds:
        train_step(images, labels)

    for test_images, test_labels in test_ds:
        test_step(test_images, test_labels)

    print(
        f'Epoch {epoch +1}'
        f'Loss: {train_loss.result()}'
        f'Accuracy: {train_accuracy.result() * 100}'
        f'Test Loss: {test_loss.result()}'
        f'Test Accuracy: {test_accuracy.result() * 100}'
    )