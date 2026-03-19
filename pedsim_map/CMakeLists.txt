cmake_minimum_required(VERSION 3.0.2)
project(pedsim_map)

add_definitions(-Wall -Wunused -std=c++11 -pipe -Wextra)

find_package(catkin REQUIRED COMPONENTS
  nav_msgs
  roscpp
  visualization_msgs
  tf
  spencer_tracking_msgs
)

###################################
## catkin specific configuration ##
###################################
catkin_package(
 INCLUDE_DIRS include
 CATKIN_DEPENDS nav_msgs roscpp visualization_msgs tf
)

###########
## Build ##
###########

include_directories(include ${catkin_INCLUDE_DIRS})


set(EXECUTABLE_NAME ${PROJECT_NAME}_node)


add_executable(${EXECUTABLE_NAME}
  src/real_map_node.cpp
  src/real_map.cpp
)

add_dependencies(${EXECUTABLE_NAME} ${catkin_EXPORTED_TARGETS})

target_link_libraries(${EXECUTABLE_NAME}
  ${catkin_LIBRARIES}
)

#############
## Install ##
#############
install(TARGETS ${EXECUTABLE_NAME}
  RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY include/${PROJECT_NAME}/
  DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}
  FILES_MATCHING PATTERN "*.h"
)