import sklearn
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class LinearRegression:
    def __init__(self, data, X, y, X_single):
        """
        creates a basic linear regression model
        """
        self.model = sklearn.linear_model.LinearRegression()
        self.data = data
        self.X = X
        self.y = y
        self.X_single = X_single
        self.X_train, self.X_test, self.y_train, self.y_test = sklearn.model_selection.train_test_split(
            self.X_single, 
            self.y, 
            test_size=0.2, 
            random_state=42
        )
    
    def train(self):
        """
        https://youtu.be/29jij4ldkNs?si=3kWjKt66zadK55g4
        """
        self.model.fit(self.X_train, self.y_train)
        self.y_pred = self.model.predict(self.X_test)
        self.mse = sklearn.metrics.mean_squared_error(self.y_test, self.y_pred)
        self.r2 = sklearn.metrics.r2_score(self.y_test, self.y_pred)
        
    def predict(self, median_income):
        """
        predicts median house value (in $100,000s) given a median income.
        """
        input_array = np.array([median_income])  # reshape to (1, 1)
        prediction = self.model.predict(input_array)
        return prediction[0]
    
    def plot(self):
        plt.scatter(self.X_test, self.y_test, color='blue', label='Actual')
        plt.plot(self.X_test, self.y_pred, color='red', linewidth=2, label='Predicted')
        plt.xlabel('Median Income')
        plt.ylabel('Median House Value ($100,000s)')
        plt.title('Linear Regression: Median Income vs House Value')
        plt.legend()
        plt.show()
    
    
class LogisticRegressionClassifier:
    def __init__(self, X, y, test_size=0.2, random_state=42):
        self.model = sklearn.linear_model.LogisticRegression(max_iter=10000)
        self.X = X
        self.y = y
        self.X_train, self.X_test, self.y_train, self.y_test = sklearn.model_selection.train_test_split(
            self.X, 
            self.y, 
            test_size=test_size, 
            random_state=random_state
        )        

    def train(self):
        self.model.fit(self.X_train, self.y_train)

    def evaluate(self):
        y_pred = self.model.predict(self.X_test)
        self.accuracy = sklearn.metrics.accuracy_score(self.y_test, y_pred)
        self.precision = sklearn.metrics.precision_score(self.y_test, y_pred)
        self.recall = sklearn.metrics.recall_score(self.y_test, y_pred)
        self.f1 = sklearn.metrics.f1_score(self.y_test, y_pred)
        self.conf_matrix = sklearn.metrics.confusion_matrix(self.y_test, y_pred)
        self.report = sklearn.metrics.classification_report(self.y_test, y_pred)
        
    def summary(self):
        print('Logistic Regression Performance')
        print('-'*32)
        print(f'Accuracy:  {self.accuracy:.2f}')
        print(f'Precision: {self.precision:.2f}')
        print(f'Recall:    {self.recall:.2f}')
        print(f'F1 Score:  {self.f1:.2f}')
        print('\nConfusion Matrix:\n', self.conf_matrix)
        print('\nClassification Report:\n', self.report)
        
    def plot_evaluation(self):
        # predict probabilities
        y_prob = self.model.predict_proba(self.X_test)[:, 1]
        fpr, tpr, thresholds = sklearn.metrics.roc_curve(self.y_test, y_prob)
        roc_auc = sklearn.metrics.auc(fpr, tpr)
        # plot roc curve
        plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1)
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC)')
        plt.legend(loc='lower right')
        # plot confusion matrix
        plt.subplot(1, 2, 2)
        sns.heatmap(self.conf_matrix, annot=True, fmt='d', cmap='Blues')
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.tight_layout()
        plt.show()