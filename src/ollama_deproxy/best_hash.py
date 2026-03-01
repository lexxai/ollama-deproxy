import hashlib
import logging
import os
import threading
import timeit

logger = logging.getLogger(__name__)


class BestHash:
    _HASH_CANDIDATES: tuple[str, ...] = ("blake2s", "blake2b", "sha256")
    _SELECTED_HASH_NAME: str | None = None
    _HASH_SELECT_LOCK = threading.Lock()

    @classmethod
    def _hash_available(cls, name: str) -> bool:
        try:
            hashlib.new(name)
            return True
        except ValueError:
            return False

    @classmethod
    def measure_hash_speed(
        cls,
        *,
        data_size_bytes: int = 1024 * 1024,
        number_iterations: int = 256,
        repeat: int = 5,
        warmup_rounds: int = 8,
    ) -> dict[str, float]:
        """
        Benchmark candidate hash algorithms on this platform using timeit.

        Returns: {algorithm_name: throughput_mib_per_sec}
        """
        data = os.urandom(data_size_bytes)
        results: dict[str, float] = {}

        for name in cls._HASH_CANDIDATES:
            if not cls._hash_available(name):
                continue

            logger.debug(f"Measuring {name} hash speed...")

            def one() -> None:
                h = hashlib.new(name)
                h.update(data)
                h.digest()

            for _ in range(warmup_rounds):
                one()

            timings = timeit.repeat(one, number=number_iterations, repeat=repeat)
            best_seconds = min(timings)

            total_bytes = data_size_bytes * number_iterations
            mib_per_sec = (total_bytes / (1024 * 1024)) / best_seconds if best_seconds > 0 else 0.0
            results[name] = mib_per_sec
            logger.debug(f"Measured {name} hash speed:{mib_per_sec:.2f} MiB/s")

        return results

    @classmethod
    def select_best_hash(cls, algorithm: str = "auto") -> str:
        """Select (and cache) the fastest available hash algorithm for this platform."""
        if algorithm != "auto":
            cls._SELECTED_HASH_NAME = algorithm
            return algorithm

        if cls._SELECTED_HASH_NAME is not None:
            return cls._SELECTED_HASH_NAME

        if cls._SELECTED_HASH_NAME is not None:
            return cls._SELECTED_HASH_NAME
        logger.info("Cache key hash algorithm auto-selection...")

        with cls._HASH_SELECT_LOCK:
            speeds = cls.measure_hash_speed()
            if not speeds:
                cls._SELECTED_HASH_NAME = "sha256"  # conservative fallback
                return cls._SELECTED_HASH_NAME

            cls._SELECTED_HASH_NAME = max(speeds, key=speeds.get)
            return cls._SELECTED_HASH_NAME
