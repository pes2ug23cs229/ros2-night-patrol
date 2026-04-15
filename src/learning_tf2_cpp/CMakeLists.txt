cmake_minimum_required(VERSION 3.8)
project(learning_tf2_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(turtlesim REQUIRED)

# ---------------- BROADCASTER ----------------
add_executable(turtle_tf2_broadcaster src/turtle_tf2_broadcaster.cpp)

ament_target_dependencies(
  turtle_tf2_broadcaster
  geometry_msgs
  rclcpp
  tf2
  tf2_ros
  turtlesim
)

install(TARGETS
  turtle_tf2_broadcaster
  DESTINATION lib/${PROJECT_NAME}
)

# ---------------- STATIC BROADCASTER ----------------
add_executable(static_turtle_tf2_broadcaster src/static_turtle_tf2_broadcaster.cpp)

ament_target_dependencies(
  static_turtle_tf2_broadcaster
  geometry_msgs
  rclcpp
  tf2
  tf2_ros
)

install(TARGETS
  static_turtle_tf2_broadcaster
  DESTINATION lib/${PROJECT_NAME}
)

# ---------------- LISTENER ----------------
add_executable(turtle_tf2_listener src/turtle_tf2_listener.cpp)

ament_target_dependencies(
  turtle_tf2_listener
  geometry_msgs
  rclcpp
  tf2
  tf2_ros
  turtlesim
)

install(TARGETS
  turtle_tf2_listener
  DESTINATION lib/${PROJECT_NAME}
)

# ---------------- FIXED FRAME ----------------
add_executable(fixed_frame_tf2_broadcaster src/fixed_frame_tf2_broadcaster.cpp)

ament_target_dependencies(
  fixed_frame_tf2_broadcaster
  geometry_msgs
  rclcpp
  tf2_ros
)

install(TARGETS
  fixed_frame_tf2_broadcaster
  DESTINATION lib/${PROJECT_NAME}
)

# ---------------- INSTALL LAUNCH FILES ----------------
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

# ---------------- FINAL ----------------
ament_package()
