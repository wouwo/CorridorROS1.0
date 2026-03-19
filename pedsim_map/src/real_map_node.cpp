#include <pedsim_map/real_map.h>

int main(int argc, char** argv) {
  ros::init(argc, argv, "real_map_server");
  ros::NodeHandle nh;
  ros::Rate loop_rate(25);
  
  RealObstacleProcess realMap(nh);
  realMap.YamlReader();
  
  while (ros::ok()){
    ros::spinOnce();
    loop_rate.sleep();
  }
}