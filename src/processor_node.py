"""Processor node: receives both track boundaries and processes them once.

Subscribes to /track/left and /track/right (nav_msgs/Path). The publisher
resends the track periodically, so we process the first complete pair and
ignore every later message.
"""
import time
from typing import Optional

import numpy as np
import rclpy
from nav_msgs.msg import Path as PathMsg
from rclpy.node import Node
from rclpy.parameter import Parameter

from src.geometry import Corridor, Track, apply_offsets, build_corridor, path_length
from src.optimizers import get_optimizer


def path_to_array(path: PathMsg) -> np.ndarray:
    """Convert a nav_msgs/Path into an (N, 2) float array of [x, y] rows."""
    return np.array(
        [[ p.pose.position.x, p.pose.position.y] for p in path.poses],
        dtype = float,
    ).reshape(-1,2)


class TrackProcessor(Node):
    """Collects the two boundaries, then runs the pipeline once."""

    def __init__(self) -> None:
        super().__init__("track_processor")  # node name

        self._left: Optional[np.ndarray] = None
        self._right: Optional[np.ndarray] = None
        self._corridor: Optional[Corridor] = None
        self._racing_line: Optional[np.ndarray] = None
        self._done = False

        # No defaults in code: every value must come from config/params.yaml.
        # An unset parameter raises ParameterUninitializedException on read.
        self.declare_parameter("optimizer", Parameter.Type.STRING)
        self.declare_parameter("alpha_limit", Parameter.Type.DOUBLE)
        self.declare_parameter("max_iterations", Parameter.Type.INTEGER)
        self.declare_parameter("tolerance", Parameter.Type.DOUBLE)
        self._optimizer_name = self.get_parameter("optimizer").value
        self._optimizer_params = {
            "alpha_limit": self.get_parameter("alpha_limit").value,
            "max_iterations": self.get_parameter("max_iterations").value,
            "tolerance": self.get_parameter("tolerance").value,
        }
        self.get_logger().info(
            f"Config: optimizer={self._optimizer_name}, "
            f"params={self._optimizer_params}"
        )
        # Look the optimizer up now, so a typo fails at startup, not mid-run.
        self._optimizer = get_optimizer(self._optimizer_name)

        self.create_subscription(PathMsg, "track/left", self._on_left, 10)
        self.create_subscription(PathMsg, "track/right", self._on_right, 10)
        self.get_logger().info("Processor started, waiting for /track/left and /track/right")

    def _on_left(self, msg: PathMsg) -> None:
        """Store the left boundary, then check whether we can process."""
        if self._done:
            return
        self._left = path_to_array(msg)
        self._try_process()

    def _on_right(self, msg: PathMsg) -> None:
        """Store the right boundary, then check whether we can process."""
        if self._done:
            return
        self._right = path_to_array(msg)
        self._try_process()

    def _try_process(self) -> None:
        """Run the pipeline once, as soon as both boundaries have arrived."""
        if self._left is None or self._right is None:
            return  # still waiting for the other side
        self._done = True
        track = Track(left=self._left, right=self._right)
        self.get_logger().info(
            f"Received track: left={len(track.left)} points, "
            f"right={len(track.right)} points"
        )

        # Stage 1: centerline and sideways vectors.
        start = time.perf_counter()
        self._corridor = build_corridor(track)
        center_length = path_length(self._corridor.center)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        self.get_logger().info(
            f"Centerline: {len(self._corridor.center)} points, "
            f"length={center_length:.1f} m (assumed meters), "
            f"took {elapsed_ms:.2f} ms"
        )

        # Stage 2: racing line from the chosen optimizer.
        start = time.perf_counter()
        alpha = self._optimizer(self._corridor, self._optimizer_params)
        self._racing_line = apply_offsets(self._corridor, alpha)
        line_length = path_length(self._racing_line)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        saving = center_length - line_length
        self.get_logger().info(
            f"Racing line '{self._optimizer_name}': length={line_length:.1f} m, "
            f"{saving:.1f} m shorter than the centerline, "
            f"alpha in [{alpha.min():.2f}, {alpha.max():.2f}], "
            f"took {elapsed_ms:.1f} ms"
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TrackProcessor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
