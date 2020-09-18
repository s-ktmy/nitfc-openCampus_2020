import tensorflow as tf
from pathlib import Path
import json
from ..const import RNN_GENERATE_MEASURE
from collections import defaultdict
import tensorflow.keras.layers as tfLayers
from tensorflow.keras.models import Sequential
from typing import Union


class generateRNN:

    def __init__(self, modelPath: Path, invDictPath: Path):

        # 辞書データをロード
        with invDictPath.open(mode="r") as fp:
            dictJson = json.load(fp=fp)
        # Tuple -> int
        self.translateDict = defaultdict(int)
        # int -> Tuple
        self.translateDict_inv = defaultdict(tuple)

        for k in dictJson.keys():
            v = dictJson[k]
            t = (v["pitch"], v["rhythm"])
            self.translateDict[t] = int(k)
            self.translateDict_inv[int(k)] = t

        self.model = Sequential()
        self.makeModel(
            layerName="LSTM",
            optimizerFunc="Adam",
            lossFunc=lambda true, pred: tf.keras.losses.sparse_categorical_crossentropy(true, pred, from_logits=True)
        )
        self.model.summary()
        self.model.load_weights(tf.train.latest_checkpoint(modelPath))

    def makeModel(self, layerName: str, optimizerFunc: Union[str, callable], lossFunc: Union[str, callable]):
        layers = []
        assert (layerName == "GRU") or (layerName == "LSTM"), "未実装のレイヤーが指定されました"
        if layerName == "GRU":
            layers = [
                # 埋め込みベクトル化層
                tfLayers.Embedding(
                    input_dim=len(self.translateDict.keys()),
                    output_dim=256,
                    batch_input_shape=[1, None]
                ),
                # GRU層
                tfLayers.GRU(
                    units=1024,
                    return_sequences=True,
                    stateful=True,
                    recurrent_initializer="glorot_uniform",
                ),
                # 全結合層
                tfLayers.Dense(len(self.translateDict.keys()))
            ]
        elif layerName == "LSTM":
            layers = [
                # 埋め込みベクトル化層
                tfLayers.Embedding(
                    input_dim=len(self.translateDict.keys()),
                    output_dim=256,
                    batch_input_shape=[1, None]
                ),
                # LSTM層
                tfLayers.LSTM(
                    units=1024,
                    return_sequences=True,
                    stateful=True,
                    recurrent_initializer="glorot_uniform",
                ),
                # 全結合層
                tfLayers.Dense(len(self.translateDict.keys()))
            ]

        for layer in layers:
            self.model.add(layer)

        self.model.compile(
            optimizer=optimizerFunc,
            loss=lossFunc
        )

    def generate(self, seed: list) -> list:
        self.model.reset_states()

        inputVec = list(map(lambda d: self.translateDict[d], seed))
        result = inputVec.copy()
        inputVec = tf.expand_dims(inputVec, 0)
        print(inputVec)
        timeptr = 0

        while timeptr < 16 * RNN_GENERATE_MEASURE:
            predict = self.model(inputVec)

            predict = tf.squeeze(predict, 0)
            predict_value = tf.random.categorical(predict, num_samples=1)[-1, 0].numpy()

            inputVec = tf.expand_dims([predict_value], 0)
            length = self.translateDict_inv[predict_value][1]
            result.append(predict_value)
            timeptr += length

        # はみ出した分を短くする
        overrun = timeptr - 16 * RNN_GENERATE_MEASURE
        pr_Result = list(map(lambda d: self.translateDict_inv[d], result))
        res = []
        for pr in pr_Result:
            res.append([pr[0], pr[1]])

        res[-1][1] -= overrun

        return res
