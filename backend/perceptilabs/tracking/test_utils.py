from perceptilabs.tracking.utils import aggregate_summaries


def test_aggregate_summaries():
    summaries = [
        {'accuracy_training': 0.3, 'loss_validation': 0.5},
        {'accuracy_training': 0.7, 'loss_validation': 0.4},
        {'loss_validation': 0.2}
    ]

    agg_metrics = aggregate_summaries(summaries)

    assert agg_metrics['metric_accuracy_training_max_over_layers'] == 0.7
    assert agg_metrics['metric_accuracy_training_min_over_layers'] == 0.3
    assert agg_metrics['metric_accuracy_training_avg_over_layers'] == (0.7 + 0.3) / 2
    assert agg_metrics['metric_accuracy_training_num_layers'] == 2
    
    assert agg_metrics['metric_loss_validation_max_over_layers'] == 0.5
    assert agg_metrics['metric_loss_validation_min_over_layers'] == 0.2
    assert agg_metrics['metric_loss_validation_avg_over_layers'] == (0.5 + 0.4 + 0.2) / 3
    assert agg_metrics['metric_loss_validation_num_layers'] == 3

    
    
    

    
    
