"""QoS profile shared by the publisher and the processor (needs rclpy).

Keeping it in one place guarantees that both sides use compatible settings:
a transient-local subscriber never connects to a volatile publisher, and ROS
does not raise an error when that happens.
"""

from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy

# TRANSIENT_LOCAL: the publisher keeps its last message(s) and hands them to
# subscribers that connect later, so the track needs to be published only once.
# KEEP_LAST with depth 1: only the newest message per topic is kept.
# RELIABLE: required, because the track must arrive complete.
TRACK_QOS = QoSProfile(
    history=HistoryPolicy.KEEP_LAST,
    depth=1,
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.TRANSIENT_LOCAL,
)
