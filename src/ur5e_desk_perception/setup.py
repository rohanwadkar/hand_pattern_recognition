from setuptools import setup
import os
from glob import glob

package_name = 'ur5e_desk_perception'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ROS Developer',
    maintainer_email='user@todo.todo',
    description='RGB-D vision node for 3D object detection and pose estimation',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'object_detection_node = ur5e_desk_perception.object_detection_node:main',
        ],
    },
)
