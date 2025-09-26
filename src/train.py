from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

def train_and_eval(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
    model = LogisticRegression(max_iter=1000, class_weight='balanced')
    model.fit(X_train, y_train)
    probs = model.predict_proba(X_test)[:,1]
    return {
        'pr_auc': average_precision_score(y_test, probs),
        'roc_auc': roc_auc_score(y_test, probs)
    }
