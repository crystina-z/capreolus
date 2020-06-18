import os
from pathlib import Path

import pytest
import torch
from pymagnitude import Magnitude

from capreolus.benchmark import DummyBenchmark
from capreolus.extractor import EmbedText, BertText, BertPassage
from capreolus.reranker.PACRR import PACRR
from capreolus.sampler import TrainTripletSampler, PredSampler, TrainPairSampler
from capreolus.tests.common_fixtures import tmpdir_as_cache, dummy_index
from capreolus.tokenizer import AnseriniTokenizer, BertTokenizer
from capreolus.trainer import PytorchTrainer, TensorFlowTrainer
from capreolus.extractor.bagofwords import BagOfWords
from capreolus.extractor.deeptileextractor import DeepTileExtractor
from capreolus.reranker.CDSSM import CDSSM
from capreolus.reranker.DeepTileBar import DeepTileBar
from capreolus.reranker.DSSM import DSSM
from capreolus.reranker.HINT import HINT
from capreolus.reranker.KNRM import KNRM
from capreolus.reranker.PACRR import PACRR
from capreolus.reranker.POSITDRMM import POSITDRMM
from capreolus.reranker.CDSSM import CDSSM
from capreolus.reranker.TFBERTMaxP import TFBERTMaxP
from capreolus.reranker.TFKNRM import TFKNRM
from capreolus.reranker.TK import TK


def test_knrm_pytorch(dummy_index, tmpdir, tmpdir_as_cache, monkeypatch):
    def fake_magnitude_embedding(*args, **kwargs):
        return Magnitude(None)

    monkeypatch.setattr(EmbedText, "_get_pretrained_emb", fake_magnitude_embedding)

    reranker = KNRM(
        {
            "gradkernels": True,
            "scoretanh": False,
            "singlefc": True,
            "finetune": False,
            "trainer": {"niters": 1, "itersize": 4, "batch": 2},
        },
        provide={"index": dummy_index},
    )
    extractor = reranker.extractor
    metric = "map"
    benchmark = DummyBenchmark()

    extractor.preprocess(["301"], ["LA010189-0001", "LA010189-0002"], benchmark.topics[benchmark.query_type])
    reranker.build_model()

    train_run = {"301": ["LA010189-0001", "LA010189-0002"]}
    train_dataset = TrainTripletSampler()
    train_dataset.prepare(train_run, benchmark.qrels, extractor)

    dev_dataset = PredSampler()
    dev_dataset.prepare(train_run, benchmark.qrels, extractor)
    reranker.trainer.train(
        reranker, train_dataset, Path(tmpdir) / "train", dev_dataset, Path(tmpdir) / "dev", benchmark.qrels, metric
    )

    assert os.path.exists(Path(tmpdir) / "train" / "dev.best")


def test_knrm_tf(dummy_index, tmpdir, tmpdir_as_cache, monkeypatch):
    def fake_magnitude_embedding(*args, **kwargs):
        return Magnitude(None)

    monkeypatch.setattr(EmbedText, "_get_pretrained_emb", fake_magnitude_embedding)

    reranker = TFKNRM(
        {"gradkernels": True, "finetune": False, "trainer": {"niters": 1, "itersize": 4, "batch": 2}},
        provide={"index": dummy_index},
    )
    extractor = reranker.extractor
    metric = "map"
    benchmark = DummyBenchmark()

    extractor.preprocess(["301"], ["LA010189-0001", "LA010189-0002"], benchmark.topics[benchmark.query_type])
    reranker.build_model()

    train_run = {"301": ["LA010189-0001", "LA010189-0002"]}
    train_dataset = TrainTripletSampler()
    train_dataset.prepare(train_run, benchmark.qrels, extractor)
    dev_dataset = PredSampler()
    dev_dataset.prepare(train_run, benchmark.qrels, extractor)
    reranker.trainer.train(
        reranker, train_dataset, Path(tmpdir) / "train", dev_dataset, Path(tmpdir) / "dev", benchmark.qrels, metric
    )

    assert os.path.exists(Path(tmpdir) / "train" / "dev.best.index")

