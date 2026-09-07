"""
Python support file for algorithm demonstration.

@author: Preeston Mackert
"""

# ------------------------------------------------------------------------------------------------------- #
# libraries
# ------------------------------------------------------------------------------------------------------- #

import zipfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from dataclasses import dataclass
from urllib.request import Request, urlopen
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression as SklearnLogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

# ------------------------------------------------------------------------------------------------------- #
# data utilities
# ------------------------------------------------------------------------------------------------------- #

@dataclass
class DatasetBundle:
    """
    A container for dataset arrays and feature names that will be used by the model.
    """
    X: np.ndarray
    y: np.ndarray
    feature_names: list[str]
    dataframe: pd.DataFrame


class ReadmissionDataset:
    """
    Loads the public UCI Diabetes 130-US Hospitals dataset for 30-day readmission.

    Source: https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008
    """
    UCI_ZIP_URL = (
        'https://archive.ics.uci.edu/static/public/296/'
        'diabetes+130-us+hospitals+for+years+1999-2008.zip'
    )
    # expired and hospice discharges are not candidates for 30-day readmission -> remove from prediction.
    EXCLUDED_DISCHARGE_IDS = {11, 13, 14, 19, 20, 21}

    def __init__(self):
        self.data = self.load()

    def load(self, n_samples: int | None = 2400) -> DatasetBundle:
        """
        Load and prepare the public readmission dataset.

        @param: n_samples:
            Optional stratified subsample to run notebook faster.
            Pass None to use every eligible encounter (~100k rows).
        """
        raw = self._load_raw_frame()
        prepared = self._prepare(raw).reset_index(drop=True)        
        feature_names = [
            'age',
            'prior_inpatient_visits',
            'number_diagnoses',
            'time_in_hospital',
            'num_medications',
            'number_emergency',
            'number_outpatient',
            'on_diabetes_med',
        ]
        X = prepared[feature_names].to_numpy(dtype=float)
        y = prepared['actual_readmit'].to_numpy(dtype=int)
        return DatasetBundle(X=X, y=y, feature_names=feature_names, dataframe=prepared)

    def _download_uci_csv(self, csv_path: Path) -> None:
        """
        Support function to download the uci data into ./data
        """
        zip_path = './data/diabetes_130.zip'
        request = Request(
            self.UCI_ZIP_URL, 
            headers={}
        )
        with urlopen(request) as response:
            zip_path.write_bytes(response.read())
        with zipfile.ZipFile(zip_path) as archive:
            with archive.open('./data/diabetic_data.csv') as source, csv_path.open('wb') as target:
                target.write(source.read())
                
    def _load_raw_frame(self) -> pd.DataFrame:
        """ 
        Support function to load downloaded csv into pandas.
        """
        csv_path = './data/diabetic_data.csv'
        if not Path(csv_path).exists():
            self._download_uci_csv(csv_path)
        return pd.read_csv(csv_path, low_memory=False)    

    def _prepare(self, raw: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans the raw UCI dataset before feeding into prediction models by dropping 
        cases that are not relevant for predicting readmission (e.g. patient past away). 
        The data set also uses bins for age, which are mapped to the midpoint for the 
        model.
        """
        frame = raw[~raw['discharge_disposition_id'].isin(self.EXCLUDED_DISCHARGE_IDS)]
        age_midpoints = {
            '[0-10)': 5,
            '[10-20)': 15,
            '[20-30)': 25,
            '[30-40)': 35,
            '[40-50)': 45,
            '[50-60)': 55,
            '[60-70)': 65,
            '[70-80)': 75,
            '[80-90)': 85,
            '[90-100)': 95,
        }
        prepared = pd.DataFrame(
            {
                'age': frame['age'].map(age_midpoints),
                'prior_inpatient_visits': frame['number_inpatient'].astype(float),
                'number_diagnoses': frame['number_diagnoses'].astype(float),
                'time_in_hospital': frame['time_in_hospital'].astype(float),
                'num_medications': frame['num_medications'].astype(float),
                'number_emergency': frame['number_emergency'].astype(float),
                'number_outpatient': frame['number_outpatient'].astype(float),
                'on_diabetes_med': (frame['diabetesMed'] == 'Yes').astype(float),
                'actual_readmit': (frame['readmitted'] == '<30').astype(int),
            }
        )
        return prepared.dropna().reset_index(drop=True)


def split_train_val_test(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.20,
    val_size: float = 0.20,
    random_state: int = 42,
):
    """
    Stratified train / validation / test split.

    test_size and val_size are fractions of the full dataset (default 60/20/20).
    Fit on train, tune thresholds and model choices on validation, report only on test.
    """
    X_tv, X_test, y_tv, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    val_fraction_of_tv = val_size / (1.0 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_tv,
        y_tv,
        test_size=val_fraction_of_tv,
        random_state=random_state,
        stratify=y_tv,
    )
    return X_train, X_val, X_test, y_train, y_val, y_test
        
# ------------------------------------------------------------------------------------------------------- #
# algorithms
# ------------------------------------------------------------------------------------------------------- #

class LogisticRegression:
    """
    MBA-style logistic regression baseline for binary readmission risk.

    Fits P(y=1 | x) with sklearn LogisticRegression, exposes coefficients /
    odds ratios, and supports F1-based threshold tuning for comparison with
    the other notebook models.
    """
    def __init__(
        self,
        random_state: int = 42,
        max_iter: int = 2000,
        class_weight: str | dict | None = 'balanced',
    ):
        self.random_state = random_state
        # Must use the sklearn alias — this class is also named LogisticRegression.
        self.model = SklearnLogisticRegression(
            max_iter=max_iter,
            class_weight=class_weight,
            random_state=random_state,
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> 'LogisticRegression':
        self.model.fit(X, y)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        scores = self.predict_proba(X)[:, 1]
        return (scores >= threshold).astype(int)

    def coefficient_table(self, feature_names: list[str]) -> pd.DataFrame:
        table = pd.DataFrame(
            {
                'feature': feature_names,
                'theta': self.model.coef_[0],
                'odds_ratio': np.exp(self.model.coef_[0]),
            }
        )
        return table.sort_values('theta', key=abs, ascending=False).reset_index(drop=True)

    def tune(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        model_name: str = 'LogisticRegression',
    ) -> tuple[dict, dict]:
        """
        Fit on train, pick an F1 threshold on validation, score test.

        Returns:
            result: ModelEvaluator-compatible metrics dict on the test split
            tuned_output: scores / threshold / pred payload for tuned_outputs
        """
        self.fit(X_train, y_train)
        train_scores = self.predict_proba(X_train)[:, 1]
        val_scores = self.predict_proba(X_val)[:, 1]
        test_scores = self.predict_proba(X_test)[:, 1]
        tuned_output = pack_tuned_output(
            y_val,
            val_scores,
            test_scores,
            train_scores=train_scores,
        )
        threshold = tuned_output['threshold']
        test_metrics = metrics_at_threshold(y_test, test_scores, threshold)
        result = {
            'model': model_name,
            'train_accuracy': accuracy_score(y_train, (train_scores >= threshold).astype(int)),
            'test_accuracy': test_metrics['test_accuracy'],
            'precision': test_metrics['precision'],
            'recall': test_metrics['recall'],
            'f1': test_metrics['f1'],
            'confusion_matrix': confusion_matrix(y_test, tuned_output['pred']),
            'threshold': threshold,
            'intercept': float(self.model.intercept_[0]),
        }
        return result, tuned_output


class TreeBenchmarker:
    """
    Decision tree and random forest benchmarking helpers.
    """
    def __init__(self, random_state: int = 42):
        self.random_state = random_state

    def depth_sweep(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        depths: list[int] | None = None,
    ) -> list[dict]:
        if depths is None:
            depths = list(range(1, 13))
        results: list[dict] = []
        for depth in depths:
            model = DecisionTreeClassifier(max_depth=depth, random_state=self.random_state)
            metrics = ModelEvaluator.evaluate(model, X_train, y_train, X_test, y_test, f'DecisionTree(d={depth})')
            metrics['max_depth'] = depth
            results.append(metrics)
        return results

    def compare_best_tree_and_forest(
        self,
        depth_results: list[dict],
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> list[dict]:
        best = max(depth_results, key=lambda row: row['test_accuracy'])
        best_depth = best['max_depth']

        best_tree = DecisionTreeClassifier(max_depth=best_depth, random_state=self.random_state)
        forest = RandomForestClassifier(
            n_estimators=300,
            min_samples_leaf=2,
            random_state=self.random_state,
        )

        tree_result = ModelEvaluator.evaluate(
            best_tree,
            X_train,
            y_train,
            X_test,
            y_test,
            model_name=f'DecisionTree(best d={best_depth})',
        )
        forest_result = ModelEvaluator.evaluate(
            forest,
            X_train,
            y_train,
            X_test,
            y_test,
            model_name='RandomForest(300 trees)',
        )
        return [tree_result, forest_result]


class TinyNeuralNetClassifier:
    """
    Minimal two-layer neural net for binary classification.
    """
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 24,
        learning_rate: float = 0.01,
        epochs: int = 2000,
        random_state: int = 42,
    ):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.rng = np.random.default_rng(random_state)

        self.W1 = self.rng.normal(0, 0.25, size=(input_dim, hidden_dim))
        self.b1 = np.zeros((1, hidden_dim))
        self.W2 = self.rng.normal(0, 0.25, size=(hidden_dim, 1))
        self.b2 = np.zeros((1, 1))

        self.loss_curve_: list[float] = []

    @staticmethod
    def _sigmoid(z: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-z))

    @staticmethod
    def _bce_loss(y_true: np.ndarray, y_pred: np.ndarray, eps: float = 1e-8) -> float:
        y_pred = np.clip(y_pred, eps, 1 - eps)
        return float(-(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred)).mean())

    def _forward(self, X: np.ndarray) -> np.ndarray:
        self.z1 = X @ self.W1 + self.b1
        self.a1 = np.tanh(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.y_hat = self._sigmoid(self.z2)
        return self.y_hat

    def _backward(self, X: np.ndarray, y: np.ndarray) -> None:
        m = X.shape[0]

        dz2 = (self.y_hat - y) / m
        dW2 = self.a1.T @ dz2
        db2 = dz2.sum(axis=0, keepdims=True)

        da1 = dz2 @ self.W2.T
        dz1 = da1 * (1 - np.tanh(self.z1) ** 2)
        dW1 = X.T @ dz1
        db1 = dz1.sum(axis=0, keepdims=True)

        self.W2 -= self.learning_rate * dW2
        self.b2 -= self.learning_rate * db2
        self.W1 -= self.learning_rate * dW1
        self.b1 -= self.learning_rate * db1

    def fit(self, X: np.ndarray, y: np.ndarray) -> 'TinyNeuralNetClassifier':
        y = y.reshape(-1, 1)
        self.loss_curve_.clear()
        for _ in range(self.epochs):
            y_hat = self._forward(X)
            loss = self._bce_loss(y, y_hat)
            self._backward(X, y)
            self.loss_curve_.append(loss)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        proba = self._forward(X)
        return np.column_stack([1 - proba.ravel(), proba.ravel()])

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        return (self._forward(X).ravel() >= threshold).astype(int)

        
class RecursiveReweightingEnsemble:
    """
    Iterative sample reweighting with shallow trees.
    """
    def __init__(self, rounds: int = 16, depth: int = 2, learning_rate: float = 0.8, random_state: int = 42):
        self.rounds = rounds
        self.depth = depth
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.models_: list[DecisionTreeClassifier] = []
        self.alphas_: list[float] = []
        self.history_: list[dict] = []

    @staticmethod
    def _safe_error(value: float) -> float:
        return float(np.clip(value, 1e-6, 1 - 1e-6))

    def fit(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray | None = None,
        y_test: np.ndarray | None = None,
    ) -> 'RecursiveReweightingEnsemble':
        n = X_train.shape[0]
        weights = np.ones(n, dtype=float) / n

        self.models_.clear()
        self.alphas_.clear()
        self.history_.clear()

        for round_idx in range(self.rounds):
            model = DecisionTreeClassifier(max_depth=self.depth, random_state=self.random_state + round_idx)
            model.fit(X_train, y_train, sample_weight=weights)
            pred_train = model.predict(X_train)

            miss = (pred_train != y_train).astype(float)
            weighted_error = self._safe_error(float(np.sum(weights * miss)))
            alpha = self.learning_rate * 0.5 * np.log((1 - weighted_error) / weighted_error)

            direction = np.where(miss > 0, 1.0, -1.0)
            weights *= np.exp(alpha * direction)
            weights /= weights.sum()

            train_acc = accuracy_score(y_train, pred_train)
            row = {
                'round': round_idx + 1,
                'weighted_error': weighted_error,
                'alpha': float(alpha),
                'train_accuracy': train_acc,
            }

            if X_test is not None and y_test is not None:
                pred_test = self.predict(X_test, extra_models=self.models_ + [model], extra_alphas=self.alphas_ + [alpha])
                row['test_accuracy'] = accuracy_score(y_test, pred_test)
                row['test_f1'] = f1_score(y_test, pred_test, zero_division=0)

            self.models_.append(model)
            self.alphas_.append(float(alpha))
            self.history_.append(row)

        return self

    def _decision_score(
        self,
        X: np.ndarray,
        extra_models: list[DecisionTreeClassifier] | None = None,
        extra_alphas: list[float] | None = None,
    ) -> np.ndarray:
        models = self.models_ if extra_models is None else extra_models
        alphas = self.alphas_ if extra_alphas is None else extra_alphas

        score = np.zeros(X.shape[0], dtype=float)
        for model, alpha in zip(models, alphas):
            pred_pm = np.where(model.predict(X) == 1, 1.0, -1.0)
            score += alpha * pred_pm
        return score

    def predict(
        self,
        X: np.ndarray,
        extra_models: list[DecisionTreeClassifier] | None = None,
        extra_alphas: list[float] | None = None,
    ) -> np.ndarray:
        score = self._decision_score(X, extra_models=extra_models, extra_alphas=extra_alphas)
        return (score >= 0).astype(int)

    def evaluate(self, X: np.ndarray, y: np.ndarray, model_name: str = 'RecursiveReweightingEnsemble') -> dict:
        y_pred = self.predict(X)
        return {
            'model': model_name,
            'train_accuracy': np.nan,
            'test_accuracy': accuracy_score(y, y_pred),
            'precision': precision_score(y, y_pred, zero_division=0),
            'recall': recall_score(y, y_pred, zero_division=0),
            'f1': f1_score(y, y_pred, zero_division=0),
            'confusion_matrix': confusion_matrix(y, y_pred),
        }


# ------------------------------------------------------------------------------------------------------- #
# model evaluation helpers
# ------------------------------------------------------------------------------------------------------- #

class ModelEvaluator:
    """
    Shared evaluation utilities for binary classification.
    """
    @staticmethod
    def evaluate(model, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray, model_name: str) -> dict:
        model.fit(X_train, y_train)
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        return {
            'model': model_name,
            'train_accuracy': accuracy_score(y_train, y_train_pred),
            'test_accuracy': accuracy_score(y_test, y_test_pred),
            'precision': precision_score(y_test, y_test_pred, zero_division=0),
            'recall': recall_score(y_test, y_test_pred, zero_division=0),
            'f1': f1_score(y_test, y_test_pred, zero_division=0),
            'confusion_matrix': confusion_matrix(y_test, y_test_pred),
        }

    @staticmethod
    def format_results(results: list[dict]) -> str:
        header = f'{'Model':<32} {'Train Acc':>10} {'Test Acc':>10} {'Precision':>10} {'Recall':>10} {'F1':>8}'
        lines = [header, '-' * len(header)]
        for r in results:
            lines.append(
                f'{r['model']:<32} {r['train_accuracy']:>10.3f} {r['test_accuracy']:>10.3f} '
                f'{r['precision']:>10.3f} {r['recall']:>10.3f} {r['f1']:>8.3f}'
            )
        return '\n'.join(lines)
        
def plot_depth_sweep(depth_results: list[dict]) -> None:
    depths = [r['max_depth'] for r in depth_results]
    train_acc = [r['train_accuracy'] for r in depth_results]
    test_acc = [r['test_accuracy'] for r in depth_results]

    plt.figure(figsize=(7, 4.5))
    plt.plot(depths, train_acc, marker='o', label='Train Accuracy')
    plt.plot(depths, test_acc, marker='s', label='Validation Accuracy')
    plt.title('Decision Tree Depth Sweep')
    plt.xlabel('Tree Depth')
    plt.ylabel('Accuracy')
    plt.xticks(depths)
    plt.grid(alpha=0.2)
    plt.legend()
    plt.show()


def plot_confusion_matrices(results: list[dict], title: str = 'Confusion Matrices') -> None:
    fig, axes = plt.subplots(1, len(results), figsize=(5 * len(results), 4))
    if len(results) == 1:
        axes = [axes]

    for ax, row in zip(axes, results):
        ConfusionMatrixDisplay(row['confusion_matrix']).plot(ax=ax, colorbar=False)
        ax.set_title(row['model'])

    plt.suptitle(title)
    plt.tight_layout()
    plt.show()


def plot_recursive_history(history: list[dict]) -> None:
    rounds = [row['round'] for row in history]
    train_acc = [row['train_accuracy'] for row in history]
    weighted_error = [row['weighted_error'] for row in history]
    test_acc = [row.get('test_accuracy', np.nan) for row in history]
    max_round = int(max(rounds)) if rounds else 1
    round_ticks = list(range(2, max_round + 1, 2)) or [1]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    axes[0].plot(rounds, train_acc, marker='o', label='Train Accuracy')
    if not np.isnan(test_acc).all():
        axes[0].plot(rounds, test_acc, marker='s', label='Validation Accuracy')
    axes[0].set_title('Recursive Learning Accuracy')
    axes[0].set_xlabel('Round')
    axes[0].set_ylabel('Accuracy')
    axes[0].set_xticks(round_ticks)
    axes[0].set_xlim(0.5, max_round + 0.5)
    axes[0].grid(alpha=0.2)
    axes[0].legend()
    axes[1].plot(rounds, weighted_error, marker='d', color='tab:red')
    axes[1].set_title('Weighted Training Error')
    axes[1].set_xlabel('Round')
    axes[1].set_ylabel('Weighted Error')
    axes[1].set_xticks(round_ticks)
    axes[1].set_xlim(0.5, max_round + 0.5)
    axes[1].grid(alpha=0.2)
    plt.tight_layout()
    plt.show()



def _tuned_metrics_table(tuned_outputs: dict, y_true: np.ndarray) -> pd.DataFrame:
    """Build per-model classification metrics from tuned_outputs."""
    y_true = np.asarray(y_true).ravel()
    rows = []
    for name, payload in tuned_outputs.items():
        pred = np.asarray(payload['pred']).astype(int)
        rows.append(
            {
                'model': name,
                'accuracy': accuracy_score(y_true, pred),
                'precision': precision_score(y_true, pred, zero_division=0),
                'recall': recall_score(y_true, pred, zero_division=0),
                'f1': f1_score(y_true, pred, zero_division=0),
            }
        )
    return pd.DataFrame(rows)


def _style_bar_labels(
    ax,
    bars,
    values,
    fmt: str = '{:.2f}',
    pad: float = 0.015,
    rotation: float = 0,
) -> None:
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + pad,
            fmt.format(value),
            ha='center' if rotation == 0 else 'left',
            va='bottom',
            fontsize=8,
            rotation=rotation,
            rotation_mode='anchor',
        )


def model_metrics_table(tuned_outputs: dict, y_true: np.ndarray) -> pd.DataFrame:
    """
    Build the shared metrics table for notebook display.

    Sorted by accuracy (desc). Includes accuracy, precision, recall, and f1.
    """
    return (
        _tuned_metrics_table(tuned_outputs, y_true)
        .sort_values('accuracy', ascending=False)
        .reset_index(drop=True)
    )


def plot_model_comparison(tuned_outputs: dict, y_true: np.ndarray) -> pd.DataFrame:
    """
    Compare every tuned model on held-out classification metrics.

    Expects tuned_outputs[name] = {'scores', 'threshold', 'pred'}.
    Draws grouped bars for Accuracy / Precision / Recall / F1 (sorted by accuracy).
    Does not display a table — call model_metrics_table(...) in a separate cell.
    """
    comparison = model_metrics_table(tuned_outputs, y_true)

    metrics = ['accuracy', 'precision', 'recall', 'f1']
    models = comparison['model'].tolist()
    x = np.arange(len(models))
    width = 0.18
    colors = ['#2F6F8F', '#5B8C5A', '#C47A3A', '#7A5C8A']
    bar_edge = {'edgecolor': '#A8A8A8', 'linewidth': 0.8}

    fig, ax = plt.subplots(figsize=(max(9, 1.4 * len(models)), 5.4))
    for i, (metric, color) in enumerate(zip(metrics, colors)):
        values = comparison[metric].to_numpy()
        offset = (i - (len(metrics) - 1) / 2) * width
        bars = ax.bar(
            x + offset,
            values,
            width,
            label=metric.capitalize(),
            color=color,
            **bar_edge,
        )
        _style_bar_labels(ax, bars, values, rotation=65)

    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=20, ha='right')
    ax.set_ylim(0, 1.22)
    ax.set_ylabel('Score')
    ax.set_title('Tuned Model Comparison on Test Set')
    ax.legend(frameon=False, ncol=4, loc='upper right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, alpha=0.25)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.show()


# ------------------------------------------------------------------------------------------------------- #
# threshold helpers
# ------------------------------------------------------------------------------------------------------- #

def metrics_at_threshold(y_true: np.ndarray, scores: np.ndarray, threshold: float) -> dict:
    y_pred = (scores >= threshold).astype(int)
    return {
        'threshold': float(threshold),
        'test_accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0),
        'predicted_positive': int(y_pred.sum()),
    }

def best_threshold_by_f1(
    y_true: np.ndarray,
    scores: np.ndarray,
    thresholds: np.ndarray | None = None,
) -> tuple[dict, list[dict]]:
    if thresholds is None:
        thresholds = np.linspace(0.05, 0.95, 37)
    rows = [metrics_at_threshold(y_true, scores, t) for t in thresholds]
    return max(rows, key=lambda row: row['f1']), rows


def pack_tuned_output(
    y_val: np.ndarray,
    val_scores: np.ndarray,
    test_scores: np.ndarray,
    train_scores: np.ndarray | None = None,
    thresholds: np.ndarray | None = None,
) -> dict:
    """
    Choose an F1 cutoff on validation scores, then apply it to test scores.
    """
    best, _ = best_threshold_by_f1(y_val, val_scores, thresholds)
    threshold = best['threshold']
    payload = {
        'scores': np.asarray(test_scores),
        'val_scores': np.asarray(val_scores),
        'threshold': threshold,
        'pred': (np.asarray(test_scores) >= threshold).astype(int),
    }
    if train_scores is not None:
        payload['train_scores'] = np.asarray(train_scores)
    return payload

