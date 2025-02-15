import pandas as pd
import numpy as np


def handle_ordered_categorical_cols(df):
    # 'Histological Diagnosis'
    pass


def handle_categorical_cols(df, encoder=None):
    from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder
    # 'Form Name'
    categorical_cols = [
        ' Hospital',
        'אבחנה-Margin Type'
    ]  # TODO 'אבחנה-Basic stage',

    if encoder is None:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse=False)
        encoder.fit(df[categorical_cols])
    transformed = encoder.transform(df[categorical_cols])
    transformed_df = pd.DataFrame(transformed, columns=encoder.get_feature_names_out(categorical_cols))
    result = pd.concat([df, transformed_df], axis=1)
    return result, encoder


def drop_cols(df, cols):
    # User name
    for col_name in cols:
        if col_name in df.columns:
            df.drop(col_name, axis=1, inplace=True)


def handle_dates_features(df):
    # handle unknown dates in order to subtract dates:
    # in total _ samples were dropped:
    # (df['אבחנה-Surgery date1'] == 'Unknown').sum()
    # (df['אבחנה-Surgery date2'] == 'Unknown').sum()
    # (df['אבחנה-Surgery date3'] == 'Unknown').sum()

    df = df[df['אבחנה-Surgery date1'] != 'Unknown']
    df = df[df['אבחנה-Surgery date2'] != 'Unknown']
    df = df[df['אבחנה-Surgery date3'] != 'Unknown']
    df.reset_index()

    # 'diagnosis_and_surgery_days_dif'  # 33-7
    dif = pd.to_datetime(df['אבחנה-Diagnosis date']) - pd.to_datetime(df['surgery before or after-Activity date'])
    df['diagnosis_and_surgery_days_dif'] = dif.dt.days

    # 'first_and_second_surgery_days_diff' # 22-21
    dif = pd.to_datetime(df['אבחנה-Surgery date2']) - pd.to_datetime(df['אבחנה-Surgery date1'])
    df['first_and_second_surgery_days_diff'] = dif.dt.days

    # 'second_and_third_surgery_days_diff' # 23-22
    dif = pd.to_datetime(df['אבחנה-Surgery date3']) - pd.to_datetime(df['אבחנה-Surgery date2'])
    df['second_and_third_surgery_days_diff'] = dif.dt.days

    # drop
    drop_cols(df, ['אבחנה-Surgery date1', 'אבחנה-Surgery date2', 'אבחנה-Surgery date3',
                   'surgery before or after-Activity date', 'אבחנה-Diagnosis date'])
    return df


def handle_ivi(df):
    # utilities.present_unique_values(df, col_name='אבחנה-Ivi -Lymphovascular invasion')
    positive_val = ['yes', '+', 'extensive', 'pos', 'MICROPAPILLARY VARIANT', '(+)']
    negative_val = ['not', 'none', 'neg', 'no', '-', '(-)', 'NO', 'No']

    last = df['אבחנה-Ivi -Lymphovascular invasion'] == 'yes'

    for pos_val in positive_val:
        cur = df['אבחנה-Ivi -Lymphovascular invasion'] == pos_val
        last = cur | last
    df['pos_ivi'] = last

    last = df['אבחנה-Ivi -Lymphovascular invasion'] == 'not'
    for neg_val in negative_val:
        cur = df['אבחנה-Ivi -Lymphovascular invasion'] == neg_val
        last = cur | last
    df['neg_ivi'] = last

    return df


