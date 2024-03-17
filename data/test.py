import sqlite3
import pickle
import ast
from sklearn.preprocessing import StandardScaler
import pandas as pd
from category_encoders import TargetEncoder
from sklearn.decomposition import PCA


def some_ml_function(file_name, cursor):
    # здесь код ML
    with open('logreg.pkl', 'rb') as f:
        logreg = pickle.load(f)
    with open('features.txt', 'r') as f:
        features = ast.literal_eval(f.read())
    with open('continuous.txt', 'r') as f:
        continuous = ast.literal_eval(f.read())
    with open('categorical.txt', 'r') as f:
        categorical = ast.literal_eval(f.read())
    X_train = pd.read_parquet('df_clean.parquet')[features]
    y_train = pd.read_parquet('df_clean.parquet')['target']

    df_test = pd.DataFrame(data=pd.read_parquet(file_name))
    X_test = df_test[['id']+features]

    cursor.execute('UPDATE tasks SET percent = ? WHERE id = ?',
                   (10, file_id))  # вставить между кодом
    connection.commit()

    scaler = StandardScaler()
    X_train_std = X_train.copy()
    X_train_std[continuous] = scaler.fit_transform(X_train[continuous])
    X_test_std = X_test.copy()
    X_test_std[continuous] = scaler.transform(X_test_std[continuous])

    cursor.execute('UPDATE tasks SET percent = ? WHERE id = ?', (25, file_id))
    connection.commit()

    enc = TargetEncoder(cols=categorical).fit(X_train_std[categorical], y_train)
    X_train_std_enc = X_train_std.copy()
    X_train_std_enc[categorical] = enc.transform(X_train_std[categorical])
    X_test_std_enc = X_test_std.copy()
    X_test_std_enc[categorical] = enc.transform(X_test_std[categorical])

    cursor.execute('UPDATE tasks SET percent = ? WHERE id = ?', (50, file_id))
    connection.commit()

    n_components = 20
    pca = PCA(n_components=20)
    pca.fit(X_train_std_enc)
    X_test_std_enc_pca = pd.DataFrame(pca.transform(X_test_std_enc.drop(columns=['id'])))
    for i in range(n_components):
        X_test_std_enc_pca.rename(columns={i: 'pca_feature_'+str(i)}, inplace=True)
    X_test_std_enc_pca = pd.concat([X_test_std_enc_pca, X_test_std_enc['id']], axis=1)

    cursor.execute('UPDATE tasks SET percent = ? WHERE id = ?', (75, file_id))
    connection.commit()
    h = list(X_test_std_enc_pca.drop(columns=['id']).columns[X_test_std_enc_pca.drop(columns=['id']).isnull().any()])
    pred_test = logreg.predict(X_test_std_enc_pca.drop(columns=['id']))
    for i in range(pred_test):
        cursor.execute(
            'INSERT INTO clients (name, result) VALUES (?, ?)', (i[0], i[1]))
    cursor.execute('UPDATE tasks SET percent = ? WHERE id = ?', (100, file_id))
    connection.commit()

    # plt.savefig('name.png') - это для сохраниения графика и до show
    # конец кода
    return 0


connection = sqlite3.connect('data.sqlite3')
cursor = connection.cursor()
cursor.execute('SELECT id, filename FROM tasks WHERE percent = 0 LIMIT 1')
data = cursor.fetchone()
if (data):
    file_id = data[0]
    file_name = data[1]  # здесь будет название файлика
    some_ml_function(file_name, cursor)
connection.close()
