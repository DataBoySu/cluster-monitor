# GPU Bounce Simulation - Usage Guide

## Running the Simulation

### Basic Command
```powershell
python health_monitor.py benchmark --type particle --duration 60 --visualize
```

### Parameters
- `--duration 60`: Run for 60 seconds
- `--visualize`: Show real-time visualization window
- `--num-particles 100000`: Set particle capacity (default: 100k)

## Interactive Controls

### Sliders (Bottom of Window)
1. **Big Ball Gravity** (0-10000): Controls gravitational force strength
   - Higher = larger white boundary circles
   - Affects how strongly big balls attract each other
   
2. **Small Ball Speed** (50-600): Constant velocity of small balls
   - Small balls maintain this speed (normalized each frame)
   
3. **Total Small Balls** (1-2000): Target number of small balls
   - Particles spawn from top center until this limit
   - **Exponential growth**: Each collision creates 2 more balls!

## Simulation Mechanics

### Physics Model
- **4 Big Balls** (red/orange, mass 1000):
  - Start stationary at center
  - Attract each other via N×N gravitational matrix
  - **Proper momentum conservation**: Heavy balls barely move from small ball impacts
  
- **Small Balls** (white→red, mass 1):
  - Spawn from top center (500, 50) with constant velocity
  - **Color changes**: Turn red when hitting big balls, fade back to white
  - **Glow intensity**: GPU-computed based on speed (faster = brighter)
  - **Particle splitting**: Each collision creates 2 new balls!

### Collision Dynamics
- **Elastic collisions** with proper momentum: `impulse = 2×m_other / (m1+m2)`
- Small ball hitting big ball: `Δv_big ≈ 0.002×Δv_small` (mass ratio 1:1000)
- **All collisions trigger splitting**: Small balls spawn 2 children on ANY collision
- Children spawn near parent with random velocity directions

### GPU Acceleration Features
1. **Vectorized collision detection**: N×N distance matrices computed on GPU
2. **Parallel force accumulation**: All collisions processed simultaneously
3. **GPU-computed effects**:
   - Color state (collision tracking)
   - Glow intensity (speed-based)
   - Particle splitting flags
4. **Matrix-based gravity**: 4×4 pairwise force computation for big balls

## Visualizations

### White Boundary Circles
- Show **actual gravitational influence radius**
- Calculated as: `r = √(G×M / force_threshold)`
- Scale with gravity slider setting
- Represent where gravitational force becomes perceptible

### Color Coding
- **Big balls**: Red/orange, constant
- **Small balls**: 
  - White = normal state
  - Red = just collided with big ball
  - Brightness = speed (GPU glow shader)

## GPU Utilization Issues

### Why <5% GPU at 100k particles?

**Bottlenecks identified:**
1. **CPU-GPU transfer**: Pygame rendering pulls data to CPU every frame
2. **Sampling**: `get_particle_sample()` transfers 2000 particles to CPU
3. **Serial spawning**: Particle splitting uses Python loops (not vectorized)
4. **Pygame overhead**: Screen rendering is single-threaded CPU

**GPU is waiting on CPU I/O**, not doing more work!

### Solutions to Increase GPU Load

#### Option 1: Reduce Sampling Frequency
Edit `runner.py` line 157:
```python
if frame_count % 5 == 0:  # Only sample every 5 frames
    positions, masses, colors, glows = self.stress_worker.get_particle_sample()
```

#### Option 2: Disable Visualization
```powershell
python health_monitor.py benchmark --type particle --duration 60
# No --visualize flag = pure GPU computation
```
**Expected**: 80-100% GPU utilization

#### Option 3: Increase Particle Count
```powershell
python health_monitor.py benchmark --type particle --duration 60 --visualize --num-particles 500000
```
Set slider to 2000 balls → exponential growth → millions of particles

#### Option 4: Vectorize Spawning (Code Change)
Replace Python loops in workloads.py with batch GPU operations:
```python
# Instead of: for idx, parent_idx in enumerate(...)
# Use: Batch spawn all children with cp.random arrays
```

#### Option 5: Add More GPU Workload
- Increase big ball count (4 → 16): More N×N gravity computations
- Add inter-particle forces for small balls
- Implement GPU-based spatial hashing for collision optimization
- Add particle aging/decay with GPU timers

## Performance Expectations

| Configuration | Expected GPU % | Bottleneck |
|--------------|----------------|------------|
| 100 balls, viz | 5-10% | Pygame rendering |
| 1000 balls, viz | 15-25% | CPU-GPU transfer |
| 10k balls, viz | 30-50% | Sampling overhead |
| 100k balls, no viz | 80-100% | Pure GPU compute |
| 100k balls, viz | <10% | **CPU transfer dominates** |

## Recommended Testing

1. **Baseline GPU stress** (no visualization):
   ```powershell
   python health_monitor.py benchmark --type particle --duration 60 --num-particles 500000
   ```
   Check GPU% in task manager. Should be 80-100%.

2. **Watch exponential growth**:
   - Start with slider at 50 balls
   - Increase gravity to 5000
   - Watch particle count explode from splitting
   - Monitor GPU% as count rises

3. **Gravity field visualization**:
   - Set gravity slider to various values (100, 1000, 5000)
   - White circles resize dynamically
   - Shows actual physics influence zone

## Technical Notes

- Simulation runs at 60 FPS (capped by `clock.tick(60)`)
- Physics timestep: 0.016 seconds (locked)
- Collision detection: O(N²) but GPU-parallelized
- Memory: ~100MB for 100k particles on GPU
- Particle splitting causes **exponential growth**: N → 2N → 4N → 8N...

## Monitoring GPU

Use `nvidia-smi` to check real utilization:
```powershell
# Watch GPU utilization in real-time
nvidia-smi --query-gpu=utilization.gpu --format=csv -l 1
```

Or open Task Manager → Performance → GPU → CUDA/Compute
