"""Signal Detector - Automated trading signal detection

Uses existing MCP tools to detect fresh trading signals for the watchlist,
providing the intelligence layer for the hybrid trading system.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import time

# Import existing MCP tools for signal detection
from ..tools.peak_trough_analysis_tool import analyze_peaks_and_troughs as get_stock_peak_trough_analysis
from ..tools.market_data_tools import get_stock_snapshots
from ..tools.streaming_tools import get_stock_stream_data


class SignalDetector:
    """
    Automated signal detection using existing MCP tools.
    
    This class provides intelligent signal detection by:
    1. Using peak/trough analysis to identify fresh signals
    2. Validating signals with streaming data
    3. Confirming liquidity with snapshot data
    4. Ranking signals by confidence score
    """
    
    def __init__(self):
        self.logger = logging.getLogger('signal_detector')
        
        # Detection state
        self.last_scan: Optional[datetime] = None
        self.scan_count = 0
        self.signals_detected = 0
        self.error_count = 0
        
        # Signal parameters
        self.fresh_signal_bars = 5  # Signal must be <5 bars old
        self.min_confidence = 0.0
        self.min_volume_threshold = 100000
        
        # Cache for recent scans to avoid duplicate signals
        self.recent_signals: Dict[str, Dict] = {}
        self.signal_cache_duration = 300  # 5 minutes
        
        self.logger.info("SignalDetector initialized")
    
    async def scan_for_signals(self, symbols: List[str], confidence_threshold: float = 0.75) -> List[Dict]:
        """
        Scan watchlist symbols for trading signals.
        
        Args:
            symbols: List of symbols to scan
            confidence_threshold: Minimum confidence for returned signals
            
        Returns:
            List of detected signals above confidence threshold
        """
        self.last_scan = datetime.now(timezone.utc)
        self.scan_count += 1
        
        all_signals = []
        
        try:
            # Clean expired signals from cache
            self._clean_signal_cache()
            
            # Process symbols in batches for efficiency
            batch_size = 5
            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]
                
                # Run peak/trough analysis for batch
                batch_signals = await self._analyze_symbol_batch(batch)
                all_signals.extend(batch_signals)
                
                # Small delay to avoid overwhelming the API
                if i + batch_size < len(symbols):
                    await asyncio.sleep(0.5)
            
            # Filter by confidence threshold
            high_confidence_signals = [
                signal for signal in all_signals 
                if signal.get('confidence', 0) >= confidence_threshold
            ]
            
            # Update detection stats
            self.signals_detected += len(high_confidence_signals)
            
            if high_confidence_signals:
                self.logger.info(
                    f"🎯 Detected {len(high_confidence_signals)} high-confidence signals "
                    f"from {len(symbols)} symbols"
                )
            
            return high_confidence_signals
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Error in signal scanning: {e}")
            return []
    
    async def _analyze_symbol_batch(self, symbols: List[str]) -> List[Dict]:
        """Analyze a batch of symbols for signals"""
        signals = []
        
        for symbol in symbols:
            try:
                # Skip if we recently detected a signal for this symbol
                if self._has_recent_signal(symbol):
                    continue
                
                # Get peak/trough analysis using existing MCP tool
                analysis_result = await get_stock_peak_trough_analysis(
                    symbols=symbol,
                    timeframe="1Min",
                    days=1,
                    window_len=21,
                    lookahead=1
                )
                
                # Parse analysis for signals
                symbol_signals = await self._parse_peak_trough_analysis(symbol, analysis_result)
                signals.extend(symbol_signals)
                
            except Exception as e:
                self.logger.warning(f"Error analyzing {symbol}: {e}")
                continue
        
        return signals
    
    async def _parse_peak_trough_analysis(self, symbol: str, analysis_result: str) -> List[Dict]:
        """Parse peak/trough analysis result for trading signals"""
        signals = []
        
        try:
            # Look for the latest peak/trough information in the analysis
            lines = analysis_result.split('\n')
            
            # Find the symbol section
            symbol_section = False
            latest_peak_info = None
            latest_trough_info = None
            
            for line in lines:
                # Check if we're in the right symbol section
                if line.strip().startswith(f"## {symbol}"):
                    symbol_section = True
                    continue
                elif line.strip().startswith("## ") and not line.strip().startswith(f"## {symbol}"):
                    symbol_section = False
                    continue
                
                if not symbol_section:
                    continue
                
                # Look for latest peak information
                if line.strip().startswith("Latest peak:"):
                    latest_peak_info = line.strip()
                
                # Look for latest trough information  
                elif line.strip().startswith("Latest trough:"):
                    latest_trough_info = line.strip()
                
                # Look for trading signal summary
                elif "Last signal:" in line and ("PEAK" in line or "TROUGH" in line):
                    # Extract signal from trading summary
                    signal = await self._extract_signal_from_summary(symbol, line, analysis_result)
                    if signal:
                        signals.append(signal)
            
            # Also check latest peak/trough lines for fresh signals
            if latest_peak_info:
                signal = await self._extract_latest_signal(symbol, latest_peak_info, 'peak', analysis_result)
                if signal:
                    signals.append(signal)
                    
            if latest_trough_info:
                signal = await self._extract_latest_signal(symbol, latest_trough_info, 'trough', analysis_result)
                if signal:
                    signals.append(signal)
            
            # Cache any detected signals
            if signals:
                for signal in signals:
                    self._cache_signal(symbol, signal)
            
        except Exception as e:
            self.logger.error(f"Error parsing analysis for {symbol}: {e}")
        
        return signals
    
    async def _extract_signal_from_summary(self, symbol: str, line: str, full_analysis: str) -> Optional[Dict]:
        """Extract signal from trading signal summary line"""
        try:
            # Parse line like: "📊 Last signal: PEAK at sample 381 ($1.5700)"
            import re
            
            # Extract signal type
            signal_type = None
            if "PEAK" in line.upper():
                signal_type = "fresh_peak"
            elif "TROUGH" in line.upper():
                signal_type = "fresh_trough"
            else:
                return None
            
            # Extract price
            price_match = re.search(r'\$(\d+\.?\d*)', line)
            price = float(price_match.group(1)) if price_match else None
            
            # Extract sample/bars info - look for pattern like "sample 381" or "(7 bars ago)"
            bars_ago = None
            sample_match = re.search(r'sample\s+(\d+)', line)
            bars_match = re.search(r'\((\d+)\s+bars?\s+ago\)', line)
            
            if bars_match:
                bars_ago = int(bars_match.group(1))
            elif sample_match:
                # Estimate bars ago from context or set to reasonable default
                bars_ago = 1  # Assume recent if no bars ago specified
            
            if bars_ago is None or bars_ago > self.fresh_signal_bars * 2:  # Allow some flexibility
                return None
            
            # Calculate confidence (no threshold since we removed confidence requirements)
            confidence = self._calculate_signal_confidence(bars_ago, signal_type, full_analysis)
            
            # Validate signal
            is_valid = await self._validate_signal(symbol, price, signal_type.replace('fresh_', ''))
            if not is_valid:
                return None
            
            action = "buy_candidate" if signal_type == "fresh_trough" else "sell_candidate"
            
            signal = {
                'symbol': symbol,
                'signal_type': signal_type,
                'price': price,
                'bars_ago': bars_ago,
                'confidence': confidence,
                'action': action,
                'detected_at': datetime.now(timezone.utc).isoformat(),
                'source': 'peak_trough_analysis'
            }
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error extracting signal from summary for {symbol}: {e}")
            return None
    
    async def _extract_latest_signal(self, symbol: str, line: str, signal_type: str, full_analysis: str) -> Optional[Dict]:
        """Extract signal from latest peak/trough line"""
        try:
            # Parse line like: "Latest peak: Sample 381, $1.5700 (7 bars ago)"
            import re
            
            # Extract price
            price_match = re.search(r'\$(\d+\.?\d*)', line)
            price = float(price_match.group(1)) if price_match else None
            
            # Extract bars ago
            bars_match = re.search(r'\((\d+)\s+bars?\s+ago\)', line)
            bars_ago = int(bars_match.group(1)) if bars_match else None
            
            if bars_ago is None or bars_ago > self.fresh_signal_bars * 2:  # Allow some flexibility
                return None
            
            # Calculate confidence
            confidence = self._calculate_signal_confidence(bars_ago, signal_type, full_analysis)
            
            # Validate signal
            is_valid = await self._validate_signal(symbol, price, signal_type)
            if not is_valid:
                return None
            
            signal_type_name = f"fresh_{signal_type}"
            action = "buy_candidate" if signal_type == "trough" else "sell_candidate"
            
            signal = {
                'symbol': symbol,
                'signal_type': signal_type_name,
                'price': price,
                'bars_ago': bars_ago,
                'confidence': confidence,
                'action': action,
                'detected_at': datetime.now(timezone.utc).isoformat(),
                'source': 'peak_trough_analysis'
            }
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error extracting latest signal for {symbol}: {e}")
            return None
    
    async def _extract_trough_signal(self, symbol: str, line: str, full_analysis: str) -> Optional[Dict]:
        """Extract trough signal from analysis line"""
        try:
            # Parse the line to extract trough information
            # Example: "Fresh trough detected at $150.25 (2 bars ago)"
            
            # Look for price in the line
            price = None
            bars_ago = None
            
            # Extract price (look for $ followed by number)
            import re
            price_match = re.search(r'\$?(\d+\.?\d*)', line)
            if price_match:
                price = float(price_match.group(1))
            
            # Extract bars ago
            bars_match = re.search(r'(\d+)\s+bars?\s+ago', line)
            if bars_match:
                bars_ago = int(bars_match.group(1))
            
            # Only consider fresh signals
            if bars_ago is None or bars_ago > self.fresh_signal_bars:
                return None
            
            # Calculate confidence based on freshness and analysis quality
            confidence = self._calculate_signal_confidence(bars_ago, 'trough', full_analysis)
            
            if confidence < self.min_confidence:
                return None
            
            # Validate with additional data
            is_valid = await self._validate_signal(symbol, price, 'trough')
            if not is_valid:
                return None
            
            signal = {
                'symbol': symbol,
                'signal_type': 'fresh_trough',
                'price': price,
                'bars_ago': bars_ago,
                'confidence': confidence,
                'action': 'buy_candidate',
                'detected_at': datetime.now(timezone.utc).isoformat(),
                'source': 'peak_trough_analysis'
            }
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error extracting trough signal for {symbol}: {e}")
            return None
    
    async def _extract_peak_signal(self, symbol: str, line: str, full_analysis: str) -> Optional[Dict]:
        """Extract peak signal from analysis line"""
        try:
            # Similar to trough extraction but for peaks (sell signals)
            import re
            
            price = None
            bars_ago = None
            
            price_match = re.search(r'\$?(\d+\.?\d*)', line)
            if price_match:
                price = float(price_match.group(1))
            
            bars_match = re.search(r'(\d+)\s+bars?\s+ago', line)
            if bars_match:
                bars_ago = int(bars_match.group(1))
            
            if bars_ago is None or bars_ago > self.fresh_signal_bars:
                return None
            
            confidence = self._calculate_signal_confidence(bars_ago, 'peak', full_analysis)
            
            if confidence < self.min_confidence:
                return None
            
            is_valid = await self._validate_signal(symbol, price, 'peak')
            if not is_valid:
                return None
            
            signal = {
                'symbol': symbol,
                'signal_type': 'fresh_peak',
                'price': price,
                'bars_ago': bars_ago,
                'confidence': confidence,
                'action': 'sell_candidate',
                'detected_at': datetime.now(timezone.utc).isoformat(),
                'source': 'peak_trough_analysis'
            }
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error extracting peak signal for {symbol}: {e}")
            return None
    
    def _calculate_signal_confidence(self, bars_ago: int, signal_type: str, analysis: str) -> float:
        """Calculate confidence score for a signal"""
        try:
            # Base confidence from freshness (fresher = higher confidence)
            freshness_score = max(0, 1.0 - (bars_ago / self.fresh_signal_bars))
            
            # Bonus for signal quality indicators in analysis
            quality_bonus = 0
            
            # Look for quality indicators in the analysis text
            quality_keywords = {
                'high volume': 0.1,
                'strong momentum': 0.1,
                'confirmed': 0.15,
                'significant': 0.1,
                'clear pattern': 0.1
            }
            
            analysis_lower = analysis.lower()
            for keyword, bonus in quality_keywords.items():
                if keyword in analysis_lower:
                    quality_bonus += bonus
            
            # Combine scores
            confidence = min(1.0, freshness_score * 0.7 + quality_bonus)
            
            return confidence
            
        except Exception:
            return 0.5  # Default confidence
    
    async def _validate_signal(self, symbol: str, price: Optional[float], signal_type: str) -> bool:
        """Validate signal with additional market data"""
        try:
            # Get current snapshot for volume validation
            snapshot_result = await get_stock_snapshots(symbols=symbol)
            
            if isinstance(snapshot_result, dict) and 'snapshots' in snapshot_result:
                snapshots = snapshot_result['snapshots']
                if symbol in snapshots:
                    snapshot = snapshots[symbol]
                    
                    # Check volume threshold
                    daily_volume = snapshot.get('daily_volume', 0)
                    if daily_volume < self.min_volume_threshold:
                        return False
                    
                    # Check if price is reasonable vs current market
                    current_price = snapshot.get('latest_trade', {}).get('price')
                    if price and current_price:
                        price_diff = abs(price - current_price) / current_price
                        if price_diff > 0.1:  # Price too far from current (>10%)
                            return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Error validating signal for {symbol}: {e}")
            return True  # Default to valid if validation fails
    
    def _has_recent_signal(self, symbol: str) -> bool:
        """Check if we have a recent signal for this symbol"""
        if symbol not in self.recent_signals:
            return False
        
        last_signal_time = self.recent_signals[symbol].get('timestamp', 0)
        return (time.time() - last_signal_time) < self.signal_cache_duration
    
    def _cache_signal(self, symbol: str, signal: Dict):
        """Cache a signal to avoid duplicates"""
        self.recent_signals[symbol] = {
            'signal': signal,
            'timestamp': time.time()
        }
    
    def _clean_signal_cache(self):
        """Remove expired signals from cache"""
        current_time = time.time()
        expired_symbols = [
            symbol for symbol, data in self.recent_signals.items()
            if (current_time - data.get('timestamp', 0)) > self.signal_cache_duration
        ]
        
        for symbol in expired_symbols:
            del self.recent_signals[symbol]
    
    def get_status(self) -> Dict:
        """Get signal detector status"""
        return {
            'active': True,
            'last_scan': self.last_scan.isoformat() if self.last_scan else None,
            'scan_count': self.scan_count,
            'signals_detected': self.signals_detected,
            'error_count': self.error_count,
            'cached_signals': len(self.recent_signals),
            'parameters': {
                'fresh_signal_bars': self.fresh_signal_bars,
                'min_confidence': self.min_confidence,
                'min_volume_threshold': self.min_volume_threshold
            }
        }


# Future enhancement: Multi-timeframe signal detection
class MultiTimeframeSignalDetector:
    """
    Future implementation for multi-timeframe signal analysis.
    
    This will combine signals from multiple timeframes (1min, 5min, 15min)
    to increase signal confidence and reduce false positives.
    """
    
    def __init__(self, base_detector: SignalDetector):
        self.base_detector = base_detector
        self.logger = logging.getLogger('multi_timeframe_detector')
    
    async def analyze_multi_timeframe(self, symbol: str) -> Dict:
        """Analyze signal across multiple timeframes"""
        # Future implementation:
        # 1. Run analysis on 1min, 5min, 15min timeframes
        # 2. Combine signals for higher confidence
        # 3. Weight newer timeframes more heavily
        # 4. Return consensus signal with high confidence
        
        self.logger.info("Multi-timeframe analysis planned for Phase 2")
        return {}