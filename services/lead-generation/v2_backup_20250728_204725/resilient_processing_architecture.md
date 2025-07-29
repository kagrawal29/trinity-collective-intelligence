# 🛡️ Resilient Processing Architecture - Auto-Recovery System

## 🎯 Problem Statement
Current issue: Batch processing timed out after 122/192 leads, leaving 70 unprocessed with no automatic recovery.

## 🚀 Comprehensive Solution Architecture

### 1. **Checkpoint-Based Processing**
```python
class ResilientBatchProcessor:
    def __init__(self):
        self.checkpoint_file = "processing_checkpoint.json"
        self.max_retries = 3
        self.batch_timeout = 30  # seconds per batch
        
    def save_checkpoint(self, batch_num: int, processed_leads: List[Dict]):
        """Save progress after each batch"""
        checkpoint = {
            "last_completed_batch": batch_num,
            "total_processed": len(processed_leads),
            "timestamp": datetime.now().isoformat(),
            "lead_ids_processed": [lead['linkedin_url'] for lead in processed_leads]
        }
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f)
    
    def load_checkpoint(self) -> Dict:
        """Resume from last checkpoint"""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {"last_completed_batch": 0, "total_processed": 0}
```

### 2. **Automatic Resume Capability**
```python
def process_leads_with_resume(leads: List[Dict]):
    """Process leads with automatic resume on failure"""
    checkpoint = load_checkpoint()
    start_batch = checkpoint['last_completed_batch'] + 1
    
    if start_batch > 1:
        print(f"🔄 RESUMING from batch {start_batch} (already processed {checkpoint['total_processed']} leads)")
        # Skip already processed leads
        leads = leads[checkpoint['total_processed']:]
    
    # Continue processing from checkpoint
    process_remaining_batches(leads, start_batch)
```

### 3. **Timeout Detection & Recovery**
```python
import signal
import functools

def timeout_handler(signum, frame):
    raise TimeoutError("Batch processing timeout")

def with_timeout(seconds):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)  # Cancel alarm
            return result
        return wrapper
    return decorator

@with_timeout(300)  # 5-minute timeout
def process_batch_safely(batch: List[Dict]) -> List[Dict]:
    """Process batch with timeout protection"""
    return process_batch(batch)
```

### 4. **Progressive Batch Sizing**
```python
class AdaptiveBatchProcessor:
    def __init__(self):
        self.initial_batch_size = 10
        self.min_batch_size = 2
        self.max_batch_size = 20
        self.current_batch_size = self.initial_batch_size
        
    def adjust_batch_size(self, processing_time: float):
        """Dynamically adjust batch size based on performance"""
        if processing_time > 20:  # Too slow
            self.current_batch_size = max(self.min_batch_size, 
                                         self.current_batch_size - 2)
        elif processing_time < 5:  # Very fast
            self.current_batch_size = min(self.max_batch_size, 
                                         self.current_batch_size + 2)
```

### 5. **Database Transaction Management**
```python
def process_with_savepoints(batch: List[Dict]):
    """Use database savepoints for partial commit"""
    conn = sqlite3.connect('trinity_logging.db')
    
    try:
        conn.execute('BEGIN')
        
        for i, lead in enumerate(batch):
            # Create savepoint every 5 leads
            if i % 5 == 0:
                conn.execute(f'SAVEPOINT batch_{i}')
            
            process_lead(lead, conn)
            
            # Commit savepoint
            if (i + 1) % 5 == 0:
                conn.execute(f'RELEASE SAVEPOINT batch_{i-4}')
        
        conn.commit()
    except Exception as e:
        # Rollback to last savepoint
        conn.execute('ROLLBACK TO SAVEPOINT batch_' + str((i // 5) * 5))
        conn.commit()  # Commit partial progress
        raise
```

### 6. **Health Monitoring & Alerts**
```python
class ProcessingMonitor:
    def __init__(self):
        self.metrics = {
            'total_leads': 0,
            'processed_leads': 0,
            'failed_batches': 0,
            'average_batch_time': 0,
            'timeout_count': 0
        }
    
    def check_health(self) -> Dict:
        """Real-time health check"""
        completion_rate = self.metrics['processed_leads'] / self.metrics['total_leads']
        
        if completion_rate < 0.5 and self.metrics['timeout_count'] > 2:
            return {
                'status': 'CRITICAL',
                'message': 'Multiple timeouts detected, manual intervention needed',
                'recommendation': 'Reduce batch size or increase timeout'
            }
        elif completion_rate < 0.8:
            return {
                'status': 'WARNING',
                'message': f"Only {completion_rate*100:.1f}% complete",
                'recommendation': 'Monitor closely, may need intervention'
            }
        return {'status': 'HEALTHY'}
```

### 7. **Configuration Management**
```yaml
# config/processing_config.yaml
processing:
  batch_size:
    initial: 10
    min: 2
    max: 20
    adaptive: true
  
  timeouts:
    per_batch: 30
    total_run: 600
    api_call: 10
  
  retry:
    max_attempts: 3
    backoff_factor: 2
    
  checkpointing:
    enabled: true
    frequency: "every_batch"
    
  recovery:
    auto_resume: true
    partial_commit: true
```

### 8. **CLAUDE.md Integration**
```markdown
## 🛡️ Resilient Processing Guidelines

### Auto-Recovery Protocol
1. **Always check for checkpoints** before starting
2. **Save progress after each batch** 
3. **Use smaller batches (5)** if timeouts occur
4. **Monitor health metrics** during processing

### Timeout Handling
- Default: 5 minutes total, 30 seconds per batch
- On timeout: Auto-save checkpoint and resume
- After 3 timeouts: Alert for manual intervention

### Command Examples
```bash
# Normal run (auto-resumes if needed)
python3 analyze_batch_llm_sqlite.py

# Force fresh start
python3 analyze_batch_llm_sqlite.py --fresh

# Custom timeout
python3 analyze_batch_llm_sqlite.py --timeout 600

# Resume from specific batch
python3 analyze_batch_llm_sqlite.py --resume-batch 14
```
```

## 🎯 Implementation Priority

### Phase 1: Immediate (Next PR)
1. Add checkpoint saving to `analyze_batch_llm_sqlite.py`
2. Implement auto-resume on script start
3. Add `--timeout` parameter

### Phase 2: This Week
1. Adaptive batch sizing
2. Database savepoints
3. Health monitoring dashboard

### Phase 3: Long-term
1. Distributed processing support
2. Real-time progress UI
3. Predictive timeout prevention

## 🚀 Benefits

1. **Zero Data Loss** - Every processed lead saved
2. **Automatic Recovery** - No manual intervention needed
3. **Predictable Completion** - System adapts to conditions
4. **Full Visibility** - Know exactly what's happening
5. **Production Ready** - Handles real-world conditions

## 📊 Success Metrics

- **Completion Rate**: 100% (vs current 64%)
- **Manual Interventions**: 0 (vs current requirement)
- **Recovery Time**: < 30 seconds (automatic)
- **Data Integrity**: 100% attribution preserved

---

*This architecture ensures the Trinity system is truly production-ready, handling all edge cases automatically!*