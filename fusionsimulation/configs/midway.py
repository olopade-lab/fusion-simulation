from parsl.providers import SlurmProvider

from parsl.config import Config
from parsl.executors import HighThroughputExecutor
from parsl.utils import get_all_checkpoints

cores_per_slot = 8
worker_init = """

module load singularity
conda activate parsl
"""


config = Config(
    executors=[
        HighThroughputExecutor(
            'htex',
            cores_per_worker=5,
            heartbeat_threshold=480,
            heartbeat_period=10,
            worker_debug=True,
            provider=SlurmProvider(
                'broadwl',
                walltime='24:00:00',
                worker_init=worker_init,
                init_blocks=19,
                max_blocks=19
            ),
        )
    ],
    checkpoint_mode='task_exit',
    checkpoint_files=get_all_checkpoints()
)
