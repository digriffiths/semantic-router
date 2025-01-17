import pytest
from semantic_router.encoders import TfidfEncoder
from semantic_router.schemas.route import Route


@pytest.fixture
def tfidf_encoder():
    return TfidfEncoder()


class TestTfidfEncoder:
    def test_initialization(self, tfidf_encoder):
        assert tfidf_encoder.word_index is None
        assert tfidf_encoder.idf is None

    def test_fit(self, tfidf_encoder):
        routes = [
            Route(
                name="test_route",
                utterances=["some docs", "and more docs", "and even more docs"],
            )
        ]
        tfidf_encoder.fit(routes)
        assert tfidf_encoder.word_index is not None
        assert tfidf_encoder.idf is not None

    def test_call_method(self, tfidf_encoder):
        routes = [
            Route(
                name="test_route",
                utterances=["some docs", "and more docs", "and even more docs"],
            )
        ]
        tfidf_encoder.fit(routes)
        result = tfidf_encoder(["test"])
        assert isinstance(result, list), "Result should be a list"
        assert all(
            isinstance(sublist, list) for sublist in result
        ), "Each item in result should be a list"

    def test_call_method_no_docs(self, tfidf_encoder):
        with pytest.raises(ValueError):
            tfidf_encoder([])

    def test_call_method_no_word(self, tfidf_encoder):
        routes = [
            Route(
                name="test_route",
                utterances=["some docs", "and more docs", "and even more docs"],
            )
        ]
        tfidf_encoder.fit(routes)
        result = tfidf_encoder(["doc with fake word gta5jabcxyz"])
        assert isinstance(result, list), "Result should be a list"
        assert all(
            isinstance(sublist, list) for sublist in result
        ), "Each item in result should be a list"

    def test_call_method_with_uninitialized_model(self, tfidf_encoder):
        with pytest.raises(ValueError):
            tfidf_encoder(["test"])
