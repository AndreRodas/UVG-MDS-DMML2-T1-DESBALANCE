from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support
from sklearn.impute import SimpleImputer
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import RobustScaler
from sklearn.preprocessing import StandardScaler

from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler

import pandas as pd
import numpy as np


if __name__ == '__main__':

    imputar_datos = True
    normalizar_datos = True #necesario normalizar los datos para no tener error en la regresion lineal
    scaler_type = "Standard"  # La otra opcion es Robust
    cross_validation = False
    rebalancear = True
    oversampling = True # Tenemos mejor recall y f1 si agregamos el oversampling
    undersampling = True
    do_eval = False

    #one_hot_encoder_min_frequency = 2400
    random_state = 0
    smote_sampling = 0.1 
    under_sampling_ratio = 0.5

    #Esta parte de 'Leyendo archivo princial' y 'Generando archivos...' se puede obviar una vez ya estén generados, tomar en cuenta...
    # 60% entrenamiento 20% validacion y 20% test

    print("\nLeyendo archivo princial")
    #df = pd.read_csv("C:/Users/ajrodas/Documents/GitHub/UVG-MDS-DMML2-CLASDESB/creditcard.csv")
    # 60% entrenamiento 20% validacion y 20% test
    #train, validation, test = np.split(df.sample(frac=1), [int(.6*len(df)), int(.8*len(df))])

    print("\nGenerando archivos...")
    #train.to_csv('train.csv', index=False)
    #validation.to_csv('validation.csv', index=False)
    #test.to_csv('test.csv', index=False)

    # Leemos los archivos
    print("\nLeyendo archivos...")
    train = pd.read_csv("C:/Users/ajrodas/Documents/GitHub/UVG-MDS-DMML2-CLASDESB/train.csv")
    validation = pd.read_csv("C:/Users/ajrodas/Documents/GitHub/UVG-MDS-DMML2-CLASDESB/validation.csv")
    test = pd.read_csv("C:/Users/ajrodas/Documents/GitHub/UVG-MDS-DMML2-CLASDESB/test.csv")

    # Seleccionamos las features que nos interesan
    # Ignoramos las que son id unicas de cada ejemplo
    # Las features de tiempo podrían ser interesantes ya que algunas veces
    # los malwares son dispersados por redes basadas en ciertas partes del mundo
    # por lo que saber cuando se vio por primera vez podria ser util.
    # Les queda de ejercicio generar esas features.
    feature_cols = ['V1','V2','V3','V4','V5','V6','V7','V8','V9','V10','V11','V12','V13','V14','V15','V16','V17','V18','V19','V20','V21','V22','V23','V24','V25','V26','V27','V28','Amount']

    X = train.loc[:, feature_cols]
    y = train.Class

    if imputar_datos:
        print("Imputando datos...")
        # Por simpleza solo vamos a llenar los datos con el valor promedio
        # probablemente podemos hacer algo mejor...
        imputer = SimpleImputer()
        X = imputer.fit_transform(X)

    if normalizar_datos:
        print("Estandarizando datos...")
        # Vamos a utilizar RobustScaler que utiliza la mediana en lugar de la media
        # Es posible probar ambos y ver cual funciona mejor, dado que tenemos
        # datos con valores anomalos, considere que este era mejor.
        if scaler_type == "Standard":
            scaler = StandardScaler().fit(X)
        else:
            scaler = RobustScaler().fit(X)
        X = scaler.transform(X)

    #No lo incluyo porque no tengo variables categoricas en el dataset
    #if add_categorical:
        #print("Creando features categoricas...")
        # Vamos a utilizar OneHotEncoding para usar las extensiones de los archivos
        # Tambien nos vamos a quedar solo con los valores mas comunes, esto requiere
        # busqueda de hiperparametros
        #extensions = train.loc[:, ['Extension']].select_dtypes(include=[object])
        #enc = OneHotEncoder(handle_unknown='infrequent_if_exist', min_frequency=one_hot_encoder_min_frequency)
        #enc.fit(extensions)
        #extensionFeatures = enc.transform(extensions).toarray()
        #X = pd.concat([pd.DataFrame(X), pd.DataFrame(extensionFeatures)], axis=1)

    print("\nEvaluacion sin rebalanceo")
    clf = LogisticRegression(random_state=random_state).fit(X, y)
    train_metrics = precision_recall_fscore_support(y, clf.predict(X), average=None, labels=[0, 1])
    print('\nTraining metrics')
    print('Precision: ' + str(train_metrics[0]))
    print('Recall: ' + str(train_metrics[1]))
    print('F1: ' + str(train_metrics[2]))

    X_val = validation.loc[:, feature_cols]
    y_val = validation.Class
    if imputar_datos:
        X_val = imputer.transform(X_val)
    if normalizar_datos:
        X_val = scaler.transform(X_val)
    #if add_categorical:
        #val_extensions = validation.loc[:, ['Extension']].select_dtypes(include=[object])
        #val_extensionFeatures = enc.transform(val_extensions).toarray()
        #X_val = pd.concat([pd.DataFrame(X_val), pd.DataFrame(val_extensionFeatures)], axis=1)
    val_metrics = precision_recall_fscore_support(y_val, clf.predict(X_val), average=None, labels=[0, 1])
    print('\nValidation metrics')
    print('Precision: ' + str(val_metrics[0]))
    print('Recall: ' + str(val_metrics[1]))
    print('F1: ' + str(val_metrics[2]))

    if cross_validation:
        print("\nEvaluando modelo SIN rebalanceo, utilizando cross fold validation")
        clf = LogisticRegression(random_state=random_state)
        cv = RepeatedStratifiedKFold(n_splits=10, random_state=random_state)
        scores = cross_val_score(clf, X, y, scoring='roc_auc', cv=cv, n_jobs=1)
        print("avg. roc auc: " + str(np.mean(scores)))

    if rebalancear:
        print("\nRebalanceando")
        if oversampling:
            sm = SMOTE(random_state=random_state, sampling_strategy=smote_sampling)
            X, y = sm.fit_resample(X, y)
        if undersampling:
            under = RandomUnderSampler(random_state=random_state, sampling_strategy=under_sampling_ratio)
            X, y = under.fit_resample(X, y)

        print("Evaluacion CON rebalanceo")
        clf = LogisticRegression(random_state=random_state).fit(X, y)
        train_metrics = precision_recall_fscore_support(y, clf.predict(X), average=None, labels=[0, 1])
        print('\nTraining metrics')
        print('Precision: ' + str(train_metrics[0]))
        print('Recall: ' + str(train_metrics[1]))
        print('F1: ' + str(train_metrics[2]))

        X_val = validation.loc[:, feature_cols]
        y_val = validation.Class
        if imputar_datos:
            X_val = imputer.transform(X_val)
        if normalizar_datos:
            X_val = scaler.transform(X_val)
        #if add_categorical:
            #val_extensions = validation.loc[:, ['Extension']].select_dtypes(include=[object])
            #val_extensionFeatures = enc.transform(val_extensions).toarray()
            #X_val = pd.concat([pd.DataFrame(X_val), pd.DataFrame(val_extensionFeatures)], axis=1)
        val_metrics = precision_recall_fscore_support(y_val, clf.predict(X_val), average=None, labels=[0, 1])
        print('\nValidation metrics')
        print('Precision: ' + str(val_metrics[0]))
        print('Recall: ' + str(val_metrics[1]))
        print('F1: ' + str(val_metrics[2]))

        if cross_validation:
            print("\nEvaluando modelo CON rebalanceo, utilizando cross fold validation")
            clf = LogisticRegression(random_state=random_state)
            cv = RepeatedStratifiedKFold(n_splits=10, random_state=random_state)
            scores = cross_val_score(clf, X, y, scoring='roc_auc', cv=cv, n_jobs=1)
            print("avg. roc auc: " + str(np.mean(scores)))

    if do_eval:
        X = train.loc[:, feature_cols]
        y = train.Class
        X_val = validation.loc[:, feature_cols]
        y_val = validation.Class
        X_allTrain = pd.concat([pd.DataFrame(X), pd.DataFrame(X_val)])
        y_allTrain = np.concatenate((y, y_val), axis=0)
        X_test = test.loc[:, feature_cols]
        y_test = test.Class
        if imputar_datos:
            imputer = SimpleImputer()
            X_allTrain = imputer.fit_transform(X_allTrain)
        if normalizar_datos:
            if scaler_type == "Standard":
                scaler = StandardScaler().fit(X_allTrain)
            else:
                scaler = RobustScaler().fit(X_allTrain)
            X_allTrain = scaler.transform(X_allTrain)
        #if add_categorical:
            #all_train = pd.concat([train, validation])
            #extensions = all_train.loc[:, ['Extension']].select_dtypes(include=[object])
            #enc = OneHotEncoder(handle_unknown='infrequent_if_exist', min_frequency=one_hot_encoder_min_frequency)
            #enc.fit(extensions)
            #extensionFeatures = enc.transform(extensions).toarray()
            #X_allTrain = pd.concat([pd.DataFrame(X_allTrain), pd.DataFrame(extensionFeatures)], axis=1)
        if rebalancear:
            if oversampling:
                sm = SMOTE(random_state=random_state, sampling_strategy=smote_sampling)
                X_allTrain, y_allTrain = sm.fit_resample(X_allTrain, y_allTrain)
            if undersampling:
                under = RandomUnderSampler(random_state=random_state, sampling_strategy=under_sampling_ratio)
                X_allTrain, y_allTrain = under.fit_resample(X_allTrain, y_allTrain)
        clf = LogisticRegression(random_state=random_state).fit(X_allTrain, y_allTrain)
        if imputar_datos:
            X_test = imputer.transform(X_test)
        if normalizar_datos:
            X_test = scaler.transform(X_test)
        #if add_categorical:
            #test_extensions = test.loc[:, ['Extension']].select_dtypes(include=[object])
            #test_extensionFeatures = enc.transform(test_extensions).toarray()
            #X_test = pd.concat([pd.DataFrame(X_test), pd.DataFrame(test_extensionFeatures)], axis=1)
        test_metrics = precision_recall_fscore_support(y_test, clf.predict(X_test), average=None,labels=[0, 1])
        print('\nTesting metrics')
        print('Precision: ' + str(test_metrics[0]))
        print('Recall: ' + str(test_metrics[1]))
        print('F1: ' + str(test_metrics[2]))