def handle_ki67(df):
    def get_low():
        words = ['Score 1', 'Score1-2', 'Very Low <3%', 'low-int', 'Low', 'LOW', 'low'
                 , 'Very Low', 'score 1-2', 'score 1', 'score 2', 'Score 1-2','score1-2', 'score1-2',
                 'score1', 'score2',
                 'Score1-2', 'no', 'No', 'NO', 'negative', 'Negative', 'score 1']
        result = []
        for val in unique_vals:
            if type(val) is str:

                for i in range(1, 20):
                    if str(i) in val:
                        result.append(val)

                for word in words:
                    if word in val:
                        result.append(val)
        unique_values_minus_result = [val for val in unique_vals if val not in result]
        return result, unique_values_minus_result

    def get_medium():
        words = ['score1-2', 'score 2', 'Score 2', 'Score II', 'intermediate', 'intermediate',  'Intermediate'
                 ,'score II', 'score 3', 'Score 2-3', 'Score 3', 'Score2-3', 'Score3', 'score3','Score I-2','Score 2' ]
        result = []
        for val in unique_vals:
            if type(val) is str:

                for i in range(20, 50):
                    if str(i) in val:
                        result.append(val)
                for word in words:
                    if word in val:
                        result.append(val)
        unique_values_minus_result = [val for val in unique_vals if val not in result]
        return result, unique_values_minus_result

    def get_medium_high():
        words = ['score4']
        result = []
        for val in unique_vals:
            if type(val) is str:

                for i in range(50, 70):
                    if str(i) in val:
                        result.append(val)
                for word in words:
                    if word in val:
                        result.append(val)
        unique_values_minus_result = [val for val in unique_vals if val not in result]
        return result, unique_values_minus_result

    def get_high():
        words = ['score 3-4', 'score 3', 'High', 'Score 4', 'high', 'HIGH','High', 'score IV',
                 'Score 6', ]
        result = []
        for val in unique_vals:
            if type(val) is str:
                for i in range(70, 100):
                    if str(i) in val:
                        result.append(val)
                for word in words:
                    if word in val:
                        result.append(val)
            unique_values_minus_result = [val for val in unique_vals if val not in result]
        return result, unique_values_minus_result

    # utilities.present_unique_values(df, 'אבחנה-KI67 protein')
    unique_vals = df['אבחנה-KI67 protein'].unique()
    high, unique_vals = get_high()
    medium_high, unique_vals = get_medium_high()
    medium, unique_vals = get_medium()
    low, unique_vals = get_low()

    low_indices = set()
    for val in low:
        cur = df['אבחנה-KI67 protein'] == val
        low_indices |= set(cur[cur].index)
    df.loc[low_indices, 'אבחנה-KI67 protein'] = 0

    medium_indices = set()
    for val in medium:
        cur = df['אבחנה-KI67 protein'] == val
        medium_indices |= set(cur[cur].index)
    df.loc[medium_indices, 'אבחנה-KI67 protein'] = 1

    medium_high_indices = set()
    for val in medium_high:
        cur = df['אבחנה-KI67 protein'] == val
        medium_high_indices |= set(cur[cur].index)
    df.loc[medium_high_indices, 'אבחנה-KI67 protein'] = 2

    high_indices = set()
    for val in high:
        cur = df['אבחנה-KI67 protein'] == val
        high_indices |= set(cur[cur].index)
    df.loc[high_indices, 'אבחנה-KI67 protein'] = 3

    # todo: decide based on correlation nan values
    nan_idx = df[df['אבחנה-KI67 protein'].isnull()].index.tolist()
    df.loc[nan_idx, 'אבחנה-KI67 protein'] = -10

    # todo: handle with values that not appears in the list ahead
    union_idx = {*low_indices, *medium_indices, *medium_high_indices, *high_indices, *nan_idx}
    different_values = [i for i in range(len(df['אבחנה-KI67 protein'])) if i not in union_idx]

    df.loc[different_values, 'אבחנה-KI67 protein'] = 1.5
    df['אבחנה-KI67 protein'] = df['אבחנה-KI67 protein'].astype(float)
    return df


def main():
    df = pd.read_csv(r'train.feats.csv', parse_dates=[
        "אבחנה-Diagnosis date",
        "אבחנה-Surgery date1",
        "אבחנה-Surgery date2",
        "אבחנה-Surgery date3",
        "surgery before or after-Activity date"
    ], infer_datetime_format=True, dayfirst=True)
    # drop_cols(df, ['User Name'])
    # df = handle_dates_features(df)
    # df = handle_categorical_cols(df)
    df = handle_ivi(df)
    # df = handle_ki67(df)


if __name__ == '__main__':
    main()
