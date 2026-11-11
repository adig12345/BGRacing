"""Publisher node: reads the track CSV and publishes it as two nav_msgs/Path.

Topics: /track/left and /track/right, published once. The QoS is transient
local (see ros_qos.py), so a subscriber that starts later still receives the
last message of each topic.
"""

import numpy as np
import rclpy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path as PathMsg
from rclpy.node import Node
from rclpy.parameter import Parameter

from src.geometry import load_track
from src.ros_qos import TRACK_QOS


class TrackPublisher(Node):
    """Loads the track and publishes both boundaries once."""

    def __init__(self) -> None:
        super().__init__("track_publisher")  # must match params.yaml key

        # No defaults in code: every value must come from config/params.yaml.
        # An unset parameter raises ParameterUninitializedException on read.
        self.declare_parameter("csv_path", Parameter.Type.STRING)
        self.declare_parameter("frame_id", Parameter.Type.STRING)
        csv_path = self.get_parameter("csv_path").value
        self._frame_id = self.get_parameter("frame_id").value
        self.get_logger().info(
            f"Config: csv_path={csv_path}, frame_id={self._frame_id}"
        )

        self._track = load_track(csv_path)
        self.get_logger().info(
            f"Loaded track: left={len(self._track.left)} points, "
            f"right={len(self._track.right)} points"
        )

        self._left_pub = self.create_publisher(PathMsg, "track/left", TRACK_QOS)
        self._right_pub = self.create_publisher(PathMsg, "track/right", TRACK_QOS)
        self._publish_track()

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

    def _publish_track(self) -> None:
        """Publish the whole track (both sides) once; ROS keeps it for late joiners."""
        self._left_pub.publish(self._to_path(self._track.left))
        self._right_pub.publish(self._to_path(self._track.right))
        self.get_logger().info(
            f"Published track once: left={len(self._track.left)}, "
            f"right={len(self._track.right)} points (transient local)"
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