def test_knrm_tf_ce(dummy_index, tmpdir, tmpdir_as_cache, monkeypatch):
    def fake_magnitude_embedding(*args, **kwargs):
        return Magnitude(None)

    monkeypatch.setattr(EmbedText, "_get_pretrained_emb", fake_magnitude_embedding)

    reranker = TFKNRM(
        {"gradkernels": True, "finetune": False, "trainer": {"niters": 1, "itersize": 4, "batch": 2, "loss": "binary_crossentropy"}},
        provide={"index": dummy_index},
    )
    extractor = reranker.extractor
    metric = "map"
    benchmark = DummyBenchmark()

    extractor.preprocess(["301"], ["LA010189-0001", "LA010189-0002"], benchmark.topics[benchmark.query_type])
    reranker.build_model()

    train_run = {"301": ["LA010189-0001", "LA010189-0002"]}
    train_dataset = TrainPairSampler()
    train_dataset.prepare(train_run, benchmark.qrels, extractor)
    dev_dataset = PredSampler()
    dev_dataset.prepare(train_run, benchmark.qrels, extractor)
    reranker.trainer.train(
        reranker, train_dataset, Path(tmpdir) / "train", dev_dataset, Path(tmpdir) / "dev", benchmark.qrels, metric
    )

    assert os.path.exists(Path(tmpdir) / "train" / "dev.best.index")

def test_pacrr(dummy_index, tmpdir, tmpdir_as_cache, monkeypatch):
    def fake_magnitude_embedding(*args, **kwargs):
        return Magnitude(None)

    monkeypatch.setattr(EmbedText, "_get_pretrained_emb", fake_magnitude_embedding)

    reranker = PACRR(
        {
            "nfilters": 32,
            "idf": True,
            "kmax": 2,
            "combine": 32,
            "nonlinearity": "relu",
            "trainer": {"niters": 1, "itersize": 4, "batch": 2},
        },
        provide={"index": dummy_index},
    )
    extractor = reranker.extractor
    metric = "map"
    benchmark = DummyBenchmark()

    extractor.preprocess(["301"], ["LA010189-0001", "LA010189-0002"], benchmark.topics[benchmark.query_type])
    reranker.build_model()

    train_run = {"301": ["LA010189-0001", "LA010189-0002"]}
    train_dataset = TrainTripletSampler(train_run, benchmark.qrelsextractor)
    dev_dataset = PredSampler(train_run, benchmark.qrels, extractor)
    reranker.trainer.train(
        reranker, train_dataset, Path(tmpdir) / "train", dev_dataset, Path(tmpdir) / "dev", benchmark.qrels, metric
    )

    assert os.path.exists(Path(tmpdir) / "train" / "dev.best")


def test_dssm_unigram(dummy_index, tmpdir, tmpdir_as_cache, monkeypatch):
    def fake_magnitude_embedding(*args, **kwargs):
        return Magnitude(None)

    monkeypatch.setattr(EmbedText, "_get_pretrained_emb", fake_magnitude_embedding)

    reranker = DSSM({"nhiddens": "56", "trainer": {"niters": 1, "itersize": 4, "batch": 2}}, provide={"index": dummy_index})
    extractor = reranker.extractor
    metric = "map"
    benchmark = DummyBenchmark()

    extractor.preprocess(["301"], ["LA010189-0001", "LA010189-0002"], benchmark.topics[benchmark.query_type])
    reranker.build_model()

    train_run = {"301": ["LA010189-0001", "LA010189-0002"]}
    train_dataset = TrainTripletSampler(train_run, benchmark.qrels, extractor)
    dev_dataset = PredSampler(train_run, benchmark.qrels, extractor)
    reranker.trainer.train(
        reranker, train_dataset, Path(tmpdir) / "train", dev_dataset, Path(tmpdir) / "dev", benchmark.qrels, metric
    )

    assert os.path.exists(Path(tmpdir) / "train" / "dev.best")


