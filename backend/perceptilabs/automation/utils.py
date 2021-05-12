from perceptilabs.automation.modelrecommender.base import ModelRecommender
from perceptilabs.automation.autosettings.base import SettingsEngine


def get_model_recommendation(data_loader):
    """ Runs the model recommender and the auto settings engine. 

    Args:
        data_loader: loader for the dataset

    Returns:
        graph_spec: the recommended model
        training_settings: the recommended training settings        
    """
    recommender = ModelRecommender(data_loader=data_loader)
    graph_spec = recommender.get_graph(data_loader.feature_specs)

    training_settings = { # TODO(anton.k): invoke settings engine on model to get optimal settings
        'Batch_size': 32,
        'Beta1': 0.9,
        'Beta2': 0.999,
        'Centered': False,
        'Epochs': 100,
        'Learning_rate': 0.001,
        'Loss': 'Quadratic',
        'LossOptions': [
            {'text': 'Cross-Entropy', 'value': 'Cross-Entropy'},
            {'text': 'Quadratic', 'value': 'Quadratic'},
            {'text': 'Dice', 'value': 'Dice'}
        ],
        'Momentum': 0,
        'Optimizer': 'ADAM',
        'OptimizerOptions': [
            {'text': 'ADAM', 'value': 'ADAM'},
            {'text': 'SGD', 'value': 'SGD'},
            {'text': 'Adagrad', 'value': 'Adagrad'},
            {'text': 'RMSprop', 'value': 'RMSprop'}
        ],
        'Shuffle': True
    }
    return graph_spec, training_settings

    
    
    
    
    

