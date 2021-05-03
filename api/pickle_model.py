import pickle
import tempfile
from tensorflow.keras.models import load_model, save_model, Model

# Hotfix function
def make_picklable():
    def __getstate__(self):
        model_str = ""
        with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=True) as fd:
            save_model(self, fd.name, overwrite=True)
            model_str = fd.read()
        d = {'model_str': model_str}
        return d

    def __setstate__(self, state):
        with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=True) as fd:
            fd.write(state['model_str'])
            fd.flush()
            model = load_model(fd.name)
        self.__dict__ = model.__dict__


    cls = Model
    cls.__getstate__ = __getstate__
    cls.__setstate__ = __setstate__


if __name__ == '__main__':
    # Run the function
    make_picklable()

    model = load_model('tmp/GloVe_LSTM_SA_Classifier.h5')
    print(model.summary())

    # Save
    with open('GloVe_LSTM_SA_Classifier.sav', 'wb') as f:
        pickle.dump(model, f)