def test_tk(dummy_index, tmpdir, tmpdir_as_cache, monkeypatch):
    def fake_magnitude_embedding(*args, **kwargs):
        return Magnitude(None)

    monkeypatch.setattr(EmbedText, "_get_pretrained_emb", fake_magnitude_embedding)

    reranker = TK(
        {
            "gradkernels": True,
            "scoretanh": False,
            "singlefc": True,
            "projdim": 32,
            "ffdim": 100,
            "numlayers": 2,
            "numattheads": 4,
            "alpha": 0.5,
            "usemask": False,
            "usemixer": True,
            "finetune": True,
            "trainer": {"niters": 1, "itersize": 4, "batch": 2},
        },
        provide={"index": dummy_index},
    )
    extractor = reranker.extractor
    metric = "map"
    benchmark = DummyBenchmark()

    extractor.preprocess(["301"], ["LA010189-0001", "LA010189-0002"], benchmark.topics[benchmark.query_type])
    reranker.build_model()

    train_run = {"301": ["LA010189-0001", "LA010189-0002"]}
    train_dataset = TrainTripletSampler(train_run, benchmark.qrels, extractor)
    dev_dataset = PredSampler(train_run, benchmark.qrels, extractor)
    reranker.trainer.train(
        reranker, train_dataset, Path(tmpdir) / "train", dev_dataset, Path(tmpdir) / "dev", benchmark.qrels, metric
    )

    assert os.path.exists(Path(tmpdir) / "train" / "dev.best")


def test_tk_get_mask(tmpdir, dummy_index, monkeypatch):
    def fake_magnitude_embedding(*args, **kwargs):
        return Magnitude(None)

    monkeypatch.setattr(EmbedText, "_get_pretrained_emb", fake_magnitude_embedding)

    reranker = TK(
        {
            "gradkernels": True,
            "scoretanh": False,
            "singlefc": True,
            "projdim": 16,
            "ffdim": 100,
            "numlayers": 1,
            "numattheads": 2,
            "alpha": 0.5,
            "usemask": True,
            "usemixer": True,
            "finetune": True,
            "trainer": {"niters": 1, "itersize": 4, "batch": 2},
        },
        provide={"index": dummy_index},
    )
    extractor = reranker.extractor
    benchmark = DummyBenchmark()

    extractor.preprocess(["301"], ["LA010189-0001", "LA010189-0002"], benchmark.topics[benchmark.query_type])
    reranker.build_model()

    # 3 batches, each of seq len 4, and embedding dim 8
    embedding = torch.ones(3, 4, 8)
    # Set the 2nd and last token in first batch as pad
    embedding[0, 1] = torch.zeros(8)
    embedding[0, 3] = torch.zeros(8)

    # set the first and third token in second batch as pad
    embedding[1, 0] = torch.zeros(8)
    embedding[1, 2] = torch.zeros(8)

    mask = reranker.model.get_mask(embedding)

    assert torch.equal(
        mask[0],
        torch.tensor(
            [
                [0, float("-inf"), 0, float("-inf")],
                [float("-inf"), float("-inf"), float("-inf"), float("-inf")],
                [0, float("-inf"), 0, float("-inf")],
                [float("-inf"), float("-inf"), float("-inf"), float("-inf")],
            ],
            dtype=torch.float,
        ),
    )

    assert torch.equal(
        mask[1],
        torch.tensor(
            [
                [float("-inf"), float("-inf"), float("-inf"), float("-inf")],
                [float("-inf"), 0, float("-inf"), 0],
                [float("-inf"), float("-inf"), float("-inf"), float("-inf")],
                [float("-inf"), 0, float("-inf"), 0],
            ],
            dtype=torch.float,
        ),
    )

    assert torch.equal(mask[2], torch.zeros(4, 4, dtype=torch.float))


def test_deeptilebars(dummy_index, tmpdir, tmpdir_as_cache, monkeypatch):
    def fake_magnitude_embedding(*args, **kwargs):
        return Magnitude(None)

    monkeypatch.setattr(DeepTileExtractor, "_get_pretrained_emb", fake_magnitude_embedding)
    reranker = DeepTileBar(
        {
            "name": "DeepTileBar",
            "passagelen": 30,
            "numberfilter": 3,
            "lstmhiddendim": 3,
            "linearhiddendim1": 32,
            "linearhiddendim2": 16,
            "trainer": {"niters": 1, "itersize": 4, "batch": 2},
        },
        provide={"index": dummy_index},
    )
    extractor = reranker.extractor
    metric = "map"
    benchmark = DummyBenchmark()

    extractor.preprocess(["301"], ["LA010189-0001", "LA010189-0002"], benchmark.topics[benchmark.query_type])
    reranker.build_model()

    train_run = {"301": ["LA010189-0001", "LA010189-0002"]}
    train_dataset = TrainTripletSampler(train_run, benchmark.qrels, extractor)
    dev_dataset = PredSampler(train_run, benchmark.qrels, extractor)
    reranker.trainer.train(
        reranker, train_dataset, Path(tmpdir) / "train", dev_dataset, Path(tmpdir) / "dev", benchmark.qrels, metric
    )

    assert os.path.exists(Path(tmpdir) / "train" / "dev.best")


