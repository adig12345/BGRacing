"""Publisher node: reads the track CSV and republishes it as two nav_msgs/Path.

Topics: /track/left and /track/right. The track is republished every
`publish_period_s` seconds so a late-starting subscriber still gets it
(we use default QoS, which does not keep old messages).
"""

import numpy as np
import rclpy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path as PathMsg
from rclpy.node import Node
from rclpy.parameter import Parameter

from src.geometry import load_track


class TrackPublisher(Node):
    """Loads the track once and publishes both boundaries on a timer."""

    def __init__(self) -> None:
        super().__init__("track_publisher")  # must match params.yaml key

        # No defaults in code: every value must come from config/params.yaml.
        # An unset parameter raises ParameterUninitializedException on read.
        self.declare_parameter("csv_path", Parameter.Type.STRING)
        self.declare_parameter("publish_period_s", Parameter.Type.DOUBLE)
        self.declare_parameter("frame_id", Parameter.Type.STRING)
        csv_path = self.get_parameter("csv_path").value
        period = self.get_parameter("publish_period_s").value
        self._frame_id = self.get_parameter("frame_id").value
        self.get_logger().info(
            f"Config: csv_path={csv_path}, publish_period_s={period}, "
            f"frame_id={self._frame_id}"
        )

        self._track = load_track(csv_path)
        self.get_logger().info(
            f"Loaded track: left={len(self._track.left)} points, "
            f"right={len(self._track.right)} points"
        )

        self._left_pub = self.create_publisher(PathMsg, "track/left", 10)
        self._right_pub = self.create_publisher(PathMsg, "track/right", 10)
        self.create_timer(period, self._on_timer)

    def _to_path(self, points: np.ndarray) -> PathMsg:
        """Convert an (N, 2) array of [x, y] rows into a nav_msgs/Path."""
        path = PathMsg()
        path.header.frame_id = self._frame_id
        path.header.stamp = self.get_clock().now().to_msg()
        for x, y in points:
            pose = PoseStamped()
            pose.pose.position.x = float(x)
            pose.pose.position.y = float(y)
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)
        return path

    def _on_timer(self) -> None:
        """Publish the whole track (both sides) once."""
        self._left_pub.publish(self._to_path(self._track.left))
        self._right_pub.publish(self._to_path(self._track.right))
        self.get_logger().info(
            f"Published track: left={len(self._track.left)}, "
            f"right={len(self._track.right)} points"
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TrackPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
