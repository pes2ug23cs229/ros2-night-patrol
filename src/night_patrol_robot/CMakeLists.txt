cmake_minimum_required(VERSION 3.8)
project(night_patrol_robot)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

# Install Python package
ament_python_install_package(${PROJECT_NAME})

# Install scripts as executables
install(PROGRAMS
  night_patrol_robot/patrol_node.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME patrol_node
)

# Install launch, urdf, config, maps
install(DIRECTORY
  launch urdf config maps
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
