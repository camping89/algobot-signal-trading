import importlib
import logging
from pathlib import Path
from typing import List
from fastapi import APIRouter

logger = logging.getLogger(__name__)


def discover_feature_routers() -> List[APIRouter]:
    routers = []

    # Discover from trading app features
    trading_features_path = Path(__file__).parent.parent / "app" / "trading" / "features"
    routers.extend(_discover_routers_in_path(trading_features_path, "app.trading.features"))

    # Discover from discord app features
    discord_features_path = Path(__file__).parent.parent / "app" / "discord" / "features"
    routers.extend(_discover_routers_in_path(discord_features_path, "app.discord.features"))

    logger.info(f"Total feature routers discovered: {len(routers)}")
    return routers

def _discover_routers_in_path(features_path: Path, module_prefix: str) -> List[APIRouter]:
    routers = []

    if not features_path.exists():
        logger.debug(f"Features directory not found: {features_path}")
        return routers

    def _discover_recursive(path: Path, prefix: str):
        for item in path.iterdir():
            if not item.is_dir() or item.name.startswith("__"):
                continue

            try:
                module_name = f"{prefix}.{item.name}"
                module = importlib.import_module(module_name)

                if hasattr(module, 'routers'):
                    feature_routers = module.routers
                    routers.extend(feature_routers)
                    logger.info(f"Discovered {len(feature_routers)} routers from {module_name}")
                else:
                    # Check for nested features
                    _discover_recursive(item, module_name)

            except ImportError as e:
                logger.debug(f"No module found for {module_name}: {e}")
                # Try to discover nested features anyway
                _discover_recursive(item, f"{prefix}.{item.name}")
            except Exception as e:
                logger.error(f"Error loading routers from {module_name}: {e}")

    _discover_recursive(features_path, module_prefix)
    return routers


def discover_system_routers() -> List[APIRouter]:
    routers = []
    try:
        from src.api.system import routers as system_routers
        routers.extend(system_routers)
        logger.info(f"Discovered {len(system_routers)} system routers")
    except ImportError:
        logger.debug("No system routers found")
    except Exception as e:
        logger.error(f"Error loading system routers: {e}")

    return routers


def discover_all_routers() -> List[APIRouter]:
    all_routers = []

    feature_routers = discover_feature_routers()
    system_routers = discover_system_routers()

    all_routers.extend(feature_routers)
    all_routers.extend(system_routers)

    logger.info(f"Total routers discovered: {len(all_routers)} ({len(feature_routers)} features + {len(system_routers)} system)")
    return all_routers