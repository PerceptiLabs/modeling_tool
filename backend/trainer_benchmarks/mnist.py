import time
import tensorflow as tf

from trainer_benchmarks.suite import BenchmarkSuite
import perceptilabs.data.utils as data_utils


class MnistSuite(BenchmarkSuite):
    def __init__(self):
        self.data_loader = data_utils.get_mnist_loader()

    def _get_recommended_results(self, trainer, training_settings, training_duration):
        """ Formats the results summary of a PerceptiLabs recommended model. The output dict should match the baseline 

        Arguments:
            trainer: the trainer used 
            training_settings: the settings used
            training_duration: the training duration in seconds
        
        Returns:
            a dictionary of metrics and their values
        """
        stats = next(iter(trainer.get_output_stats().values()))  # This dataset has a single output
        results = stats.get_summary()
        results['training_duration (s)'] = training_duration
        results['epoch_duration (ms)'] = training_duration / int(training_settings['Epochs']) * 1000
        results['num_epochs'] = int(training_settings['Epochs'])
        return results
        
    def _run_baseline_model(self):
        """ This trains a stand-alone baseline. E.g., an optimal Keras baseline. The output dict should match the recommended model

        Returns:
            a dictionary of metrics and their values
        """
        n_epochs = 100
        
        def convert_dataset(inputs, targets):
            """Puts the mnist dataset in the format Keras expects, (features, labels)."""
            image = inputs['image_path']
            target = targets['target']
            return image, target

        dataset_size = self.data_loader.get_dataset_size(partition='training')
        training_set = self.data_loader.get_dataset(partition='training').map(convert_dataset).shuffle(buffer_size=dataset_size).batch(32)
        validation_set = self.data_loader.get_dataset(partition='validation').map(convert_dataset).batch(32)

        input_shape = self.data_loader.get_feature_shape('image_path')
        preprocessing = self.data_loader.get_preprocessing_pipeline('target', mode='training')
        n_categories = preprocessing.n_categories
        
        model = tf.keras.Sequential(
            [
                tf.keras.Input(shape=input_shape),
                tf.keras.layers.Conv2D(32, kernel_size=(3, 3), activation="relu"),
                tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
                tf.keras.layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),
                tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dropout(0.5),
                tf.keras.layers.Dense(n_categories, activation="softmax"),
            ]
        )
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

        t0 = time.perf_counter()
        history = model.fit(training_set, epochs=n_epochs, validation_data=validation_set)
        dt = time.perf_counter() - t0
        
        results = {
            'loss_training': history.history['loss'][-1],
            'loss_validation': history.history['val_loss'][-1],            
            'accuracy_training': history.history['accuracy'][-1],
            'accuracy_validation': history.history['val_accuracy'][-1],
            'training_duration (s)': dt,
            'epoch_duration (ms)': dt/n_epochs*1000,
            'num_epochs': n_epochs
        }
        return results

