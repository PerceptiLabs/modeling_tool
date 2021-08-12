import tensorflow as tf
import tensorflow.keras.backend as K

def weighted_crossentropy(class_weights):
    """ Weighted Cross Entropy loss function """

    def compute_loss(y_true, y_pred):
        n_classes = y_pred.get_shape().as_list()[-1]
        flat_pred = tf.reshape(y_pred, [-1, n_classes])
        flat_labels = tf.reshape(y_true, [-1, n_classes])
        loss_tensor =  tf.reduce_mean(tf.nn.weighted_cross_entropy_with_logits(y_true, y_pred, class_weights))
        return loss_tensor

    return compute_loss


def dice(y_true, y_pred):
    """ Dice loss function """
    eps = 1e-5
    dice_coef = dice_coefficient(y_true, y_pred, eps)
    loss_tensor = tf.clip_by_value(1 - dice_coef, eps, 1.0-eps)
    return loss_tensor

def dice_coefficient(y_true, y_pred, eps=1e-5):
    """ Dice coefficient """
    intersection = tf.reduce_sum(tf.multiply(y_pred, y_true))
    union = tf.reduce_sum(y_pred) + tf.reduce_sum(y_true)
    dice_coef = (2 * intersection + eps)/(union + eps)
    return dice_coef
