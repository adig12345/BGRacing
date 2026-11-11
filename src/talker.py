"""Toy publisher: sends a counter string on /chatter.

Only used in step 2 to prove two containers can talk. Replaced in step 3.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Talker(Node):
    """Publishes 'hello N' on /chatter every `publish_period_s` seconds."""

    def __init__(self) -> None:
        super().__init__("talker")  # node name: must match params file key

        self.declare_parameter("publish_period_s", 1.0)
        period = self.get_parameter("publish_period_s").value
        self.get_logger().info(f"Config: publish_period_s={period}")

        self._publisher = self.create_publisher(String, "chatter", 10)
        self._count = 0
        self.create_timer(period, self._on_timer)

    def _on_timer(self) -> None:
        """Called by the executor once per period."""
        msg = String()
        msg.data = f'hello {self._count}'
        self._publisher.publish(msg)
        self.get_logger().info(f"Published: {msg.data}")
        self._count += 1


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Talker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