def test_HINT(dummy_index, tmpdir, tmpdir_as_cache, monkeypatch):
    def fake_magnitude_embedding(*args, **kwargs):
        return Magnitude(None)

    monkeypatch.setattr(EmbedText, "_get_pretrained_emb", fake_magnitude_embedding)

    reranker = HINT(
        {"spatialGRU": 2, "LSTMdim": 6, "kmax": 10, "trainer": {"niters": 1, "itersize": 2, "batch": 1}},
        provide={"index": dummy_index},
    )
    extractor = reranker.extractor
    metric = "map"
    benchmark = DummyBenchmark()

    extractor.preprocess(["301"], ["LA010189-0001", "LA010189-0002"], benchmark.topics[benchmark.query_type])
    reranker.build_model()

    train_run = {"301": ["LA010189-0001", "LA010189-0002"]}
    train_dataset = TrainTripletSampler(train_run, benchmark.qrels, extractor)
    dev_dataset = PredSampler(train_run, benchmark.qrels, extractor)
    reranker.trainer.train(
        reranker, train_dataset, Path(tmpdir) / "train", dev_dataset, Path(tmpdir) / "dev", benchmark.qrels, metric
    )

    assert os.path.exists(Path(tmpdir) / "train" / "dev.best")


def test_POSITDRMM(dummy_index, tmpdir, tmpdir_as_cache, monkeypatch):
    def fake_magnitude_embedding(*args, **kwargs):
        return Magnitude(None)

    monkeypatch.setattr(EmbedText, "_get_pretrained_emb", fake_magnitude_embedding)

    reranker = POSITDRMM({"trainer": {"niters": 1, "itersize": 4, "batch": 2}}, provide={"index": dummy_index})
    extractor = reranker.extractor
    metric = "map"
    benchmark = DummyBenchmark()

    extractor.preprocess(["301"], ["LA010189-0001", "LA010189-0002"], benchmark.topics[benchmark.query_type])
    reranker.build_model()
    reranker.searcher_scores = {"301": {"LA010189-0001": 2, "LA010189-0002": 1}}
    train_run = {"301": ["LA010189-0001", "LA010189-0002"]}
    train_dataset = TrainTripletSampler(train_run, benchmark.qrels, extractor)
    dev_dataset = PredSampler(train_run, benchmark.qrels, extractor)
    reranker.trainer.train(
        reranker, train_dataset, Path(tmpdir) / "train", dev_dataset, Path(tmpdir) / "dev", benchmark.qrels, metric
    )

    assert os.path.exists(Path(tmpdir) / "train" / "dev.best")


def test_CDSSM(dummy_index, tmpdir, tmpdir_as_cache, monkeypatch):
    def fake_magnitude_embedding(*args, **kwargs):
        return Magnitude(None)

    monkeypatch.setattr(EmbedText, "_get_pretrained_emb", fake_magnitude_embedding)

    reranker = CDSSM(
        {
            "nkernel": 3,
            "nfilter": 1,
            "nhiddens": 30,
            "windowsize": 3,
            "dropoutrate": 0,
            "trainer": {"niters": 1, "itersize": 2, "batch": 1},
        },
        provide={"index": dummy_index},
    )
    extractor = reranker.extractor
    metric = "map"
    benchmark = DummyBenchmark()

    extractor.preprocess(["301"], ["LA010189-0001", "LA010189-0002"], benchmark.topics[benchmark.query_type])
    reranker.build_model()
    reranker.searcher_scores = {"301": {"LA010189-0001": 2, "LA010189-0002": 1}}
    train_run = {"301": ["LA010189-0001", "LA010189-0002"]}
    train_dataset = TrainTripletSampler(train_run, benchmark.qrels, extractor)
    dev_dataset = PredSampler(train_run, benchmark.qrels, extractor)
    reranker.trainer.train(
        reranker, train_dataset, Path(tmpdir) / "train", dev_dataset, Path(tmpdir) / "dev", benchmark.qrels, metric
    )


