"""
Comprehensive logging system for V2 Lead Generation Pipeline
Tracks every action, API call, data transformation, and decision
"""

import logging
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional
import traceback
import os
from pathlib import Path


class PipelineLogger:
    """
    Centralized logging system for the entire pipeline
    Features:
    - Structured JSON logging
    - Performance tracking
    - Error context preservation
    - API call monitoring
    - Data flow tracking
    """
    
    def __init__(self, log_dir: str = "logs", process_id: Optional[str] = None):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Generate unique process ID if not provided
        self.process_id = process_id or f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create different log files for different purposes
        self.setup_loggers()
        
        # Performance tracking
        self.timers = {}
        
        # API call tracking
        self.api_calls = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'rate_limited': 0
        }
    
    def setup_loggers(self):
        """Setup different loggers for different aspects"""
        # Main pipeline log
        self.pipeline_logger = self._create_logger(
            'pipeline',
            f"{self.process_id}_pipeline.log",
            logging.INFO
        )
        
        # API calls log
        self.api_logger = self._create_logger(
            'api',
            f"{self.process_id}_api_calls.log",
            logging.DEBUG
        )
        
        # Data flow log
        self.data_logger = self._create_logger(
            'data',
            f"{self.process_id}_data_flow.log",
            logging.DEBUG
        )
        
        # Error log
        self.error_logger = self._create_logger(
            'error',
            f"{self.process_id}_errors.log",
            logging.ERROR
        )
        
        # Quality control log
        self.qc_logger = self._create_logger(
            'qc',
            f"{self.process_id}_quality_control.log",
            logging.INFO
        )
    
    def _create_logger(self, name: str, filename: str, level: int) -> logging.Logger:
        """Create a logger with JSON formatting"""
        logger = logging.getLogger(f"{self.process_id}_{name}")
        logger.setLevel(level)
        
        # File handler
        handler = logging.FileHandler(self.log_dir / filename)
        handler.setLevel(level)
        
        # JSON formatter
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": %(message)s}'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        return logger
    
    # Pipeline Stage Logging
    def start_stage(self, stage: str, context: Dict[str, Any] = None):
        """Log the start of a pipeline stage"""
        self.timers[stage] = time.time()
        self.pipeline_logger.info(json.dumps({
            'event': 'stage_start',
            'stage': stage,
            'context': context or {}
        }))
    
    def end_stage(self, stage: str, status: str = 'success', 
                  results: Dict[str, Any] = None, error: str = None):
        """Log the end of a pipeline stage"""
        duration = time.time() - self.timers.get(stage, time.time())
        
        log_data = {
            'event': 'stage_end',
            'stage': stage,
            'status': status,
            'duration_seconds': round(duration, 2),
            'results': results or {}
        }
        
        if error:
            log_data['error'] = error
            self.error_logger.error(json.dumps(log_data))
        else:
            self.pipeline_logger.info(json.dumps(log_data))
    
    # API Call Logging
    def log_api_call(self, endpoint: str, params: Dict[str, Any], 
                     method: str = 'GET'):
        """Log API call initiation"""
        self.api_calls['total'] += 1
        
        # Don't log sensitive data
        safe_params = {k: v for k, v in params.items() 
                      if k not in ['api_key', 'token', 'password']}
        
        self.api_logger.debug(json.dumps({
            'event': 'api_call_start',
            'endpoint': endpoint,
            'method': method,
            'params': safe_params,
            'timestamp': datetime.now().isoformat()
        }))
        
        return time.time()  # Return start time for duration calculation
    
    def log_api_response(self, endpoint: str, start_time: float, 
                        status_code: int, response_data: Any = None,
                        error: str = None):
        """Log API response"""
        duration = time.time() - start_time
        
        log_data = {
            'event': 'api_call_end',
            'endpoint': endpoint,
            'status_code': status_code,
            'duration_seconds': round(duration, 3),
            'timestamp': datetime.now().isoformat()
        }
        
        if status_code == 200:
            self.api_calls['success'] += 1
            # Log sample of response for debugging
            if response_data:
                log_data['response_sample'] = str(response_data)[:500]
        elif status_code == 429:
            self.api_calls['rate_limited'] += 1
            log_data['error'] = 'Rate limited'
        else:
            self.api_calls['failed'] += 1
            log_data['error'] = error or f'HTTP {status_code}'
        
        self.api_logger.debug(json.dumps(log_data))
    
    # Data Flow Logging
    def log_data_transformation(self, stage: str, input_count: int, 
                               output_count: int, transformation: str,
                               sample_data: Any = None):
        """Log data transformations through the pipeline"""
        log_data = {
            'event': 'data_transformation',
            'stage': stage,
            'transformation': transformation,
            'input_count': input_count,
            'output_count': output_count,
            'reduction_rate': round((1 - output_count/input_count) * 100, 2) if input_count > 0 else 0
        }
        
        if sample_data:
            log_data['sample'] = str(sample_data)[:300]
        
        self.data_logger.debug(json.dumps(log_data))
    
    # Quality Control Logging
    def log_quality_check(self, check_type: str, passed: bool, 
                         details: Dict[str, Any], stage: str):
        """Log quality control checks"""
        self.qc_logger.info(json.dumps({
            'event': 'quality_check',
            'stage': stage,
            'check_type': check_type,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }))
    
    # Error Logging
    def log_error(self, error: Exception, context: Dict[str, Any], 
                  stage: str, critical: bool = False):
        """Log errors with full context"""
        error_data = {
            'event': 'error',
            'stage': stage,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context,
            'critical': critical,
            'timestamp': datetime.now().isoformat()
        }
        
        self.error_logger.error(json.dumps(error_data))
        
        if critical:
            # Also log to pipeline logger for visibility
            self.pipeline_logger.error(json.dumps({
                'event': 'critical_error',
                'stage': stage,
                'error': str(error)
            }))
    
    # Summary and Reporting
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of the pipeline run"""
        return {
            'process_id': self.process_id,
            'api_calls': self.api_calls,
            'stages_completed': len(self.timers),
            'total_duration': sum(time.time() - start for start in self.timers.values()),
            'errors': self._count_errors(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _count_errors(self) -> int:
        """Count errors from error log"""
        error_file = self.log_dir / f"{self.process_id}_errors.log"
        if error_file.exists():
            with open(error_file, 'r') as f:
                return len(f.readlines())
        return 0
    
    def log_summary(self):
        """Log final summary"""
        summary = self.get_summary()
        self.pipeline_logger.info(json.dumps({
            'event': 'pipeline_summary',
            **summary
        }))
        
        # Also print to console
        print("\n" + "="*50)
        print("PIPELINE EXECUTION SUMMARY")
        print("="*50)
        print(f"Process ID: {summary['process_id']}")
        print(f"Total API Calls: {summary['api_calls']['total']}")
        print(f"Successful: {summary['api_calls']['success']}")
        print(f"Failed: {summary['api_calls']['failed']}")
        print(f"Rate Limited: {summary['api_calls']['rate_limited']}")
        print(f"Total Duration: {summary['total_duration']:.2f}s")
        print(f"Errors: {summary['errors']}")
        print("="*50)


# Convenience functions for quick logging
def create_logger(process_id: Optional[str] = None) -> PipelineLogger:
    """Create a new logger instance"""
    return PipelineLogger(process_id=process_id)


# Example usage
if __name__ == "__main__":
    # Test the logger
    logger = create_logger()
    
    # Stage logging
    logger.start_stage("influencer_fetch", {"influencer_url": "linkedin.com/in/example"})
    
    # API logging
    start = logger.log_api_call("/person_deep", {"link": "example"})
    logger.log_api_response("/person_deep", start, 200, {"name": "Example"})
    
    # Data transformation
    logger.log_data_transformation("post_filtering", 100, 25, "relevance_filter")
    
    # Quality check
    logger.log_quality_check("influencer_validation", True, 
                           {"followers": 10000, "relevant": True}, "influencer_selection")
    
    # End stage
    logger.end_stage("influencer_fetch", "success", {"posts_found": 50})
    
    # Summary
    logger.log_summary()