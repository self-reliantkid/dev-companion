"""Metrics collection and analysis for generation performance."""

import time
import json
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class GenerationMetrics:
    """Metrics for a single generation request."""
    action: str
    language: str
    timestamp: str
    duration_seconds: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    quality_score: float
    success: bool
    retry_count: int
    error_message: Optional[str] = None


class MetricsCollector:
    """Collects and analyzes generation metrics."""
    
    def __init__(self, persist_path: Optional[str] = None):
        """Initialize metrics collector.
        
        Args:
            persist_path: Optional path to persist metrics to disk
        """
        self.metrics: List[GenerationMetrics] = []
        self.persist_path = persist_path
        self.session_start = datetime.now()
    
    def record(
        self,
        action: str,
        language: str,
        duration: float,
        input_tokens: int,
        output_tokens: int,
        quality_score: float,
        success: bool = True,
        retry_count: int = 0,
        error_message: Optional[str] = None
    ) -> GenerationMetrics:
        """Record metrics for a generation request.
        
        Args:
            action: Type of generation (docs, tests, review, etc.)
            language: Programming language
            duration: Time taken in seconds
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            quality_score: Quality score (0.0 to 1.0)
            success: Whether generation succeeded
            retry_count: Number of retries attempted
            error_message: Error message if failed
            
        Returns:
            GenerationMetrics object
        """
        metrics = GenerationMetrics(
            action=action,
            language=language,
            timestamp=datetime.now().isoformat(),
            duration_seconds=duration,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            quality_score=quality_score,
            success=success,
            retry_count=retry_count,
            error_message=error_message
        )
        
        self.metrics.append(metrics)
        
        if self.persist_path:
            self._persist_metrics()
        
        return metrics
    
    def get_summary(self) -> Dict:
        """Get summary statistics for all collected metrics.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.metrics:
            return {
                "total_requests": 0,
                "success_rate": 0.0,
                "avg_duration": 0.0,
                "total_tokens": 0,
                "avg_quality_score": 0.0
            }
        
        successful = [m for m in self.metrics if m.success]
        
        return {
            "total_requests": len(self.metrics),
            "successful_requests": len(successful),
            "failed_requests": len(self.metrics) - len(successful),
            "success_rate": len(successful) / len(self.metrics),
            "avg_duration": sum(m.duration_seconds for m in self.metrics) / len(self.metrics),
            "total_tokens": sum(m.total_tokens for m in self.metrics),
            "avg_tokens_per_request": sum(m.total_tokens for m in self.metrics) / len(self.metrics),
            "avg_quality_score": sum(m.quality_score for m in successful) / len(successful) if successful else 0.0,
            "total_retries": sum(m.retry_count for m in self.metrics),
            "by_action": self._get_action_breakdown(),
            "by_language": self._get_language_breakdown(),
            "session_duration": (datetime.now() - self.session_start).total_seconds()
        }
    
    def get_action_stats(self, action: str) -> Dict:
        """Get statistics for a specific action type.
        
        Args:
            action: Action type (docs, tests, review, etc.)
            
        Returns:
            Dictionary with action-specific statistics
        """
        action_metrics = [m for m in self.metrics if m.action == action]
        
        if not action_metrics:
            return {"count": 0}
        
        successful = [m for m in action_metrics if m.success]
        
        return {
            "count": len(action_metrics),
            "success_rate": len(successful) / len(action_metrics),
            "avg_duration": sum(m.duration_seconds for m in action_metrics) / len(action_metrics),
            "avg_tokens": sum(m.total_tokens for m in action_metrics) / len(action_metrics),
            "avg_quality_score": sum(m.quality_score for m in successful) / len(successful) if successful else 0.0,
            "total_retries": sum(m.retry_count for m in action_metrics)
        }
    
    def get_recent_metrics(self, count: int = 10) -> List[GenerationMetrics]:
        """Get the most recent metrics.
        
        Args:
            count: Number of recent metrics to return
            
        Returns:
            List of recent GenerationMetrics
        """
        return self.metrics[-count:] if self.metrics else []
    
    def get_quality_trends(self) -> Dict:
        """Analyze quality score trends over time.
        
        Returns:
            Dictionary with quality trend analysis
        """
        if not self.metrics:
            return {"trend": "no_data"}
        
        successful = [m for m in self.metrics if m.success]
        if len(successful) < 2:
            return {"trend": "insufficient_data"}
        
        # Split into first half and second half
        mid = len(successful) // 2
        first_half_avg = sum(m.quality_score for m in successful[:mid]) / mid
        second_half_avg = sum(m.quality_score for m in successful[mid:]) / (len(successful) - mid)
        
        trend = "improving" if second_half_avg > first_half_avg else "declining" if second_half_avg < first_half_avg else "stable"
        
        return {
            "trend": trend,
            "first_half_avg": first_half_avg,
            "second_half_avg": second_half_avg,
            "change": second_half_avg - first_half_avg,
            "current_avg": sum(m.quality_score for m in successful[-5:]) / min(5, len(successful))
        }
    
    def _get_action_breakdown(self) -> Dict:
        """Get breakdown of metrics by action type."""
        actions = {}
        for metric in self.metrics:
            if metric.action not in actions:
                actions[metric.action] = {
                    "count": 0,
                    "total_tokens": 0,
                    "total_duration": 0.0,
                    "successes": 0
                }
            actions[metric.action]["count"] += 1
            actions[metric.action]["total_tokens"] += metric.total_tokens
            actions[metric.action]["total_duration"] += metric.duration_seconds
            if metric.success:
                actions[metric.action]["successes"] += 1
        
        # Calculate averages
        for action, stats in actions.items():
            stats["avg_tokens"] = stats["total_tokens"] / stats["count"]
            stats["avg_duration"] = stats["total_duration"] / stats["count"]
            stats["success_rate"] = stats["successes"] / stats["count"]
        
        return actions
    
    def _get_language_breakdown(self) -> Dict:
        """Get breakdown of metrics by language."""
        languages = {}
        for metric in self.metrics:
            if metric.language not in languages:
                languages[metric.language] = {
                    "count": 0,
                    "successes": 0
                }
            languages[metric.language]["count"] += 1
            if metric.success:
                languages[metric.language]["successes"] += 1
        
        # Calculate success rates
        for lang, stats in languages.items():
            stats["success_rate"] = stats["successes"] / stats["count"]
        
        return languages
    
    def _persist_metrics(self):
        """Persist metrics to disk."""
        if not self.persist_path:
            return
        
        try:
            with open(self.persist_path, 'w') as f:
                json.dump([asdict(m) for m in self.metrics], f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to persist metrics: {e}")
    
    def load_metrics(self, path: str):
        """Load metrics from disk.
        
        Args:
            path: Path to metrics file
        """
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                self.metrics = [GenerationMetrics(**m) for m in data]
        except Exception as e:
            print(f"Warning: Failed to load metrics: {e}")
    
    def clear_metrics(self):
        """Clear all collected metrics."""
        self.metrics = []
        self.session_start = datetime.now()
    
    def export_csv(self, path: str):
        """Export metrics to CSV file.
        
        Args:
            path: Path to CSV file
        """
        if not self.metrics:
            return
        
        try:
            import csv
            with open(path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=asdict(self.metrics[0]).keys())
                writer.writeheader()
                for metric in self.metrics:
                    writer.writerow(asdict(metric))
        except Exception as e:
            print(f"Warning: Failed to export CSV: {e}")


# Global metrics collector instance
_global_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create the global metrics collector instance.
    
    Returns:
        MetricsCollector instance
    """
    global _global_collector
    if _global_collector is None:
        _global_collector = MetricsCollector()
    return _global_collector


def reset_metrics_collector():
    """Reset the global metrics collector."""
    global _global_collector
    _global_collector = None

# Made with Bob
