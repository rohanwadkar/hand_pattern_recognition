#include <memory>
#include <string>
#include <vector>

#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose.hpp>
#include <moveit/move_group_interface/move_group_interface.h>
#include <moveit/planning_scene_interface/planning_scene_interface.h>

#include "ur5e_desk_interfaces/srv/detect_objects.hpp"

class ArmControlNode : public rclcpp::Node
{
public:
  ArmControlNode() : Node("arm_control_node")
  {
    this->declare_parameter("home_pose", std::vector<double>{0.0, -1.57, 1.57, -1.57, -1.57, 0.0});
    RCLCPP_INFO(this->get_logger(), "Arm Control Node initialized.");
  }

  void init_moveit()
  {
    move_group_arm_ = std::make_shared<moveit::planning_interface::MoveGroupInterface>(shared_from_this(), "ur_manipulator");
    move_group_gripper_ = std::make_shared<moveit::planning_interface::MoveGroupInterface>(shared_from_this(), "gripper");

    move_group_arm_->setMaxVelocityScalingFactor(0.5);
    move_group_arm_->setMaxAccelerationScalingFactor(0.5);
  }

  bool go_to_home()
  {
    move_group_arm_->setNamedTarget("home");
    moveit::planning_interface::MoveGroupInterface::Plan plan;
    bool success = (move_group_arm_->plan(plan) == moveit::core::MoveItErrorCode::SUCCESS);
    if (success) {
      move_group_arm_->execute(plan);
    }
    return success;
  }

  bool control_gripper(double position)
  {
    move_group_gripper_->setJointValueTarget("left_finger_joint", position);
    moveit::planning_interface::MoveGroupInterface::Plan plan;
    bool success = (move_group_gripper_->plan(plan) == moveit::core::MoveItErrorCode::SUCCESS);
    if (success) {
      move_group_gripper_->execute(plan);
    }
    return success;
  }

  bool pick(const geometry_msgs::msg::Pose & target_pose)
  {
    RCLCPP_INFO(this->get_logger(), "Executing Pick Sequence...");
    control_gripper(0.0); // Open

    // Pre-grasp pose (15cm above)
    geometry_msgs::msg::Pose pre_grasp = target_pose;
    pre_grasp.position.z += 0.15;
    move_group_arm_->setPoseTarget(pre_grasp);
    move_group_arm_->move();

    // Approach pose (2cm above)
    geometry_msgs::msg::Pose grasp_pose = target_pose;
    grasp_pose.position.z += 0.02;
    move_group_arm_->setPoseTarget(grasp_pose);
    move_group_arm_->move();

    // Grasp
    control_gripper(0.035);

    // Lift
    move_group_arm_->setPoseTarget(pre_grasp);
    move_group_arm_->move();

    return true;
  }

  bool place(const geometry_msgs::msg::Pose & target_pose)
  {
    RCLCPP_INFO(this->get_logger(), "Executing Place Sequence...");
    // Pre-place pose (15cm above)
    geometry_msgs::msg::Pose pre_place = target_pose;
    pre_place.position.z += 0.15;
    move_group_arm_->setPoseTarget(pre_place);
    move_group_arm_->move();

    // Lower pose
    geometry_msgs::msg::Pose place_pose = target_pose;
    place_pose.position.z += 0.05;
    move_group_arm_->setPoseTarget(place_pose);
    move_group_arm_->move();

    // Release
    control_gripper(0.0);

    // Retract
    move_group_arm_->setPoseTarget(pre_place);
    move_group_arm_->move();

    return true;
  }

private:
  std::shared_ptr<moveit::planning_interface::MoveGroupInterface> move_group_arm_;
  std::shared_ptr<moveit::planning_interface::MoveGroupInterface> move_group_gripper_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<ArmControlNode>();
  node->init_moveit();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
