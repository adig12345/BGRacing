"""Processor node: receives both track boundaries and processes them once.

Subscribes to /track/left and /track/right (nav_msgs/Path). The publisher
resends the track periodically, so we process the first complete pair and
ignore every later message.
"""
from typing import Optional

import numpy as np
import rclpy
from nav_msgs.msg import Path as PathMsg
from rclpy.node import Node

from src.geometry import Track


def path_to_array(path: PathMsg) -> np.ndarray:
    """Convert a nav_msgs/Path into an (N, 2) float array of [x, y] rows."""
    # TODO(human): build and return the array from path.poses.
    #   Each element p of path.poses is a PoseStamped, so the x value is
    #   p.pose.position.x. A list comprehension plus np.array(..., dtype=float)
    #   is enough. Add .reshape(-1, 2) so an empty path gives shape (0, 2).
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
        self._done = False

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
        # Step 4 will compute the centerline here.


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
