"""Toy subscriber: logs every String received on /chatter.

Only used in step 2 to prove two containers can talk. Replaced in step 4.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Listener(Node):
    """Subscribes to /chatter and logs each message."""

    def __init__(self) -> None:
        super().__init__("listener")  # node name
        self._subscription = self.create_subscription(
            String, "chatter", self._on_message, 10
        )
        self.get_logger().info("Listener started, waiting for /chatter")

    def _on_message(self, msg: String) -> None:
        """Called by the executor each time a message arrives."""
        self.get_logger().info(f"Received: {msg.data}")


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Listener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
