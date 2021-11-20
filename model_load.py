import keras

DCCNN_model = None


def load():
    try:
        global DCCNN_model
        DCCNN_model = keras.models.load_model(
            'models/DCNN_10AD_sy.h5', compile=False)
        print("Load Successful")

    except Exception as e:
        print('Model couldnot be loaded', e)
