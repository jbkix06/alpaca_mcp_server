"""Global Configuration System for MCP Trading Server

Fast, aggressive trading configuration - no conservative thresholds.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class TradingConfig:
    """Trading configuration parameters"""
    trades_per_minute_threshold: int = 500
    min_percent_change_threshold: float = 10.0
    default_position_size_usd: int = 50000
    max_concurrent_positions: int = 5
    never_sell_for_loss: bool = True
    order_timeout_seconds: int = 10
    default_order_type: str = "limit"
    default_time_in_force: str = "day"

@dataclass
class TechnicalAnalysisConfig:
    """Technical analysis parameters"""
    hanning_window_samples: int = 11
    peak_trough_min_distance: int = 3
    peak_trough_lookahead: int = 1

@dataclass
class MarketHoursConfig:
    """Market hours configuration"""
    trading_hours_start: str = "04:00"
    trading_hours_end: str = "20:00"
    trading_timezone: str = "America/New_York"

@dataclass
class ScannerConfig:
    """Scanner configuration"""
    active_scan_interval_seconds: int = 60
    max_watchlist_size: int = 50
    scanner_sort_method: str = "trades"

@dataclass
class SystemConfig:
    """System configuration"""
    hibernation_enabled: bool = True
    monitoring_check_interval_seconds: int = 60
    streaming_buffer_size_per_symbol: int = 5000

@dataclass
class GlobalConfig:
    """Complete global configuration"""
    trading: TradingConfig
    technical_analysis: TechnicalAnalysisConfig
    market_hours: MarketHoursConfig
    scanner: ScannerConfig
    system: SystemConfig
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'GlobalConfig':
        """Load configuration from file"""
        if config_path is None:
            # Default to config/global_config.json in project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "global_config.json"
        
        config_path = Path(config_path)
        
        if not config_path.exists():
            logger.warning(f"Config file not found at {config_path}, using defaults")
            return cls.default()
        
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            
            return cls(
                trading=TradingConfig(**data.get('trading', {})),
                technical_analysis=TechnicalAnalysisConfig(**data.get('technical_analysis', {})),
                market_hours=MarketHoursConfig(**data.get('market_hours', {})),
                scanner=ScannerConfig(**data.get('scanner', {})),
                system=SystemConfig(**data.get('system', {}))
            )
            
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            logger.warning("Using default configuration")
            return cls.default()
    
    @classmethod
    def default(cls) -> 'GlobalConfig':
        """Return default configuration"""
        return cls(
            trading=TradingConfig(),
            technical_analysis=TechnicalAnalysisConfig(),
            market_hours=MarketHoursConfig(),
            scanner=ScannerConfig(),
            system=SystemConfig()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'trading': self.trading.__dict__,
            'technical_analysis': self.technical_analysis.__dict__,
            'market_hours': self.market_hours.__dict__,
            'scanner': self.scanner.__dict__,
            'system': self.system.__dict__
        }
    
    def save(self, config_path: Optional[str] = None) -> None:
        """Save configuration to file"""
        if config_path is None:
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "global_config.json"
        
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = self.to_dict()
        data['metadata'] = {
            'version': '1.0.0',
            'last_updated': '2025-06-18T23:25:00Z',
            'description': 'Global configuration for fast, aggressive MCP trading system'
        }
        
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Configuration saved to {config_path}")

# Global instance
_global_config: Optional[GlobalConfig] = None

def get_global_config() -> GlobalConfig:
    """Get the global configuration instance"""
    global _global_config
    if _global_config is None:
        _global_config = GlobalConfig.load()
        logger.info("Global configuration loaded successfully")
    return _global_config

def reload_global_config() -> GlobalConfig:
    """Reload configuration from file"""
    global _global_config
    _global_config = GlobalConfig.load()
    logger.info("Global configuration reloaded")
    return _global_config

# Convenience functions for quick access
def get_trading_config() -> TradingConfig:
    """Get trading configuration"""
    return get_global_config().trading

def get_technical_config() -> TechnicalAnalysisConfig:
    """Get technical analysis configuration"""
    return get_global_config().technical_analysis

def get_market_hours_config() -> MarketHoursConfig:
    """Get market hours configuration"""
    return get_global_config().market_hours

def get_scanner_config() -> ScannerConfig:
    """Get scanner configuration"""
    return get_global_config().scanner

def get_system_config() -> SystemConfig:
    """Get system configuration"""
    return get_global_config().system