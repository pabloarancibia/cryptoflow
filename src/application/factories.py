# src/application/factories.py
from typing import Dict, Any, Type
from src.domain.strategies import TradingStrategy


class StrategyFactory:
    """
    Factory Pattern with Registry.
    Open for extension (register new strategies), Closed for modification (no more if/else).
    """

    # 1. The Internal Registry (Maps string "SMA" -> Class MovingAverageStrategy)
    _registry: Dict[str, Type[TradingStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_class: Type[TradingStrategy]):
        """
        Allows external code to register a new strategy dynamically.
        """
        cls._registry[name.upper()] = strategy_class

    @staticmethod
    def create(name: str, parameters: Dict[str, Any] = None) -> TradingStrategy:
        if parameters is None:
            parameters = {}

        strategy_name = name.upper()

        # 2. Lookup the class
        strategy_cls = StrategyFactory._registry.get(strategy_name)

        if not strategy_cls:
            valid_keys = list(StrategyFactory._registry.keys())
            raise ValueError(f"Unknown strategy: '{name}'. Available: {valid_keys}")

        # 3. Dynamic Instantiation
        # We pass the dictionary items as arguments to the class constructor.
        # e.g., if parameters={'window': 5}, this calls strategy_cls(window=5)
        try:
            return strategy_cls(**parameters)
        except TypeError as e:
            # Catch cases where user sends params that the specific strategy doesn't accept
            raise ValueError(f"Invalid parameters for {strategy_name}: {e}")