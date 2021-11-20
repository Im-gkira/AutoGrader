import warnings
import cv2
import matplotlib.pyplot as plt
import pandas as pd
import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import utilities
import model_load


def warn(*args, **kwargs):
    pass


def grade(image_path_provided):
    warnings.warn = warn

    dict_clean_img = {}
    dict_img = {}

    keras.backend.set_image_data_format("channels_first")
    model_load.load()

    train_datagen = ImageDataGenerator(
        data_format='channels_first',
        zca_whitening=True,
        rotation_range=0.2)

    image_path = image_path_provided
    A = 2
    B = 2
    X = 98
    Y = 3

    img = cv2.imread(image_path)
    plt.figure(figsize=(12, 12))
    # plt.imshow(img)

    workspaces = utilities.extract_box(img)

    df_lines = pd.DataFrame()

    for r, rect in enumerate(workspaces):
        box = img[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
        H, W = box.shape[:2]

        cleaned_orig, y1s, y2s = utilities.extract_line(box, show=True)
        x1s = [0]*len(y1s)
        x2s = [W]*len(y1s)

        df = pd.DataFrame([y1s, y2s, x1s, x2s]).transpose()
        df.columns = ['y1', 'y2', 'x1', 'x2']
        df['box_num'] = r

        df_lines = pd.concat([df_lines, df])

        dict_clean_img.update({r: cleaned_orig})
        dict_img.update({r: box})

        # print(df)

    df_lines['line_name'] = ['%d%d' % (df_lines.box_num.iloc[i], df_lines.index[i])
                             for i in range(len(df_lines))]

    list_chars = list(df_lines.apply(lambda row: utilities.text_segment(
        row['y1'], row['y2'], row['x1'], row['x2'], row['box_num'], row['line_name'], show=True, dict_clean=dict_clean_img), axis=1))

    df_chars = pd.DataFrame(list_chars)
    df_chars.columns = ['box_num', 'line_name', 'char_df']

    box_nums = df_chars.box_num.unique()
    char_area_list = []
    df_chars['char_df'].apply(lambda d: char_area_list.append(list(d['area'])))

    gamma = 0
    max_ar = max([max(i) for i in char_area_list])
    ar_thresh = max_ar*gamma

    df_chars['char_df'] = df_chars['char_df'].apply(
        lambda d: d[d.area > ar_thresh])

    for bn in box_nums:
        print('BOX %d' % (bn+1))
        box_img = dict_clean_img[bn]
        box_img_1 = dict_img[bn]
        box_img = cv2.cvtColor(box_img, cv2.COLOR_GRAY2BGR)

        df = df_chars[df_chars.box_num == bn].copy()
        df_l = df_lines[df_lines["box_num"] == bn].copy()

        df['char_df'].apply(lambda d: d.apply(lambda c: cv2.rectangle(
            box_img, (c['X1'], c['Y1']), (c['X2'], c['Y2']), (255*(c['exp'] == 1), 180, 0), 2+(2*c['exp'])), axis=1))

        df['line_status'] = df['char_df'].apply(
            lambda d: utilities.evaluate(d[["pred", "exp", "pred_proba"]], A, B, X, Y))

        scale_percent = 200
        width = int(box_img.shape[1] * scale_percent / 100)
        height = int(box_img.shape[0] * scale_percent / 100)
        dim = (width, height)
        box_img = cv2.resize(box_img, dim, interpolation=cv2.INTER_AREA)

        df_l['line_status'] = list(df['line_status'])
        df_l.apply(lambda c: cv2.rectangle(box_img_1, (c['x1'], c['y1']), (c['x2'], c['y2']), (255*(
            c['line_status'] == 5), 255*(c['line_status'] == True), 255*(c['line_status'] == False)), 2), axis=1)

        # plt.figure(figsize=(13,7))
        #plt.title('Box - %d' %(bn+1) )
        #plt.imshow(cv2.cvtColor(box_img_1, cv2.COLOR_BGR2RGB))
        cv2.imwrite(f'static/images/new{bn}.jpg',
                    cv2.cvtColor(box_img_1, cv2.COLOR_BGR2RGB))
        # plt.figure()
