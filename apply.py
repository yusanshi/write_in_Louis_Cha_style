import os
import jieba
import pickle
import tensorflow as tf
from tensorflow import keras
from train import build_model
from config import MODEL_PATH, EMBEDDING_DIM, RNN_UNITS, TEMPERATURE


def apply(beginning, num_of_chars):
    # load model

    # model = keras.models.load_model(os.path.join(MODEL_PATH, 'model.h5'))
    with open(os.path.join(MODEL_PATH, 'text_to_int.pickle'), 'rb') as handle:
        text_to_int = pickle.load(handle)
    with open(os.path.join(MODEL_PATH, 'int_to_text.pickle'), 'rb') as handle:
        int_to_text = pickle.load(handle)
    with open(os.path.join(MODEL_PATH, 'vocab_size.pickle'), 'rb') as handle:
        vocab_size = pickle.load(handle)

    model = build_model(vocab_size=vocab_size,
                        embedding_dim=EMBEDDING_DIM,
                        rnn_units=RNN_UNITS,
                        batch_size=1)

    model.load_weights(os.path.join(MODEL_PATH, 'model'))
    
    print('Load model successfully.')

    input_seq_jieba = [l for l in list(jieba.cut(beginning)) if l != ' ']
    input_seq_int = [text_to_int[w]
                     for w in input_seq_jieba if w in text_to_int]
    if len(input_seq_int) == 0:
        input_seq_int = [text_to_int['<br>']]

    input_seq = tf.expand_dims(input_seq_int, axis=0)  # Add a dim

    text_generated = ''
    model.reset_states()  # Add this because 'stateful=True'
    while len(text_generated) < num_of_chars:
        predictions = model(input_seq)
        predictions = tf.squeeze(predictions, axis=0)
        predictions /= TEMPERATURE
        predicted_id = tf.random.categorical(
            predictions, num_samples=1).numpy()[0][0]
        input_seq = tf.expand_dims([predicted_id], 0)  # Add a dim
        text_generated += int_to_text[predicted_id] if int_to_text[predicted_id] != '<br>' else '\n'

    return text_generated