# Deliberately commented out. This unit test will pass only if you have tons of RAM
def test_bertmaxp(dummy_index, tmpdir, tmpdir_as_cache, monkeypatch):
    reranker = TFBERTMaxP({"pretrained": "bert-base-uncased", "passagelen": 80, "stride": 20})
    trainer = TensorFlowTrainer(
        {
            "maxdoclen": 800,
            "maxqlen": 4,
            "batch": 1,
            "niters": 1,
            "itersize": 2,
            "gradacc": 1,
            "lr": 0.001,
            "softmaxloss": True,
            "interactive": False,
            "fastforward": True,
            "validatefreq": 1,
            "usecache": False,
            "tpuname": None,
            "tpuzone": None,
            "storage": None,
            "boardname": "default",
            "loss": "approx_ndcg_loss",
        }
    )
    reranker.trainer = trainer
    reranker.extractor = BertPassage({"_name": "bertpassage", "maxqlen": 4, "usecache": False, "maxseqlen": 256, "numpassages": 16, "passagelen": 150, "stride": 100})
    extractor = reranker.extractor
    extractor.index = dummy_index
    tok_cfg = {"_name": "berttokenizer", "pretrained": "bert-base-uncased"}
    tokenizer = BertTokenizer(tok_cfg)
    extractor.tokenizer = tokenizer
    metric = "map"
    benchmark = DummyBenchmark({"fold": "s1", "rundocsonly": True})

    extractor.create(["301"], ["LA010189-0001", "LA010189-0002"], benchmark.topics[benchmark.query_type])
    reranker.build()
    reranker.bm25_scores = {"301": {"LA010189-0001": 2, "LA010189-0002": 1}}
    train_run = {"301": ["LA010189-0001", "LA010189-0002"]}
    train_dataset = TrainTripletSampler(train_run, benchmark.qrels, extractor)
    dev_dataset = PredSampler(train_run, benchmark.qrels, extractor)
    reranker.trainer.train(
        reranker, train_dataset, Path(tmpdir) / "train", dev_dataset, Path(tmpdir) / "dev", benchmark.qrels, metric
    )


def test_bertmaxp_ce(dummy_index, tmpdir, tmpdir_as_cache, monkeypatch):
    reranker = TFBERTMaxP({"pretrained": "bert-base-uncased", "passagelen": 80, "stride": 20})
    trainer = TensorFlowTrainer(
        {
            "_name": "tensorflow",
            "maxdoclen": 800,
            "maxqlen": 4,
            "batch": 1,
            "niters": 1,
            "itersize": 2,
            "gradacc": 1,
            "lr": 0.001,
            "softmaxloss": True,
            "interactive": False,
            "fastforward": True,
            "validatefreq": 1,
            "usecache": False,
            "tpuname": None,
            "tpuzone": None,
            "storage": None,
            "boardname": "default",
            "loss": "binary_crossentrop",
        }
    )
    reranker.trainer = trainer
    reranker.extractor = BertPassage({"_name": "bertpassage", "maxqlen": 4, "usecache": False, "maxseqlen": 256, "numpassages": 16, "passagelen": 150, "stride": 100})
    extractor = reranker.extractor
    extractor.index = dummy_index
    tok_cfg = {"_name": "berttokenizer", "pretrained": "bert-base-uncased"}
    tokenizer = BertTokenizer(tok_cfg)
    extractor.tokenizer = tokenizer
    metric = "map"
    benchmark = DummyBenchmark({"fold": "s1", "rundocsonly": True})

    extractor.create(["301"], ["LA010189-0001", "LA010189-0002"], benchmark.topics[benchmark.query_type])
    reranker.build()
    reranker.bm25_scores = {"301": {"LA010189-0001": 2, "LA010189-0002": 1}}
    train_run = {"301": ["LA010189-0001", "LA010189-0002"]}
    train_dataset = TrainPairSampler(train_run, benchmark.qrels, extractor)
    dev_dataset = PredSampler(train_run, benchmark.qrels, extractor)
    reranker.trainer.train(
        reranker, train_dataset, Path(tmpdir) / "train", dev_dataset, Path(tmpdir) / "dev", benchmark.qrels, metric
    )
