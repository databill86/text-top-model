import numpy as np
import json
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier


from stacking_classifier import StackingTextClassifier
from sklearn_models import MultNB, BernNB, SVM
from keras_models.fchollet_cnn import FCholletCNN
from keras_models.mlp import MLP
from benchmarks import benchmark

datasets = [
    '../data/r8-all-terms.txt',
    '../data/r52-all-terms.txt',
    '../data/20ng-all-terms.txt',
    '../data/webkb-stemmed.txt'
]

models = [
    (FCholletCNN, {'dropout_rate': 0.5, 'embedding_dim': 37, 'units': 400, 'epochs': 30}),
    (FCholletCNN, {'dropout_rate': 0.5, 'epochs': 20, 'units': 400, 'embeddings_path':
        '../data/glove.6B/glove.6B.100d.txt'}),
    (MLP, {'layers': 1, 'units': 360, 'dropout_rate': 0.87, 'epochs': 12, 'max_vocab_size': 22000}),
    (MLP, {'layers': 2, 'units': 180, 'dropout_rate': 0.6, 'epochs': 5, 'max_vocab_size': 22000}),
    (MLP, {'layers': 3, 'dropout_rate': 0.2, 'epochs': 20}),
    (MultNB, {'tfidf': True}),
    (MultNB, {'tfidf': True, 'ngram_n': 2}),
    (MultNB, {'tfidf': True, 'ngram_n': 3}),
    (BernNB, {'tfidf': True}),
    (MultNB, {'tfidf': False}),
    (MultNB, {'tfidf': False, 'ngram_n': 2}),
    (BernNB, {'tfidf': False}),
    (SVM, {'tfidf': True, 'kernel': 'linear'}),
    (SVM, {'tfidf': True, 'kernel': 'linear', 'ngram_n': 2}),
    (SVM, {'tfidf': False, 'kernel': 'linear'}),
    (SVM, {'tfidf': False, 'kernel': 'linear', 'ngram_n': 2})
]

logreg_stacker = (StackingTextClassifier, {
    'stacker': (LogisticRegression, {}),
    'base_classifiers': [
        (m, params)
        for m, params in models[:-3]
    ] + [
        (m, dict(params.items() + [('probability', True)]))
        for m, params in models[-3:]
    ],
    'use_proba': True,
    'folds': 5
})

xgb_stacker = (StackingTextClassifier, {
    'stacker': (XGBClassifier, {}),
    'base_classifiers': [m for m in models],
    'use_proba': False,
    'folds': 5
})

models.append(logreg_stacker)
models.append(xgb_stacker)

results_path = 'results.json'

if __name__ == '__main__':
    records = []
    for data_path in datasets:
        print
        print data_path

        for model_class, params in models:
            scores, times = benchmark(model_class, data_path, params, 10)
            model_str = str(model_class(**params))
            print '%.3f' % np.mean(scores), model_str
            for score, time in zip(scores, times):
                records.append({
                    'model': model_str,
                    'dataset': data_path,
                    'score': score,
                    'time': time
                })

    with open(results_path, 'wb') as f:
        for r in records:
            f.write(json.dumps(r) + '\n')
