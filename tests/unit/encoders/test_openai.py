import pytest
from openai import OpenAIError
from openai.types import CreateEmbeddingResponse, Embedding
from openai.types.create_embedding_response import Usage

from semantic_router.encoders import OpenAIEncoder


@pytest.fixture
def openai_encoder(mocker):
    mocker.patch("openai.Client")
    return OpenAIEncoder(openai_api_key="test_api_key")


class TestOpenAIEncoder:
    def test_openai_encoder_init_success(self, mocker):
        mocker.patch("os.getenv", return_value="fake-api-key")
        encoder = OpenAIEncoder()
        assert encoder.client is not None

    def test_openai_encoder_init_no_api_key(self, mocker):
        mocker.patch("os.getenv", return_value=None)
        with pytest.raises(ValueError) as e:
            OpenAIEncoder()
        assert "OpenAI API key cannot be 'None'." in str(e.value)

    def test_openai_encoder_call_uninitialized_client(self, openai_encoder):
        # Set the client to None to simulate an uninitialized client
        openai_encoder.client = None
        with pytest.raises(ValueError) as e:
            openai_encoder(["test document"])
        assert "OpenAI client is not initialized." in str(e.value)

    def test_openai_encoder_init_exception(self, mocker):
        mocker.patch("os.getenv", return_value="fake-api-key")
        mocker.patch("openai.Client", side_effect=Exception("Initialization error"))
        with pytest.raises(ValueError) as e:
            OpenAIEncoder()
        assert (
            "OpenAI API client failed to initialize. Error: Initialization error"
            in str(e.value)
        )

    def test_openai_encoder_call_success(self, openai_encoder, mocker):
        mock_embeddings = mocker.Mock()
        mock_embeddings.data = [
            Embedding(embedding=[0.1, 0.2], index=0, object="embedding")
        ]

        mocker.patch("os.getenv", return_value="fake-api-key")
        mocker.patch("time.sleep", return_value=None)  # To speed up the test

        mock_embedding = Embedding(index=0, object="embedding", embedding=[0.1, 0.2])
        # Mock the CreateEmbeddingResponse object
        mock_response = CreateEmbeddingResponse(
            model="text-embedding-ada-002",
            object="list",
            usage=Usage(prompt_tokens=0, total_tokens=20),
            data=[mock_embedding],
        )

        responses = [OpenAIError("OpenAI error"), mock_response]
        mocker.patch.object(
            openai_encoder.client.embeddings, "create", side_effect=responses
        )
        embeddings = openai_encoder(["test document"])
        assert embeddings == [[0.1, 0.2]]

    def test_openai_encoder_call_with_retries(self, openai_encoder, mocker):
        mocker.patch("os.getenv", return_value="fake-api-key")
        mocker.patch("time.sleep", return_value=None)  # To speed up the test
        mocker.patch.object(
            openai_encoder.client.embeddings,
            "create",
            side_effect=OpenAIError("Test error"),
        )
        with pytest.raises(ValueError) as e:
            openai_encoder(["test document"])
        assert "No embeddings returned. Error" in str(e.value)

    def test_openai_encoder_call_failure_non_openai_error(self, openai_encoder, mocker):
        mocker.patch("os.getenv", return_value="fake-api-key")
        mocker.patch("time.sleep", return_value=None)  # To speed up the test
        mocker.patch.object(
            openai_encoder.client.embeddings,
            "create",
            side_effect=Exception("Non-OpenAIError"),
        )
        with pytest.raises(ValueError) as e:
            openai_encoder(["test document"])

        assert "OpenAI API call failed. Error: Non-OpenAIError" in str(e.value)

    def test_openai_encoder_call_successful_retry(self, openai_encoder, mocker):
        mock_embeddings = mocker.Mock()
        mock_embeddings.data = [
            Embedding(embedding=[0.1, 0.2], index=0, object="embedding")
        ]

        mocker.patch("os.getenv", return_value="fake-api-key")
        mocker.patch("time.sleep", return_value=None)  # To speed up the test

        mock_embedding = Embedding(index=0, object="embedding", embedding=[0.1, 0.2])
        # Mock the CreateEmbeddingResponse object
        mock_response = CreateEmbeddingResponse(
            model="text-embedding-ada-002",
            object="list",
            usage=Usage(prompt_tokens=0, total_tokens=20),
            data=[mock_embedding],
        )

        responses = [OpenAIError("OpenAI error"), mock_response]
        mocker.patch.object(
            openai_encoder.client.embeddings, "create", side_effect=responses
        )
        embeddings = openai_encoder(["test document"])
        assert embeddings == [[0.1, 0.2]]
