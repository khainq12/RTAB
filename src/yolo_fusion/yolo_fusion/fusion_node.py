#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from yolo_msgs.msg import DetectionArray
from sensor_msgs.msg import PointCloud2
from visualization_msgs.msg import Marker

import sensor_msgs_py.point_cloud2 as pc2
import random


class FusionNode(Node):
    def __init__(self):
        super().__init__('fusion_node')

        # Subscribe YOLO detections
        self.sub_det = self.create_subscription(
            DetectionArray,
            '/yolo/detections',
            self.det_callback,
            10)

        # Subscribe point cloud
        self.sub_cloud = self.create_subscription(
            PointCloud2,
            '/cloud_obstacles',
            self.cloud_callback,
            10)

        # Publisher markers
        self.pub_marker = self.create_publisher(
            Marker,
            '/object_markers',
            10)

        self.latest_cloud = None

    def cloud_callback(self, msg):
        self.latest_cloud = msg

    def det_callback(self, msg):
        if self.latest_cloud is None:
            return

        # Read point cloud
        points = list(pc2.read_points(
            self.latest_cloud,
            field_names=("x", "y", "z"),
            skip_nans=True))

        if len(points) == 0:
            return

        for det in msg.detections:
            # ⚠️ DEMO: vẫn random (chưa fusion thật)
            p = random.choice(points)

            marker = Marker()
            marker.header.frame_id = self.latest_cloud.header.frame_id
            marker.header.stamp = self.get_clock().now().to_msg()

            marker.ns = "yolo_objects"
            marker.id = random.randint(0, 100000)

            marker.type = Marker.SPHERE
            marker.action = Marker.ADD

            marker.pose.position.x = float(p[0])
            marker.pose.position.y = float(p[1])
            marker.pose.position.z = float(p[2])

            marker.pose.orientation.w = 1.0

            marker.scale.x = 0.2
            marker.scale.y = 0.2
            marker.scale.z = 0.2

            marker.color.r = 1.0
            marker.color.g = 0.0
            marker.color.b = 0.0
            marker.color.a = 1.0

            self.pub_marker.publish(marker)


def main(args=None):
    rclpy.init(args=args)
    node = FusionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()