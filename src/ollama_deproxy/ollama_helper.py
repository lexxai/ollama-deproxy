import json
import logging

from starlette.requests import Request

from ollama_deproxy.config import settings
from ollama_deproxy.services import build_session

logger = logging.getLogger(__name__)


class OllamaHelper:
    """
    Provides utility methods for managing and manipulating models in an asynchronous context.

    This class is designed to facilitate interactions with models, including fetching,
    storing, and processing model data. It provides methods to replace numeric model
    identifiers with their respective names, retrieve models by ID or name, and execute
    API requests. Its primary use case is for systems requiring dynamic model management
    based on external data sources.
    """

    def __init__(self, session=None):
        self.models: list[dict] | None = None
        self.session = session

    def set_session(self, session):
        self.session = session

    async def get_request(self, path, method: str = "GET", body_bytes: bytes = None, query_params=None) -> bytes:
        """
        Asynchronous function to execute an HTTP request to the provided path using the specified method.

        This function interacts with a remote server and returns the HTTP response content for the
        requested resource. It uses an HTTP session to facilitate communication. If the session is
        not initialized, it will log an error and return an empty byte string. Any HTTP status codes
        in the 400-599 range will also log an error with the appropriate details.

        Parameters:
        path: str
            The endpoint path relative to the remote server's base URL.
        method: str, optional
            The HTTP method to be used for the request (default is "GET").
        body_bytes: bytes, optional
            The request payload in bytes. Defaults to None.
        query_params: dict or None, optional
            Optional dictionary containing query parameters for the request.

        Returns:
        bytes
            The response content from the HTTP request.
        """
        if self.session is None:
            logger.error("Session not initialized")
            return b""
        target_url = f"{str(settings.remote_url).rstrip('/')}/{path.lstrip('/')}"
        proxy_headers = {}
        response = await self.session.request(
            method=method,
            url=target_url,
            headers=proxy_headers,
            params=query_params,
            follow_redirects=False,
        )
        if response.status_code >= 400:
            logger.error(
                f"Error [{response.status_code}] on '{target_url}' with data: {body_bytes.decode()} : {response.text}"
            )
        return response.content

    async def get_models(self, request: Request = None):
        """
        Fetches and processes a list of models asynchronously.

        This method retrieves model data from an API endpoint using an asynchronous
        GET request. The returned data is processed to extract and sort models by their
        modification timestamp in descending order. If the models are successfully
        retrieved and processed, they are stored for future use.

        Parameters:
            request (Request, optional): An optional request object for the function. Defaults to None.
        """
        if self.models is None:
            path = "api/tags"
            method = "GET"
            body_bytes = await self.get_request(path, method=method)
            if body_bytes:
                try:
                    data = json.loads(body_bytes.decode())
                except (json.JSONDecodeError, UnicodeDecodeError):
                    data = {}
            else:
                data = {}
            if data:
                self.models = data.get("models")
                self.models = sorted(self.models, key=lambda x: x.get("modified_at"), reverse=True)
                for i, m in enumerate(self.models):
                    name = m.get("name")
                    logger.debug(f"{i}:{name}")
            logger.debug(f"Models: {self.models}")

    async def get_model_name(self, model_id: int):
        """
        Retrieve the name of a model based on its ID.

        This asynchronous method attempts to obtain the name of a model by its ID. If
        the list of models is uninitialized, it will trigger the process to fetch them.
        The method ensures appropriate validation, including verifying the existence of
        the model ID and that the model data is in the correct dictionary format. If
        any validation fails, the function returns None.

        Parameters:
            model_id (int): The ID of the model whose name is to be retrieved.

        Returns:
            Optional[str]: The name of the model retrieved by the given ID, or None if
            the model does not exist or validation fails.
        """
        if self.models is None:
            await self.get_models()
        if not self.models:
            return None
        if model_id > len(self.models):
            logger.debug(f"Model ID '{model_id}' is not exist")
            return None
        model = self.models[model_id]
        if not isinstance(model, dict):
            logger.debug(f"Model ID '{model_id}' is not correct")
            return None
        return model.get("name")

    async def get_model_id(self, model_name: str):
        """
        Retrieves the model ID for the given model name.

        This asynchronous method searches the models list for a model with a name
        that matches the specified model name. If found, it returns the corresponding
        model's ID. If not found or if the models list is empty or uninitialized, it
        returns None.

        Args:
            model_name (str): The name of the model to find the ID for.

        Returns:
            int | None: The ID of the matching model, or None if no match is found
            or the models list is uninitialized or empty.

        Raises:
            None
        """
        if self.models is None:
            await self.get_models()
        if not self.models:
            return None
        for model_id, model in enumerate(self.models):
            if model.get("name") == model_name:
                return model_id
        return None

    async def replace_numbered_model(self, data: bytes) -> bytes:
        """
        Replaces a numeric model identifier in the input JSON data with its corresponding
        model name.

        This method decodes the input byte data as JSON, checks if the "model" field
        contains a numeric identifier, and replaces it with the result of the
        `get_model_name` method, which maps numeric identifiers to model names. If the
        input is not valid JSON or the "model" field is missing or non-numeric, the
        original data is returned unchanged.

        Parameters:
            data (bytes): The input data in byte format, expected to be a JSON-encoded
            string.

        Returns:
            bytes: The modified data with a numeric model identifier replaced by its
            corresponding name, or the original data if no replacement is performed.

        Raises:
            json.JSONDecodeError: If decoding JSON from the input data fails during
            the modification process.
        """
        if not data:
            return data
        try:
            data_dict = json.loads(data.decode())
        except json.JSONDecodeError:
            logger.debug("Error of decoding JSON")
            return data
        model_name: str = data_dict.get("model", "")
        if model_name and model_name.isdigit():
            model_name_str = await self.get_model_name(int(model_name))
            logger.debug(f"replacement model_name: {model_name_str} for {model_name}")
            data_dict["model"] = model_name_str
            try:
                data = json.dumps(data_dict, ensure_ascii=False).encode()
                # logger.debug(data.decode())
                return data
            except json.JSONDecodeError:
                ...
        return data


if __name__ == "__main__":
    import asyncio
    from ollama_deproxy.config_logging import setup_logging

    setup_logging()

    ollama_helper = OllamaHelper()

    async def test():
        session = build_session()
        ollama_helper.set_session(session)
        # await ollama_helper.get_models()
        model_name = await ollama_helper.get_model_name(12)
        logger.info("Model name: %s", model_name)
        model_id = await ollama_helper.get_model_id("llama3.1:8b")
        logger.info("Model id: %s", model_id)

    asyncio.run(test())
